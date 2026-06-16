from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from sb3_contrib import MaskablePPO

from battle_ai.env import CARD_IDS, CARD_INDEX, GenericBattlePPOEnv
from battle_ai.samplers import RARITY_WEIGHTS
from sts2_sim.cards import CARD_LIBRARY, ironclad_a0_starting_deck, ironclad_singleplayer_reward_pool
from sts2_sim.data import EnemyDef
from sts2_sim.engine import CombatEnv
from sts2_sim.enemies import (
    ENEMY_LIBRARY,
    UNDERDOCKS_BOSS_ENCOUNTERS,
    UNDERDOCKS_ELITE_ENCOUNTERS,
    UNDERDOCKS_REGULAR_ENCOUNTERS,
    UNDERDOCKS_WEAK_ENCOUNTERS,
)


MAX_ROUTE_DECK = 45
MAX_REWARD_CHOICES = 3
ACTION_COUNT = 1 + MAX_REWARD_CHOICES + 1 + MAX_ROUTE_DECK
GLOBAL_FEATURES = 36
CARD_FEATURES = 8
OBS_SIZE = (
    GLOBAL_FEATURES
    + 2 * MAX_REWARD_CHOICES * CARD_FEATURES
    + MAX_ROUTE_DECK * CARD_FEATURES
    + 3 * len(CARD_IDS)
)

ACTION_SKIP = 0
ACTION_REWARD_OFFSET = 1
ACTION_REST = ACTION_REWARD_OFFSET + MAX_REWARD_CHOICES
ACTION_UPGRADE_OFFSET = ACTION_REST + 1


ROUTE_TEMPLATE: tuple[str, ...] = (
    "weak",
    "weak",
    "campfire",
    "weak",
    "elite",
    "campfire",
    "regular",
    "regular",
    "campfire",
    "boss",
)


STAGE_POOLS = {
    "weak": UNDERDOCKS_WEAK_ENCOUNTERS,
    "regular": UNDERDOCKS_REGULAR_ENCOUNTERS,
    "elite": UNDERDOCKS_ELITE_ENCOUNTERS,
    "boss": UNDERDOCKS_BOSS_ENCOUNTERS,
}


@dataclass
class OuterRouteResult:
    won: bool
    final_hp: int
    max_hp: int
    combats_won: int
    total_hp_lost: int
    route: list[str]
    deck: list[str]
    picks: list[str] = field(default_factory=list)
    reward_offers: list[tuple[str, str, str]] = field(default_factory=list)
    upgrades: list[str] = field(default_factory=list)
    rests: int = 0
    log: list[str] = field(default_factory=list)


class RewardRng:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.pool = ironclad_singleplayer_reward_pool()
        self.rare_offset = -0.05

    def generate(self, room_type: str) -> list[str]:
        cards: list[str] = []
        blacklist: set[str] = set()
        for _ in range(MAX_REWARD_CHOICES):
            rarity = self._roll_rarity(room_type)
            candidates = [
                card_id
                for card_id in self.pool
                if card_id not in blacklist and CARD_LIBRARY[card_id].rarity == rarity
            ]
            if not candidates:
                candidates = [card_id for card_id in self.pool if card_id not in blacklist]
            card_id = self.rng.choice(candidates)
            cards.append(card_id)
            blacklist.add(card_id)
        return cards

    def _roll_rarity(self, room_type: str) -> str:
        if room_type == "elite":
            rare_base, uncommon_base = 0.10, 0.40
        elif room_type == "boss":
            rare_base, uncommon_base = 1.0, 0.0
        else:
            rare_base, uncommon_base = 0.03, 0.37
        rare_threshold = rare_base + (0.0 if room_type == "boss" else self.rare_offset)
        roll = self.rng.random()
        if roll < rare_threshold:
            self.rare_offset = -0.05
            return "rare"
        self.rare_offset = min(0.40, self.rare_offset + 0.01)
        if roll < rare_threshold + uncommon_base:
            return "uncommon"
        return "common"


class BattleDelegatingRouteEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(
        self,
        *,
        battle_model_path: str = "battle_ai_models/ppo_generic_battle.zip",
        seed: int | None = None,
        max_turns_per_combat: int = 80,
        deterministic_battle: bool = True,
        enable_burning_blood: bool = True,
    ) -> None:
        super().__init__()
        self.battle_model_path = battle_model_path
        self.base_seed = seed
        self.max_turns_per_combat = max_turns_per_combat
        self.deterministic_battle = deterministic_battle
        self.enable_burning_blood = enable_burning_blood
        self.action_space = spaces.Discrete(ACTION_COUNT)
        self.observation_space = spaces.Box(low=-20.0, high=20.0, shape=(OBS_SIZE,), dtype=np.float32)
        self.episode_index = 0
        self._battle_wrapper = GenericBattlePPOEnv(seed=seed, stage="weak")
        self._battle_model: MaskablePPO | None = None
        self._reset_state(seed)

    @property
    def battle_model(self) -> MaskablePPO:
        if self._battle_model is None:
            path = Path(self.battle_model_path)
            if not path.exists():
                raise FileNotFoundError(f"Battle model not found: {path}")
            self._battle_model = MaskablePPO.load(str(path), env=self._battle_wrapper, device="auto")
        return self._battle_model

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is None and self.base_seed is not None:
            seed = self.base_seed + self.episode_index
        self.episode_index += 1
        self._reset_state(seed)
        self._advance_until_decision()
        return self._obs(), {}

    def step(self, action: int):
        action = int(action)
        if action < 0 or action >= ACTION_COUNT or not self.action_masks()[action]:
            action = int(np.flatnonzero(self.action_masks())[0])
        reward = -0.01
        info: dict = {}

        if self.phase == "reward":
            if action == ACTION_SKIP:
                self.picks.append("skip")
                self.log.append("Pick: skip")
                reward -= 0.4
            else:
                choice = action - ACTION_REWARD_OFFSET
                card_id = self.reward_choices[choice]
                self.deck.append(card_id)
                self.picks.append(card_id)
                self.log.append(f"Pick: {CARD_LIBRARY[card_id].name}")
                reward += self._pick_reward(card_id)
            self.reward_choices = []

        elif self.phase == "campfire":
            if action == ACTION_REST:
                healed = min(self.max_hp - self.hp, int(self.max_hp * 0.30))
                self.hp += healed
                self.rests += 1
                self.log.append(f"Campfire: rest +{healed}")
                reward += healed * 0.18
            else:
                deck_index = action - ACTION_UPGRADE_OFFSET
                card_id = self.deck[deck_index]
                upgraded_id = CARD_LIBRARY[card_id].upgraded_id
                if upgraded_id is not None:
                    self.deck[deck_index] = upgraded_id
                    self.upgrades.append(card_id)
                    self.log.append(f"Campfire: upgrade {CARD_LIBRARY[card_id].name}")
                    reward += 4.0
            self.node_index += 1

        elif self.phase == "done":
            info["result"] = self.result(won=self.hp > 0 and self.node_index >= len(ROUTE_TEMPLATE))
            return self._obs(), 0.0, True, False, info

        self._advance_until_decision()
        done = self.phase == "done"
        if done:
            won = self.hp > 0 and self.node_index >= len(ROUTE_TEMPLATE)
            reward += 350.0 if won else -180.0
            reward += self.hp * 2.0 + self.combats_won * 22.0 - self.total_hp_lost * 0.55
            reward -= max(0, len(self.deck) - 24) * 1.5
            info["result"] = self.result(won=won)
        return self._obs(), float(reward), done, False, info

    def action_masks(self) -> np.ndarray:
        mask = np.zeros(ACTION_COUNT, dtype=bool)
        if self.phase == "reward":
            mask[ACTION_SKIP] = True
            for idx in range(len(self.reward_choices)):
                mask[ACTION_REWARD_OFFSET + idx] = True
        elif self.phase == "campfire":
            mask[ACTION_REST] = True
            for idx, card_id in enumerate(self.deck[:MAX_ROUTE_DECK]):
                if CARD_LIBRARY[card_id].upgraded_id is not None:
                    mask[ACTION_UPGRADE_OFFSET + idx] = True
        else:
            mask[ACTION_SKIP] = True
        return mask

    def describe_action(self, action: int) -> str:
        if self.phase == "reward":
            if action == ACTION_SKIP:
                return "skip reward"
            idx = action - ACTION_REWARD_OFFSET
            if 0 <= idx < len(self.reward_choices):
                return f"pick {CARD_LIBRARY[self.reward_choices[idx]].name}"
        if self.phase == "campfire":
            if action == ACTION_REST:
                return "rest"
            idx = action - ACTION_UPGRADE_OFFSET
            if 0 <= idx < len(self.deck):
                return f"upgrade {CARD_LIBRARY[self.deck[idx]].name}"
        return "noop"

    def result(self, *, won: bool) -> OuterRouteResult:
        return OuterRouteResult(
            won=won,
            final_hp=max(0, self.hp),
            max_hp=self.max_hp,
            combats_won=self.combats_won,
            total_hp_lost=self.total_hp_lost,
            route=list(self.route_ids),
            deck=list(self.deck),
            picks=list(self.picks),
            reward_offers=list(self.reward_offers),
            upgrades=list(self.upgrades),
            rests=self.rests,
            log=list(self.log),
        )

    def _reset_state(self, seed: int | None) -> None:
        self.rng = random.Random(seed)
        self.reward_rng = RewardRng(self.rng)
        self.deck = ironclad_a0_starting_deck()
        self.max_hp = 80
        self.hp = 80
        self.node_index = 0
        self.phase = "route"
        self.reward_choices: list[str] = []
        self.picks: list[str] = []
        self.reward_offers: list[tuple[str, str, str]] = []
        self.upgrades: list[str] = []
        self.rests = 0
        self.combats_won = 0
        self.total_hp_lost = 0
        self.log: list[str] = []
        self.route_ids = [self._roll_encounter_id(node) if node != "campfire" else "campfire" for node in ROUTE_TEMPLATE]

    def _advance_until_decision(self) -> None:
        while self.hp > 0 and self.node_index < len(ROUTE_TEMPLATE):
            node = ROUTE_TEMPLATE[self.node_index]
            if node == "campfire":
                self.phase = "campfire"
                return
            self._run_combat(node, self.route_ids[self.node_index])
            if self.hp <= 0:
                self.phase = "done"
                return
            if node == "boss":
                self.node_index += 1
                self.phase = "done"
                return
            self.reward_choices = self.reward_rng.generate(node)
            self.reward_offers.append(tuple(self.reward_choices))
            self.phase = "reward"
            return
        self.phase = "done"

    def _run_combat(self, node: str, encounter_id: str) -> None:
        enemy_ids = STAGE_POOLS[node][encounter_id]
        enemies = [ENEMY_LIBRARY[enemy_id] for enemy_id in enemy_ids]
        combat = CombatEnv(
            list(self.deck),
            enemies,
            player_hp=self.hp,
            player_max_hp=self.max_hp,
            seed=self.rng.randrange(2**31),
            max_turns=self.max_turns_per_combat,
            enable_burning_blood=self.enable_burning_blood,
        )
        self._battle_wrapper.env = combat
        self._battle_wrapper.scenario = None
        self._battle_wrapper.initial_enemy_hp = self._battle_wrapper._enemy_hp_total(capped=True)
        obs = self._battle_wrapper._obs()
        done = False
        info = {}
        steps = 0
        while not done and steps < 700:
            action, _ = self.battle_model.predict(
                obs,
                deterministic=self.deterministic_battle,
                action_masks=self._battle_wrapper.action_masks(),
            )
            obs, _, terminated, truncated, info = self._battle_wrapper.step(int(action))
            done = terminated or truncated
            steps += 1
        result = info.get("result", combat.result())
        before_hp = self.hp
        self.hp = max(0, result.final_hp)
        self.total_hp_lost += max(0, before_hp - self.hp)
        if result.won:
            self.combats_won += 1
            self.log.append(f"Combat {encounter_id}: win, hp {before_hp}->{self.hp}, turns={result.turns}")
            self.node_index += 1
        else:
            self.log.append(f"Combat {encounter_id}: loss, hp {before_hp}->0, turns={result.turns}")
            self.hp = 0

    def _roll_encounter_id(self, node: str) -> str:
        return self.rng.choice(tuple(STAGE_POOLS[node]))

    def _pick_reward(self, card_id: str) -> float:
        rarity = CARD_LIBRARY[card_id].rarity
        reward = {"common": 0.2, "uncommon": 0.55, "rare": 1.0}.get(rarity, 0.0)
        if len(self.deck) >= 25:
            reward -= 0.5
        if card_id in {"offering", "impervious", "flame_barrier", "shrug_it_off", "pommel_strike", "battle_trance"}:
            reward += 0.25
        return reward

    def _obs(self) -> np.ndarray:
        features: list[float] = [
            self.hp / self.max_hp,
            self.max_hp / 100.0,
            self.node_index / len(ROUTE_TEMPLATE),
            self.combats_won / 7.0,
            self.total_hp_lost / 100.0,
            len(self.deck) / MAX_ROUTE_DECK,
            self.rests / 3.0,
            len(self.upgrades) / 10.0,
            1.0 if self.phase == "reward" else 0.0,
            1.0 if self.phase == "campfire" else 0.0,
            1.0 if self.phase == "done" else 0.0,
        ]
        next_node = ROUTE_TEMPLATE[min(self.node_index, len(ROUTE_TEMPLATE) - 1)]
        for node in ("weak", "regular", "elite", "boss", "campfire"):
            features.append(1.0 if next_node == node else 0.0)
        while len(features) < GLOBAL_FEATURES:
            features.append(0.0)

        for card_id in self.reward_choices:
            features.extend(self._card_features(card_id))
        for _ in range(MAX_REWARD_CHOICES - len(self.reward_choices)):
            features.extend([0.0] * CARD_FEATURES)
        # Skip option features.
        features.extend([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] * MAX_REWARD_CHOICES)

        for card_id in self.deck[:MAX_ROUTE_DECK]:
            features.extend(self._card_features(card_id))
        for _ in range(MAX_ROUTE_DECK - min(len(self.deck), MAX_ROUTE_DECK)):
            features.extend([0.0] * CARD_FEATURES)

        deck_counts = [0.0] * len(CARD_IDS)
        upgraded_counts = [0.0] * len(CARD_IDS)
        reward_seen = [0.0] * len(CARD_IDS)
        for card_id in self.deck:
            idx = CARD_INDEX.get(card_id)
            if idx is not None:
                deck_counts[idx] += 1.0 / 5.0
            base_id = self._base_card_id(card_id)
            if base_id != card_id:
                base_idx = CARD_INDEX.get(base_id)
                if base_idx is not None:
                    upgraded_counts[base_idx] += 1.0 / 5.0
        for card_id in self.picks:
            idx = CARD_INDEX.get(card_id)
            if idx is not None:
                reward_seen[idx] += 1.0 / 5.0
        features.extend(deck_counts)
        features.extend(upgraded_counts)
        features.extend(reward_seen)
        return np.asarray(features[:OBS_SIZE], dtype=np.float32)

    def _card_features(self, card_id: str) -> list[float]:
        card = CARD_LIBRARY[card_id]
        return [
            1.0,
            CARD_INDEX.get(card_id, 0) / max(1, len(CARD_IDS)),
            max(card.cost, 0) / 5.0,
            1.0 if card.card_type == "attack" else 0.0,
            1.0 if card.card_type == "skill" else 0.0,
            1.0 if card.card_type == "power" else 0.0,
            RARITY_WEIGHTS.get(card.rarity, 0.0),
            1.0 if card.upgraded_id is not None else 0.0,
        ]

    def _base_card_id(self, card_id: str) -> str:
        if not card_id.endswith("_plus"):
            return card_id
        return card_id[:-5]
