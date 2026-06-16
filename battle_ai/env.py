from __future__ import annotations

import random
from dataclasses import dataclass

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from battle_ai.samplers import all_battle_card_ids, sample_battle_scenario
from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.data import CardDef, CardInstance, Creature, EnemyMove
from sts2_sim.engine import END_TURN, Action, CombatEnv


MAX_ENEMIES = 8
MAX_CHOICES = 120
CARD_IDS = all_battle_card_ids()
CARD_INDEX = {card_id: idx for idx, card_id in enumerate(CARD_IDS)}
CARD_FEATURES = 10 + len(CARD_IDS)
ENEMY_FEATURES = 22
GLOBAL_FEATURES = 32
PILE_HISTOGRAMS = 3 * len(CARD_IDS)
OBS_SIZE = GLOBAL_FEATURES + MAX_ENEMIES * ENEMY_FEATURES + CombatEnv.max_hand_size * CARD_FEATURES + PILE_HISTOGRAMS


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


def build_action_catalog() -> tuple[ActionSpec, ...]:
    specs = [ActionSpec(-1, None, None)]
    choice_values: list[int | None] = [None] + list(range(MAX_CHOICES))
    target_values: list[int | None] = [None] + list(range(MAX_ENEMIES))
    for hand_index in range(CombatEnv.max_hand_size):
        for target_index in target_values:
            for choice_index in choice_values:
                specs.append(ActionSpec(hand_index, target_index, choice_index))
    return tuple(specs)


class GenericBattlePPOEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(
        self,
        *,
        seed: int | None = None,
        stage: str = "auto",
        max_turns: int = 60,
        min_bonus_cards: int = 0,
        max_bonus_cards: int = 15,
        enable_burning_blood: bool = False,
    ) -> None:
        super().__init__()
        self.base_seed = seed
        self.rng = random.Random(seed)
        self.stage = stage
        self.max_turns = max_turns
        self.min_bonus_cards = min_bonus_cards
        self.max_bonus_cards = max_bonus_cards
        self.enable_burning_blood = enable_burning_blood
        self.episode_index = 0
        self.action_catalog = build_action_catalog()
        self.action_to_index = {spec.to_engine_action(): idx for idx, spec in enumerate(self.action_catalog)}
        self.action_space = spaces.Discrete(len(self.action_catalog))
        self.observation_space = spaces.Box(low=-20.0, high=20.0, shape=(OBS_SIZE,), dtype=np.float32)
        self.scenario = None
        self.env: CombatEnv
        self.initial_enemy_hp = 1
        self._last_result = None
        self._new_episode(seed)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is None and self.base_seed is not None:
            seed = self.base_seed + self.episode_index
        self._new_episode(seed)
        self.episode_index += 1
        return self._obs(), {}

    def step(self, action: int):
        action = int(action)
        if action < 0 or action >= len(self.action_catalog) or not self.action_masks()[action]:
            action = 0

        before_enemy_hp = self._enemy_hp_total(capped=True)
        before_player_hp = self.env.player.hp
        _, _, done, info = self.env.step(self.action_catalog[action].to_engine_action())
        after_enemy_hp = self._enemy_hp_total(capped=True)
        after_player_hp = self.env.player.hp

        damage_dealt = max(0, before_enemy_hp - after_enemy_hp)
        hp_lost = max(0, before_player_hp - after_player_hp)
        reward = damage_dealt * 0.015 - hp_lost * 0.25 - 0.003

        if done:
            result = info["result"]
            self._last_result = result
            if result.won:
                reward += 80.0 + result.final_hp * 0.8 - result.hp_lost * 1.7 - result.turns * 0.12
            else:
                progress = 1.0 - (after_enemy_hp / max(1, self.initial_enemy_hp))
                reward += -75.0 + progress * 45.0 - result.hp_lost * 0.35

        terminated = self.env.player.hp <= 0 or not self.env._combat_relevant_enemies_alive()
        truncated = done and not terminated
        return self._obs(), float(reward), terminated, truncated, info

    def action_masks(self) -> np.ndarray:
        mask = np.zeros(len(self.action_catalog), dtype=bool)
        for action in self.env.legal_actions():
            idx = self.action_to_index.get(action)
            if idx is not None:
                mask[idx] = True
        if not mask.any():
            mask[0] = True
        return mask

    def describe_action(self, action_index: int) -> str:
        spec = self.action_catalog[int(action_index)]
        if spec.hand_index < 0:
            return "end turn"
        if spec.hand_index >= len(self.env.hand):
            return "invalid action"
        card_instance = self.env.hand[spec.hand_index]
        card = CARD_LIBRARY[card_instance.def_id]
        parts = [f"play hand[{spec.hand_index}] {card.name}"]
        if spec.target_index is not None and spec.target_index < len(self.env.enemies):
            target = self.env.enemies[spec.target_index].creature.name
            parts.append(f"target={target}")
        if spec.choice_index is not None:
            parts.append(f"choice={spec.choice_index}")
        return ", ".join(parts)

    def scenario_summary(self) -> str:
        if self.scenario is None:
            return ""
        enemy_names = ", ".join(enemy.name for enemy in self.scenario.enemies)
        deck_names = ", ".join(CARD_LIBRARY[card_id].name for card_id in self.scenario.deck)
        return (
            f"stage={self.scenario.stage}, encounter={self.scenario.encounter_id}, "
            f"hp={self.scenario.player_hp}/{self.scenario.player_max_hp}, enemies={enemy_names}, deck=[{deck_names}]"
        )

    def _new_episode(self, seed: int | None) -> None:
        if seed is not None:
            self.rng = random.Random(seed)
        self.scenario = sample_battle_scenario(
            self.rng,
            stage=self.stage,
            episode_index=self.episode_index,
            min_bonus_cards=self.min_bonus_cards,
            max_bonus_cards=self.max_bonus_cards,
        )
        self.env = CombatEnv(
            self.scenario.deck,
            self.scenario.enemies,
            player_hp=self.scenario.player_hp,
            player_max_hp=self.scenario.player_max_hp,
            seed=seed,
            max_turns=self.max_turns,
            enable_burning_blood=self.enable_burning_blood,
        )
        self.initial_enemy_hp = self._enemy_hp_total(capped=True)
        self._last_result = None

    def _enemy_hp_total(self, *, capped: bool) -> int:
        total = 0
        for enemy in self.env.enemies:
            if enemy.alive:
                hp = enemy.creature.hp
                if capped:
                    hp = min(hp, enemy.creature.max_hp, enemy.definition.max_hp)
                total += hp
        return total

    def _obs(self) -> np.ndarray:
        features: list[float] = []
        env = self.env
        player = env.player
        alive_count = sum(1 for enemy in env.enemies if enemy.alive)
        incoming = self._incoming_damage()
        features.extend(
            [
                player.hp / max(1, player.max_hp),
                player.max_hp / 100.0,
                player.block / 80.0,
                env.energy / 8.0,
                env.turn / max(1, env.max_turns),
                incoming / 80.0,
                alive_count / MAX_ENEMIES,
                len(env.hand) / CombatEnv.max_hand_size,
                len(env.draw_pile) / 40.0,
                len(env.discard_pile) / 40.0,
                len(env.exhaust_pile) / 40.0,
                player.power_amount("strength") / 20.0,
                player.power_amount("dexterity") / 20.0,
                player.power_amount("vulnerable") / 5.0,
                player.power_amount("weak") / 5.0,
                player.power_amount("frail") / 5.0,
                player.power_amount("barricade"),
                player.power_amount("corruption"),
                player.power_amount("feel_no_pain") / 10.0,
                player.power_amount("dark_embrace") / 10.0,
                player.power_amount("juggernaut") / 10.0,
                player.power_amount("rupture") / 10.0,
                player.power_amount("demon_form") / 10.0,
                player.power_amount("pyre") / 5.0,
                player.power_amount("no_draw"),
                player.power_amount("no_energy_gain"),
                player.power_amount("smoggy"),
                env.hp_lost_this_combat / 100.0,
                env.cards_exhausted_this_turn / 10.0,
                env.attacks_played_this_turn / 10.0,
                env.block_gains_this_turn / 10.0,
                self.initial_enemy_hp / 500.0,
            ]
        )

        for slot in range(MAX_ENEMIES):
            if slot >= len(env.enemies):
                features.extend([0.0] * ENEMY_FEATURES)
                continue
            enemy = env.enemies[slot]
            creature = enemy.creature
            move = env.current_enemy_move(enemy)
            move_damage = self._move_damage_hint(move)
            features.extend(
                [
                    1.0,
                    1.0 if enemy.alive else 0.0,
                    creature.hp / max(1, creature.max_hp),
                    creature.max_hp / 300.0,
                    creature.block / 80.0,
                    creature.power_amount("strength") / 30.0,
                    creature.power_amount("vulnerable") / 5.0,
                    creature.power_amount("weak") / 5.0,
                    creature.power_amount("frail") / 5.0,
                    creature.power_amount("ritual") / 10.0,
                    creature.power_amount("plating") / 20.0,
                    creature.power_amount("thorns") / 10.0,
                    creature.power_amount("artifact") / 5.0,
                    creature.power_amount("asleep") / 5.0,
                    creature.power_amount("minion"),
                    move_damage / 80.0,
                    move.hits / 8.0,
                    move.block / 80.0,
                    1.0 if move.apply_player_power else 0.0,
                    1.0 if move.apply_power else 0.0,
                    1.0 if move.summon else 0.0,
                    enemy.move_index / max(1, len(enemy.definition.moves)),
                ]
            )

        for slot in range(CombatEnv.max_hand_size):
            if slot >= len(env.hand):
                features.extend([0.0] * CARD_FEATURES)
                continue
            card_instance = env.hand[slot]
            features.extend(self._card_features(card_instance, env.enemies[0].creature if env.enemies else None))

        features.extend(self._pile_histogram(env.draw_pile))
        features.extend(self._pile_histogram(env.discard_pile))
        features.extend(self._pile_histogram(env.exhaust_pile))
        return np.asarray(features, dtype=np.float32)

    def _card_features(self, card_instance: CardInstance, target: Creature | None) -> list[float]:
        env = self.env
        card = CARD_LIBRARY[card_instance.def_id]
        one_hot = [0.0] * len(CARD_IDS)
        idx = CARD_INDEX.get(card_instance.def_id)
        if idx is not None:
            one_hot[idx] = 1.0
        base = [
            1.0,
            max(card.cost, 0) / 5.0,
            env.effective_cost(card, card_instance) / 5.0,
            1.0 if card.card_type == "attack" else 0.0,
            1.0 if card.card_type == "skill" else 0.0,
            1.0 if card.card_type == "power" else 0.0,
            1.0 if card.card_type in {"status", "curse"} else 0.0,
            1.0 if env.can_play(card, card_instance) else 0.0,
            env.estimate_card_damage(card_instance, target) / 100.0,
            self._rough_block(card) / 80.0,
        ]
        return base + one_hot

    def _pile_histogram(self, pile: list[CardInstance]) -> list[float]:
        counts = [0.0] * len(CARD_IDS)
        for card_instance in pile:
            idx = CARD_INDEX.get(card_instance.def_id)
            if idx is not None:
                counts[idx] += 1.0 / 10.0
        return counts

    def _rough_block(self, card: CardDef) -> int:
        total = 0
        for effect in card.effects:
            if effect.get("type") == "gain_block":
                total += int(effect.get("amount", 0))
        return total

    def _incoming_damage(self) -> int:
        total = 0
        for enemy in self.env.enemies:
            if not enemy.alive:
                continue
            move = self.env.current_enemy_move(enemy)
            total += self._move_damage_hint(move) * max(1, move.hits)
        return total

    def _move_damage_hint(self, move: EnemyMove) -> int:
        if move.id == "explode":
            for enemy in self.env.enemies:
                if self.env.current_enemy_move(enemy) == move:
                    return enemy.vars.get("steam_eruption_damage", move.damage)
        if move.id == "pressure_gun":
            for enemy in self.env.enemies:
                if self.env.current_enemy_move(enemy) == move:
                    return enemy.vars.get("pressure_gun_damage", move.damage)
        return move.damage

