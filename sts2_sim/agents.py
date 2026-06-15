from __future__ import annotations

import random

from sts2_sim.engine import END_TURN, CombatEnv


class RandomAgent:
    def __init__(self, seed: int | None = None, end_turn_chance: float = 0.0) -> None:
        self.rng = random.Random(seed)
        self.end_turn_chance = end_turn_chance

    def choose_action(self, env: CombatEnv) -> tuple[int, int | None]:
        actions = env.legal_actions()
        playable = [action for action in actions if action != END_TURN]
        if not playable:
            return END_TURN
        if self.end_turn_chance > 0 and self.rng.random() < self.end_turn_chance:
            return END_TURN
        return self.rng.choice(playable)


class SimpleAttackAgent:
    """Small baseline: attack lowest-HP enemies first, otherwise play defenses."""

    def choose_action(self, env: CombatEnv) -> tuple[int, int | None]:
        playable = [action for action in env.legal_actions() if action != END_TURN]
        if not playable:
            return END_TURN
        attack_actions = [
            action for action in playable
            if env.hand[action[0]].def_id in {"strike_ironclad", "strike_ironclad_plus", "bash", "bash_plus"}
        ]
        if attack_actions:
            return min(
                attack_actions,
                key=lambda action: env.enemies[action[1]].creature.hp if action[1] is not None else 999,
            )
        return playable[0]
