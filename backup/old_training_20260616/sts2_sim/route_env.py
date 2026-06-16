from __future__ import annotations

import random
from dataclasses import dataclass, field

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from sts2_sim.cards import (
    CARD_LIBRARY,
    ironclad_a0_starting_deck,
    ironclad_singleplayer_reward_pool,
)
from sts2_sim.engine import END_TURN, Action, CombatEnv
from sts2_sim.enemies import (
    ENCOUNTERS,
    ENEMY_LIBRARY,
    UNDERDOCKS_BOSS_ENCOUNTERS,
    UNDERDOCKS_ELITE_ENCOUNTERS,
    UNDERDOCKS_REGULAR_ENCOUNTERS,
    UNDERDOCKS_WEAK_ENCOUNTERS,
)


MAX_ROUTE_DECK = 40
MAX_ROUTE_ENEMIES = 5
MAX_REWARD_CHOICES = 3
MAX_COMBAT_CHOICE = MAX_ROUTE_DECK
HAND_FEATURES = 8
ENEMY_FEATURES = 10
CARD_FEATURES = 4
GLOBAL_FEATURES = 36
REWARD_FEATURES = MAX_REWARD_CHOICES * CARD_FEATURES
DECK_FEATURES = MAX_ROUTE_DECK * CARD_FEATURES
OBS_SIZE = (
    GLOBAL_FEATURES
    + MAX_ROUTE_ENEMIES * ENEMY_FEATURES
    + CombatEnv.max_hand_size * HAND_FEATURES
    + REWARD_FEATURES
    + DECK_FEATURES
)

ROUTE_PHASES = ("combat", "reward", "rest", "done")
CARD_IDS = tuple(sorted(CARD_LIBRARY))
CARD_INDEX = {card_id: idx + 1 for idx, card_id in enumerate(CARD_IDS)}
RARITY_ORDER = ("common", "uncommon", "rare")
RARITY_INDEX = {"common": 1.0, "uncommon": 2.0, "rare": 3.0}


@dataclass(frozen=True)
class RouteCombatActionSpec:
    hand_index: int
    target_index: int | None = None
    choice_index: int | None = None

    def to_engine_action(self) -> Action:
        if self.hand_index < 0:
            return END_TURN
        if self.choice_index is None:
            return (self.hand_index, self.target_index)
        return (self.hand_index, self.target_index, self.choice_index)


@dataclass
class RouteResult:
    won: bool
    final_hp: int
    total_hp_lost: int
    combats_won: int
    route: list[str]
    deck: list[str]
    picks: list[str] = field(default_factory=list)
    upgrades: list[str] = field(default_factory=list)
    rests: int = 0
    log: list[str] = field(default_factory=list)


def build_route_combat_catalog() -> tuple[RouteCombatActionSpec, ...]:
    specs = [RouteCombatActionSpec(-1, None, None)]
    choice_values: list[int | None] = [None] + list(range(MAX_COMBAT_CHOICE))
    target_values: list[int | None] = [None] + list(range(MAX_ROUTE_ENEMIES))
    for hand_index in range(CombatEnv.max_hand_size):
        for target_index in target_values:
            for choice_index in choice_values:
                specs.append(RouteCombatActionSpec(hand_index, target_index, choice_index))
    return tuple(specs)


