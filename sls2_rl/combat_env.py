from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import numpy as np

from .data import CARDS, ENCOUNTER_POOLS, ENEMIES, IRONCLAD_REWARD_POOL, IRONCLAD_STARTER_DECK, CardDef, EnemyDef

try:
    import gymnasium as gym
    from gymnasium import spaces
except Exception:  # pragma: no cover - keeps the simulator usable without RL extras.
    gym = None
    spaces = None


MAX_HAND = 10
MAX_DECK_FEATURES = 64
MAX_TURNS = 80


@dataclass
class CombatConfig:
    deck: list[str] | None = None
    encounter_pool: str = "weak"
    enemy_id: str | None = None
    random_extra_cards: tuple[int, int] = (0, 0)
    seed: int | None = None
    player_hp: int = 80
    ascension: int = 0


class SlS2CombatEnv(gym.Env if gym else object):
    """Single-player, single-enemy simplified combat environment.

    Action space:
      0..9  play hand slot 0..9
      10    end turn

    Observation is a fixed vector. See READ/Training.md for exact layout.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, config: CombatConfig | None = None):
        self.config = config or CombatConfig()
        self.action_space = spaces.Discrete(MAX_HAND + 1) if spaces else None
        self.observation_space = (
            spaces.Box(-10.0, 10.0, shape=(32 + MAX_HAND * 8 + MAX_DECK_FEATURES,), dtype=np.float32)
            if spaces
            else None
        )
        self.rng = random.Random(self.config.seed)
        self._last_info: dict[str, Any] = {}

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        if seed is not None:
            self.rng.seed(seed)
        if options:
            self.config = CombatConfig(**{**self.config.__dict__, **options})
        self.turn = 0
        self.energy = 3
        self.player_hp = self.config.player_hp
        self.player_max_hp = self.config.player_hp
        self.player_block = 0
        self.player_strength = 0
        self.player_weak = 0
        self.player_vulnerable = 0
        self.enemy_strength = 0
        self.enemy_vulnerable = 0
        self.enemy_weak = 0
        self.enemy_block = 0
        self.exhaust: list[str] = []
        self.discard: list[str] = []

        enemy_id = self.config.enemy_id or self.rng.choice(ENCOUNTER_POOLS[self.config.encounter_pool])
        self.enemy: EnemyDef = ENEMIES[enemy_id]
        self.enemy_hp = self.enemy.max_hp
        self.enemy_max_hp = self.enemy.max_hp

        deck = list(self.config.deck or IRONCLAD_STARTER_DECK)
        lo, hi = self.config.random_extra_cards
        for _ in range(self.rng.randint(lo, hi)):
            deck.append(self.rng.choice(IRONCLAD_REWARD_POOL))
        self.draw_pile = deck[:]
        self.rng.shuffle(self.draw_pile)
        self.hand: list[str] = []
        self._draw(5)
        self._last_info = {}
        return self._obs(), self._info()

    def action_masks(self) -> np.ndarray:
        mask = np.zeros(MAX_HAND + 1, dtype=bool)
        for i, card_id in enumerate(self.hand[:MAX_HAND]):
            card = CARDS[card_id]
            mask[i] = card.cost >= 0 and card.cost <= self.energy and self._has_valid_target(card)
        mask[MAX_HAND] = True
        return mask

    def step(self, action: int):
        reward = -0.01
        terminated = False
        truncated = False
        if action == MAX_HAND:
            reward += self._end_turn()
        elif 0 <= action < len(self.hand):
            if not self.action_masks()[action]:
                reward -= 0.25
            else:
                reward += self._play_card(action)
        else:
            reward -= 0.25

        if self.enemy_hp <= 0:
            terminated = True
            reward += 10.0 + self.player_hp / max(1, self.player_max_hp)
        elif self.player_hp <= 0:
            terminated = True
            reward -= 10.0
        elif self.turn >= MAX_TURNS:
            truncated = True
            reward -= 3.0
        return self._obs(), float(reward), terminated, truncated, self._info()

    def render(self):
        print(
            f"turn={self.turn} hp={self.player_hp}/{self.player_max_hp} block={self.player_block} "
            f"energy={self.energy} enemy={self.enemy.id}:{self.enemy_hp}/{self.enemy_max_hp} "
            f"intent={self.enemy.move_for_turn(self.turn).id} hand={self.hand}"
        )

    def _play_card(self, index: int) -> float:
        card_id = self.hand.pop(index)
        card = CARDS[card_id]
        self.energy -= card.cost
        reward = 0.0
        if card.block:
            self.player_block += card.block
            reward += card.block * 0.01
        if card.strength:
            self.player_strength += card.strength
            reward += 0.08 * card.strength
        if card.damage:
            damage = max(0, card.damage + self.player_strength)
            if self.player_weak > 0:
                damage = int(damage * 0.75)
            if self.enemy_vulnerable > 0:
                damage = int(damage * 1.5)
            unblocked = max(0, damage - self.enemy_block)
            self.enemy_block = max(0, self.enemy_block - damage)
            self.enemy_hp -= unblocked
            reward += unblocked * 0.03
        if card.vulnerable:
            self.enemy_vulnerable = max(self.enemy_vulnerable, card.vulnerable)
        if card.weak:
            self.enemy_weak = max(self.enemy_weak, card.weak)
        if card.draw:
            self._draw(card.draw)
        if card.exhaust or card.type == "Power":
            self.exhaust.append(card_id)
        else:
            self.discard.append(card_id)
        return reward

    def _end_turn(self) -> float:
        reward = 0.0
        move = self.enemy.move_for_turn(self.turn)
        if move.damage:
            damage = max(0, move.damage + self.enemy_strength)
            if self.enemy_weak > 0:
                damage = int(damage * 0.75)
            if self.player_vulnerable > 0:
                damage = int(damage * 1.5)
            for _ in range(move.hits):
                unblocked = max(0, damage - self.player_block)
                self.player_block = max(0, self.player_block - damage)
                self.player_hp -= unblocked
                reward -= unblocked * 0.04
        self.enemy_block += move.block
        self.enemy_strength += move.strength
        self.player_vulnerable = max(self.player_vulnerable, move.vulnerable)
        self.player_weak = max(self.player_weak, move.weak)
        self.discard.extend(self.hand)
        self.hand.clear()
        self.turn += 1
        self.energy = 3
        self.player_block = 0
        self.enemy_block = 0
        self.player_weak = max(0, self.player_weak - 1)
        self.player_vulnerable = max(0, self.player_vulnerable - 1)
        self.enemy_weak = max(0, self.enemy_weak - 1)
        self.enemy_vulnerable = max(0, self.enemy_vulnerable - 1)
        self._draw(5)
        return reward

    def _draw(self, n: int) -> None:
        for _ in range(n):
            if len(self.hand) >= MAX_HAND:
                return
            if not self.draw_pile:
                self.draw_pile = self.discard[:]
                self.discard.clear()
                self.rng.shuffle(self.draw_pile)
            if not self.draw_pile:
                return
            self.hand.append(self.draw_pile.pop())

    def _has_valid_target(self, card: CardDef) -> bool:
        return card.target in {"Self", "None"} or self.enemy_hp > 0

    def _obs(self) -> np.ndarray:
        move = self.enemy.move_for_turn(self.turn)
        base = [
            self.player_hp / self.player_max_hp,
            self.player_block / 100,
            self.energy / 3,
            self.player_strength / 20,
            self.player_weak / 5,
            self.player_vulnerable / 5,
            self.enemy_hp / self.enemy_max_hp,
            self.enemy_block / 100,
            self.enemy_strength / 20,
            self.enemy_weak / 5,
            self.enemy_vulnerable / 5,
            move.damage / 40,
            move.hits / 5,
            move.block / 40,
            move.strength / 10,
            move.vulnerable / 5,
            move.weak / 5,
            self.turn / MAX_TURNS,
            len(self.draw_pile) / 40,
            len(self.discard) / 40,
            len(self.exhaust) / 40,
        ]
        base.extend([0.0] * (32 - len(base)))
        hand_features: list[float] = []
        for i in range(MAX_HAND):
            if i < len(self.hand):
                c = CARDS[self.hand[i]]
                hand_features.extend([c.cost / 3, c.damage / 30, c.block / 30, c.vulnerable / 5, c.weak / 5, c.strength / 10, c.draw / 5, 1.0])
            else:
                hand_features.extend([0.0] * 8)
        deck_counts = [0.0] * MAX_DECK_FEATURES
        for zone in (self.hand, self.draw_pile, self.discard):
            for cid in zone:
                idx = list(CARDS).index(cid)
                if idx < MAX_DECK_FEATURES:
                    deck_counts[idx] += 1 / 10
        return np.array(base + hand_features + deck_counts, dtype=np.float32)

    def _info(self) -> dict[str, Any]:
        return {
            "enemy_id": self.enemy.id,
            "player_hp": self.player_hp,
            "enemy_hp": self.enemy_hp,
            "turn": self.turn,
            "action_mask": self.action_masks(),
        }
