from __future__ import annotations

from dataclasses import dataclass

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.engine import END_TURN, Action, CombatEnv
from sts2_sim.scenarios import SCENARIO_BUILDERS


SCENARIO_CARD_IDS = tuple(sorted(CARD_LIBRARY))
CARD_INDEX = {card_id: idx + 1 for idx, card_id in enumerate(SCENARIO_CARD_IDS)}
DEFAULT_MAX_DISCARD_CHOICES = 13
SCENARIO_MAX_DISCARD_CHOICES = {
    "ironclad_seapunk_42": 13,
    "ironclad_terror_eel_a9_32": 80,
    "ironclad_calcified_cultist_a10_bonus": 12,
}
MAX_ENEMIES = 1
HAND_FEATURES = 8
GLOBAL_FEATURES = 23
OBS_SIZE = GLOBAL_FEATURES + CombatEnv.max_hand_size * HAND_FEATURES


@dataclass(frozen=True)
class ActionSpec:
    hand_index: int
    target_index: int | None = None
    choice_index: int | None = None

    def to_engine_action(self) -> Action:
        if self.hand_index < 0:
            return END_TURN
        if self.choice_index is None:
            return (self.hand_index, self.target_index)
        return (self.hand_index, self.target_index, self.choice_index)


def build_action_catalog(max_discard_choices: int = DEFAULT_MAX_DISCARD_CHOICES) -> tuple[ActionSpec, ...]:
    specs = [ActionSpec(-1, None, None)]
    choice_values: list[int | None] = [None] + list(range(max_discard_choices))
    for hand_index in range(CombatEnv.max_hand_size):
        for target_index in (None, 0):
            for choice_index in choice_values:
                specs.append(ActionSpec(hand_index, target_index, choice_index))
    return tuple(specs)

class FixedFightPPOEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(
        self,
        *,
        scenario: str = "ironclad_seapunk_42",
        seed: int | None = None,
        max_turns: int = 40,
        enable_burning_blood: bool = False,
        extra_card_id: str | None = None,
    ) -> None:
        super().__init__()
        if scenario not in SCENARIO_BUILDERS:
            raise ValueError(f"Unknown scenario: {scenario}")
        self.scenario = scenario
        self.max_discard_choices = SCENARIO_MAX_DISCARD_CHOICES.get(scenario, DEFAULT_MAX_DISCARD_CHOICES)
        self.action_catalog = build_action_catalog(self.max_discard_choices)
        self.action_to_index = {spec.to_engine_action(): idx for idx, spec in enumerate(self.action_catalog)}
        self.base_seed = seed
        self.max_turns = max_turns
        self.enable_burning_blood = enable_burning_blood
        self.extra_card_id = extra_card_id
        self.episode_index = 0
        self.env = self._new_combat_env(seed)
        self.action_space = spaces.Discrete(len(self.action_catalog))
        self.observation_space = spaces.Box(low=-10.0, high=10.0, shape=(OBS_SIZE,), dtype=np.float32)
        self._last_enemy_hp = self._enemy_hp_total()
        self._last_player_hp = self.env.player.hp

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is None and self.base_seed is not None:
            seed = self.base_seed + self.episode_index
        self.episode_index += 1
        self.env = self._new_combat_env(seed)
        self._last_enemy_hp = self._enemy_hp_total()
        self._last_player_hp = self.env.player.hp
        return self._obs(), {}

    def step(self, action: int):
        action = int(action)
        if action < 0 or action >= len(self.action_catalog) or not self.action_masks()[action]:
            action = 0

        before_enemy_hp = self._enemy_hp_total()
        before_player_hp = self.env.player.hp
        _, _, done, info = self.env.step(self.action_catalog[action].to_engine_action())

        damage_dealt = max(0, before_enemy_hp - self._enemy_hp_total())
        hp_lost = max(0, before_player_hp - self.env.player.hp)
        # Sparse final scoring carries the real objective: win first, then minimize HP loss.
        # Small step rewards remain only as early-training guidance before the policy can win.
        reward = damage_dealt * 0.02 - hp_lost * 0.5 - 0.005

        if done:
            result = info["result"]
            if result.won:
                reward += 100.0 - result.hp_lost * 3.0 - result.turns * 0.2
            else:
                initial_enemy_hp = sum(enemy.creature.max_hp for enemy in self.env.enemies)
                remaining_enemy_hp = self._enemy_hp_total()
                damage_progress = 1.0 - (remaining_enemy_hp / max(1, initial_enemy_hp))
                reward += -120.0 - result.hp_lost * 0.5 + damage_progress * 40.0

        terminated = self.env.player.hp <= 0 or all(not enemy.alive for enemy in self.env.enemies)
        truncated = done and not terminated
        return self._obs(), float(reward), terminated, truncated, info

    def action_masks(self) -> np.ndarray:
        mask = np.zeros(len(self.action_catalog), dtype=bool)
        for action in self.env.legal_actions():
            idx = self.action_to_index.get(action)
            if idx is not None:
                mask[idx] = True
        return mask

    def describe_action(self, action_index: int) -> str:
        spec = self.action_catalog[int(action_index)]
        if spec.hand_index < 0:
            return "结束回合"
        if spec.hand_index >= len(self.env.hand):
            return "非法动作"
        card_instance = self.env.hand[spec.hand_index]
        card = CARD_LIBRARY[card_instance.def_id]
        parts = [f"打出手牌{spec.hand_index}: {card.name}"]
        if spec.target_index is not None and spec.target_index < len(self.env.enemies):
            parts.append(f"目标: {self.env.enemies[spec.target_index].creature.name}")
        if spec.choice_index is not None:
            effect_types = {effect.get("type") for effect in card.effects}
            has_chosen_exhaust = any(
                effect.get("type") == "exhaust_from_hand" and effect.get("mode", "chosen") != "random"
                for effect in card.effects
            )
            has_chosen_upgrade = any(
                effect.get("type") == "upgrade_from_hand" and not bool(effect.get("all", False))
                for effect in card.effects
            )
            if "move_discard_to_draw_top" in effect_types and spec.choice_index < len(self.env.discard_pile):
                chosen = self.env.discard_pile[spec.choice_index]
                parts.append(f"从弃牌堆选: {CARD_LIBRARY[chosen.def_id].name}")
            elif has_chosen_exhaust or has_chosen_upgrade:
                post_play_hand = [
                    card_instance
                    for idx, card_instance in enumerate(self.env.hand)
                    if idx != spec.hand_index
                ]
                if spec.choice_index < len(post_play_hand):
                    chosen = post_play_hand[spec.choice_index]
                    verb = "消耗" if has_chosen_exhaust else "升级"
                    parts.append(f"从手牌选{verb}: {CARD_LIBRARY[chosen.def_id].name}")
        return "，".join(parts)

    def _new_combat_env(self, seed: int | None) -> CombatEnv:
        return SCENARIO_BUILDERS[self.scenario](
            seed=seed,
            max_turns=self.max_turns,
            enable_burning_blood=self.enable_burning_blood,
            extra_card_id=self.extra_card_id,
        )

    def _enemy_hp_total(self) -> int:
        return sum(enemy.creature.hp for enemy in self.env.enemies if enemy.alive)

    def _obs(self) -> np.ndarray:
        env = self.env
        enemy = env.enemies[0]
        move = env.current_enemy_move(enemy)
        move_one_hot = [0.0, 0.0, 0.0, 0.0]
        move_one_hot[min(enemy.move_index, 3)] = 1.0
        global_features = [
            env.player.hp / env.player.max_hp,
            env.player.block / 30.0,
            env.energy / 5.0,
            env.turn / env.max_turns,
            env.player.power_amount("strength") / 10.0,
            env.player.power_amount("vulnerable") / 5.0,
            env.player.power_amount("weak") / 5.0,
            env.player.power_amount("frail") / 5.0,
            enemy.creature.hp / enemy.creature.max_hp,
            enemy.creature.block / 30.0,
            enemy.creature.power_amount("strength") / 10.0,
            enemy.creature.power_amount("vulnerable") / 5.0,
            enemy.creature.power_amount("vigor") / 20.0,
            enemy.creature.power_amount("shriek") / 100.0,
            move.damage / 20.0,
            move.hits / 5.0,
            move.block / 20.0,
            len(env.draw_pile) / 20.0,
            len(env.discard_pile) / 20.0,
        ]
        features = global_features + move_one_hot
        features = features[:GLOBAL_FEATURES]
        while len(features) < GLOBAL_FEATURES:
            features.append(0.0)

        for slot in range(env.max_hand_size):
            if slot >= len(env.hand):
                features.extend([0.0] * HAND_FEATURES)
                continue
            card_instance = env.hand[slot]
            card = CARD_LIBRARY[card_instance.def_id]
            features.extend(
                [
                    1.0,
                    CARD_INDEX.get(card_instance.def_id, 0) / max(1, len(CARD_INDEX)),
                    max(card.cost, 0) / 3.0,
                    1.0 if card.card_type == "attack" else 0.0,
                    1.0 if card.card_type == "skill" else 0.0,
                    1.0 if card.card_type == "power" else 0.0,
                    1.0 if env.can_play(card, card_instance) else 0.0,
                    env.estimate_card_damage(card_instance, enemy.creature) / 50.0,
                ]
            )
        return np.asarray(features, dtype=np.float32)


class IroncladSeapunkPPOEnv(FixedFightPPOEnv):
    def __init__(self, **kwargs) -> None:
        super().__init__(scenario="ironclad_seapunk_42", **kwargs)