class CardRewardRng:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.rare_offset = -0.05
        self.reward_pool = ironclad_singleplayer_reward_pool()

    def generate(self, room_type: str, count: int = 3) -> list[str]:
        blacklist: set[str] = set()
        cards: list[str] = []
        for _ in range(count):
            rarity = self._roll_rarity(room_type)
            card_id = self._roll_card(rarity, blacklist)
            blacklist.add(card_id)
            cards.append(card_id)
        return cards

    def _roll_rarity(self, room_type: str) -> str:
        if room_type == "elite":
            rare_base = 0.10
            uncommon_base = 0.40
        elif room_type == "boss":
            rare_base = 1.0
            uncommon_base = 0.0
        else:
            rare_base = 0.03
            uncommon_base = 0.37
        rare_threshold = rare_base + (0.0 if room_type == "boss" else self.rare_offset)
        roll = self.rng.random()
        if roll < rare_threshold:
            self.rare_offset = -0.05
            return "rare"
        self.rare_offset = min(self.rare_offset + 0.01, 0.40)
        if roll < rare_threshold + uncommon_base:
            return "uncommon"
        return "common"

    def _roll_card(self, rarity: str, blacklist: set[str]) -> str:
        for candidate_rarity in self._rarity_wrap(rarity):
            candidates = [
                card_id
                for card_id in self.reward_pool
                if card_id not in blacklist and CARD_LIBRARY[card_id].rarity == candidate_rarity
            ]
            if candidates:
                return self.rng.choice(candidates)
        raise RuntimeError("No valid card reward candidates.")

    @staticmethod
    def _rarity_wrap(rarity: str):
        start = RARITY_ORDER.index(rarity)
        for offset in range(len(RARITY_ORDER)):
            yield RARITY_ORDER[(start + offset) % len(RARITY_ORDER)]


class UnderdocksRoutePPOEnv(gym.Env):
    metadata = {"render_modes": []}

    combat_catalog = build_route_combat_catalog()
    combat_action_to_index = {
        spec.to_engine_action(): idx for idx, spec in enumerate(combat_catalog)
    }
    reward_action_offset = len(combat_catalog)
    rest_action_offset = reward_action_offset + MAX_REWARD_CHOICES + 1
    rest_action_count = 1 + MAX_ROUTE_DECK

    def __init__(
        self,
        *,
        seed: int | None = None,
        max_turns_per_combat: int = 60,
        enable_burning_blood: bool = True,
    ) -> None:
        super().__init__()
        self.base_seed = seed
        self.max_turns_per_combat = max_turns_per_combat
        self.enable_burning_blood = enable_burning_blood
        self.episode_index = 0
        self.action_space = spaces.Discrete(self.rest_action_offset + self.rest_action_count)
        self.observation_space = spaces.Box(
            low=-10.0,
            high=10.0,
            shape=(OBS_SIZE,),
            dtype=np.float32,
        )
        self._reset_state(seed)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is None and self.base_seed is not None:
            seed = self.base_seed + self.episode_index
        self.episode_index += 1
        self._reset_state(seed)
        return self._obs(), {}

    def step(self, action: int):
        action = int(action)
        if action < 0 or action >= self.action_space.n or not self.action_masks()[action]:
            action = self._first_legal_action()

        before_hp = self.hp
        before_enemy_hp = self._enemy_hp_total()
        reward = -0.002
        info: dict = {}

        if self.phase == "combat":
            combat_action = self.combat_catalog[action].to_engine_action()
            _, _, done, combat_info = self.combat.step(combat_action)
            damage_dealt = 0 if combat_action == END_TURN else max(0, before_enemy_hp - self._enemy_hp_total())
            hp_lost = max(0, before_hp - self.combat.player.hp)
            reward += damage_dealt * 0.01 - hp_lost * 0.2
            self.hp = self.combat.player.hp
            self.max_hp = self.combat.player.max_hp
            if done:
                result = combat_info["result"]
                self.hp = max(0, result.final_hp)
                self.max_hp = self.combat.player.max_hp
                room_type, encounter_id = self.route[self.route_index]
                if result.won:
                    self.combats_won += 1
                    room_loss = max(0, before_hp - self.hp)
                    self.log.append(
                        f"Combat won: {encounter_id}, turns={result.turns}, "
                        f"final_hp={self.hp}, room_hp_loss={room_loss}"
                    )
                    room_reward = {
                        "monster": 28.0,
                        "elite": 55.0,
                        "boss": 120.0,
                    }.get(room_type, 28.0)
                    route_progress_reward = self.combats_won * 5.0
                    reward += room_reward + route_progress_reward - room_loss * 0.9 - result.turns * 0.03
                    if room_type == "boss":
                        self.phase = "done"
                        reward += 260.0 + self.hp * 2.0 - self.total_hp_lost * 1.0
                        info["result"] = self.result(won=True)
                    else:
                        if self.combats_won >= 6:
                            reward += 80.0
                        self.reward_choices = self.card_rewards.generate(room_type, MAX_REWARD_CHOICES)
                        self.phase = "reward"
                else:
                    self.log.append(
                        f"Combat lost: {encounter_id}, turns={result.turns}, "
                        f"combats_won={self.combats_won}, final_hp={self.hp}"
                    )
                    self.phase = "done"
                    damage_progress = self._combat_damage_progress()
                    reward += -120.0 + self.combats_won * 22.0 + damage_progress * 45.0 - self.total_hp_lost * 0.8
                    info["result"] = self.result(won=False)

        elif self.phase == "reward":
            choice = action - self.reward_action_offset
            if 0 <= choice < len(self.reward_choices):
                card_id = self.reward_choices[choice]
                self.deck.append(card_id)
                self.picks.append(card_id)
                self.log.append(f"Reward pick: {CARD_LIBRARY[card_id].name}")
                reward += 1.0
            else:
                self.picks.append("skip")
                self.log.append("Reward pick: Skip")
                reward -= 0.25
            self.reward_choices = []
            self._advance_after_noncombat()

        elif self.phase == "rest":
            rest_choice = action - self.rest_action_offset
            if rest_choice == 0:
                healed = min(self.max_hp - self.hp, int(self.max_hp * 0.3))
                self.hp += healed
                self.rests += 1
                self.log.append(f"Rest site: rest for {healed} HP")
                if self.hp >= int(self.max_hp * 0.7):
                    reward -= 3.0
                else:
                    reward += healed * 0.02
            else:
                deck_index = rest_choice - 1
                old_id = self.deck[deck_index]
                new_id = CARD_LIBRARY[old_id].upgraded_id
                if new_id is None:
                    raise RuntimeError("Illegal smith action reached step().")
                self.deck[deck_index] = new_id
                self.upgrades.append(f"{old_id}->{new_id}")
                self.log.append(
                    f"Rest site: upgrade {CARD_LIBRARY[old_id].name} to {CARD_LIBRARY[new_id].name}"
                )
                reward += 12.0
            self._advance_after_noncombat()

        terminated = self.phase == "done"
        truncated = False
        if terminated and "result" not in info:
            info["result"] = self.result(won=self.hp > 0)
        return self._obs(), float(reward), terminated, truncated, info

    @property
    def total_hp_lost(self) -> int:
        return max(0, self.max_hp - max(0, self.hp))

    def action_masks(self) -> np.ndarray:
        mask = np.zeros(self.action_space.n, dtype=bool)
        if self.phase == "combat":
            for action in self.combat.legal_actions():
                idx = self.combat_action_to_index.get(action)
                if idx is not None:
                    mask[idx] = True
        elif self.phase == "reward":
            for idx in range(len(self.reward_choices)):
                mask[self.reward_action_offset + idx] = True
            mask[self.reward_action_offset + MAX_REWARD_CHOICES] = True
        elif self.phase == "rest":
            mask[self.rest_action_offset] = True
            for deck_index, card_id in enumerate(self.deck[:MAX_ROUTE_DECK]):
                if CARD_LIBRARY[card_id].upgraded_id is not None:
                    mask[self.rest_action_offset + 1 + deck_index] = True
        return mask

    def describe_action(self, action_index: int) -> str:
        action_index = int(action_index)
        if self.phase == "combat":
            spec = self.combat_catalog[action_index]
            if spec.hand_index < 0:
                return "End turn"
            if spec.hand_index >= len(self.combat.hand):
                return "Illegal combat action"
            card_instance = self.combat.hand[spec.hand_index]
            card = CARD_LIBRARY[card_instance.def_id]
            parts = [f"Play hand[{spec.hand_index}] {card.name}"]
            if spec.target_index is not None and spec.target_index < len(self.combat.enemies):
                target = self.combat.enemies[spec.target_index]
                parts.append(f"target {target.creature.name}")
            if spec.choice_index is not None:
                parts.append(f"choice {spec.choice_index}")
            return ", ".join(parts)
        if self.phase == "reward":
            choice = action_index - self.reward_action_offset
            if 0 <= choice < len(self.reward_choices):
                card_id = self.reward_choices[choice]
                return f"Pick reward {choice + 1}: {CARD_LIBRARY[card_id].name}"
            return "Skip reward"
        if self.phase == "rest":
            choice = action_index - self.rest_action_offset
            if choice == 0:
                return "Rest"
            deck_index = choice - 1
            if 0 <= deck_index < len(self.deck):
                return f"Upgrade deck[{deck_index}] {CARD_LIBRARY[self.deck[deck_index]].name}"
            return "Illegal rest action"
        return "Done"

    def result(self, *, won: bool) -> RouteResult:
        return RouteResult(
            won=won,
            final_hp=max(0, self.hp),
            total_hp_lost=self.total_hp_lost,
            combats_won=self.combats_won,
            route=[encounter_id for _, encounter_id in self.route],
            deck=list(self.deck),
            picks=list(self.picks),
            upgrades=list(self.upgrades),
            rests=self.rests,
            log=list(self.log),
        )

    def _reset_state(self, seed: int | None) -> None:
        self.rng = random.Random(seed)
        self.card_rewards = CardRewardRng(self.rng)
        self.max_hp = 80
        self.hp = 80
        self.deck = ironclad_a0_starting_deck()
        self.route = self._build_route()
        self.route_index = 0
        self.phase = "combat"
        self.reward_choices: list[str] = []
        self.picks: list[str] = []
        self.upgrades: list[str] = []
        self.rests = 0
        self.combats_won = 0
        self.log: list[str] = []
        self.combat = self._new_combat(self.route[0][1])

    def _build_route(self) -> list[tuple[str, str]]:
        weak = self.rng.sample(list(UNDERDOCKS_WEAK_ENCOUNTERS), 3)
        regular = self.rng.sample(list(UNDERDOCKS_REGULAR_ENCOUNTERS), 2)
        elite = self.rng.choice(list(UNDERDOCKS_ELITE_ENCOUNTERS))
        boss = self.rng.choice(list(UNDERDOCKS_BOSS_ENCOUNTERS))
        return [
            ("monster", weak[0]),
            ("monster", weak[1]),
            ("rest", "rest_site_1"),
            ("monster", weak[2]),
            ("elite", elite),
            ("rest", "rest_site_2"),
            ("monster", regular[0]),
            ("monster", regular[1]),
            ("rest", "rest_site_3"),
            ("boss", boss),
        ]

    def _new_combat(self, encounter_id: str) -> CombatEnv:
        enemies = [ENEMY_LIBRARY[enemy_id] for enemy_id in ENCOUNTERS[encounter_id]]
        return CombatEnv(
            list(self.deck),
            enemies,
            player_hp=self.hp,
            player_max_hp=self.max_hp,
            seed=self.rng.randrange(2**31),
            max_turns=self.max_turns_per_combat,
            enable_burning_blood=self.enable_burning_blood,
        )

    def _advance_after_noncombat(self) -> None:
        self.route_index += 1
        while self.route_index < len(self.route) and self.route[self.route_index][0] == "rest":
            self.phase = "rest"
            return
        if self.route_index >= len(self.route):
            self.phase = "done"
            return
        self.phase = "combat"
        self.combat = self._new_combat(self.route[self.route_index][1])

    def _first_legal_action(self) -> int:
        legal = np.flatnonzero(self.action_masks())
        if len(legal) == 0:
            return 0
        return int(legal[0])

    def _enemy_hp_total(self) -> int:
        if self.phase != "combat":
            return 0
        return sum(
            min(enemy.creature.hp, enemy.definition.max_hp)
            for enemy in self.combat.enemies
            if enemy.alive
        )

    def _combat_damage_progress(self) -> float:
        if self.phase != "combat":
            return 0.0
        total = sum(enemy.definition.max_hp for enemy in self.combat.enemies)
        remaining = self._enemy_hp_total()
        return max(0.0, min(1.0, 1.0 - remaining / max(1, total)))

    def _obs(self) -> np.ndarray:
        features: list[float] = []
        phase_one_hot = [1.0 if self.phase == phase else 0.0 for phase in ROUTE_PHASES]
        features.extend(phase_one_hot)
        features.extend(
            [
                self.hp / self.max_hp,
                len(self.deck) / MAX_ROUTE_DECK,
                self.route_index / max(1, len(self.route) - 1),
                self.card_rewards.rare_offset,
                self.combats_won / 6.0,
                self.rests / 3.0,
                sum(1 for c in self.deck if CARD_LIBRARY[c].card_type == "attack") / MAX_ROUTE_DECK,
                sum(1 for c in self.deck if CARD_LIBRARY[c].card_type == "skill") / MAX_ROUTE_DECK,
                sum(1 for c in self.deck if CARD_LIBRARY[c].card_type == "power") / MAX_ROUTE_DECK,
                sum(1 for c in self.deck if c.endswith("_plus")) / MAX_ROUTE_DECK,
                self._combat_damage_progress(),
            ]
        )
        if self.phase == "combat":
            combat = self.combat
            features.extend(
                [
                    combat.player.block / 50.0,
                    combat.energy / 5.0,
                    combat.turn / combat.max_turns,
                    combat.player.power_amount("strength") / 10.0,
                    combat.player.power_amount("vulnerable") / 5.0,
                    combat.player.power_amount("weak") / 5.0,
                    combat.player.power_amount("frail") / 5.0,
                    len(combat.draw_pile) / MAX_ROUTE_DECK,
                    len(combat.discard_pile) / MAX_ROUTE_DECK,
                    len(combat.exhaust_pile) / MAX_ROUTE_DECK,
                ]
            )
        while len(features) < GLOBAL_FEATURES:
            features.append(0.0)
        features = features[:GLOBAL_FEATURES]

        for slot in range(MAX_ROUTE_ENEMIES):
            if self.phase != "combat" or slot >= len(self.combat.enemies):
                features.extend([0.0] * ENEMY_FEATURES)
                continue
            enemy = self.combat.enemies[slot]
            move = self.combat.current_enemy_move(enemy)
            features.extend(
                [
                    1.0 if enemy.alive else 0.0,
                    enemy.creature.hp / max(1, enemy.creature.max_hp),
                    enemy.creature.block / 50.0,
                    enemy.creature.power_amount("strength") / 10.0,
                    enemy.creature.power_amount("vulnerable") / 5.0,
                    enemy.creature.power_amount("ritual") / 10.0,
                    enemy.creature.power_amount("plating") / 20.0,
                    move.damage / 30.0,
                    move.hits / 5.0,
                    move.block / 30.0,
                ]
            )

        for slot in range(CombatEnv.max_hand_size):
            if self.phase != "combat" or slot >= len(self.combat.hand):
                features.extend([0.0] * HAND_FEATURES)
                continue
            card_instance = self.combat.hand[slot]
            card = CARD_LIBRARY[card_instance.def_id]
            estimate_target = next((e.creature for e in self.combat.enemies if e.alive), None)
            damage = self.combat.estimate_card_damage(card_instance, estimate_target) if estimate_target else 0
            features.extend(
                [
                    1.0,
                    CARD_INDEX.get(card_instance.def_id, 0) / len(CARD_INDEX),
                    max(card.cost, 0) / 3.0,
                    1.0 if card.card_type == "attack" else 0.0,
                    1.0 if card.card_type == "skill" else 0.0,
                    1.0 if card.card_type == "power" else 0.0,
                    1.0 if self.combat.can_play(card, card_instance) else 0.0,
                    damage / 80.0,
                ]
            )

        for slot in range(MAX_REWARD_CHOICES):
            card_id = self.reward_choices[slot] if slot < len(self.reward_choices) else None
            features.extend(self._card_features(card_id))

        for slot in range(MAX_ROUTE_DECK):
            card_id = self.deck[slot] if slot < len(self.deck) else None
            features.extend(self._card_features(card_id))

        return np.asarray(features, dtype=np.float32)

    @staticmethod
    def _card_features(card_id: str | None) -> list[float]:
        if card_id is None:
            return [0.0] * CARD_FEATURES
        card = CARD_LIBRARY[card_id]
        return [
            CARD_INDEX.get(card_id, 0) / len(CARD_INDEX),
            max(card.cost, 0) / 3.0,
            RARITY_INDEX.get(card.rarity, 0.0) / 3.0,
            1.0 if card.upgraded_id is None and card_id.endswith("_plus") else 0.0,
        ]
