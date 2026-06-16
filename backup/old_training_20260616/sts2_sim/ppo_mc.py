from __future__ import annotations

import copy
from dataclasses import dataclass

from sb3_contrib import MaskablePPO

from sts2_sim.ppo_env import FixedFightPPOEnv


@dataclass(frozen=True)
class MonteCarloActionScore:
    action: int
    average_score: float
    best_score: float
    worst_score: float
    rollouts: int


def select_action_with_monte_carlo(
    env: FixedFightPPOEnv,
    model: MaskablePPO,
    *,
    rollouts: int = 16,
    max_depth: int = 80,
    rollout_deterministic: bool = False,
) -> tuple[int, list[MonteCarloActionScore]]:
    legal_actions = [idx for idx, allowed in enumerate(env.action_masks()) if allowed]
    scored: list[MonteCarloActionScore] = []

    for action in legal_actions:
        scores = [
            _score_candidate_action(
                env,
                model,
                action,
                max_depth=max_depth,
                rollout_deterministic=rollout_deterministic,
            )
            for _ in range(max(1, rollouts))
        ]
        scored.append(
            MonteCarloActionScore(
                action=action,
                average_score=sum(scores) / len(scores),
                best_score=max(scores),
                worst_score=min(scores),
                rollouts=len(scores),
            )
        )

    scored.sort(key=lambda item: item.average_score, reverse=True)
    return scored[0].action, scored


def _score_candidate_action(
    env: FixedFightPPOEnv,
    model: MaskablePPO,
    action: int,
    *,
    max_depth: int,
    rollout_deterministic: bool,
) -> float:
    clone = copy.deepcopy(env)
    obs, _, terminated, truncated, info = clone.step(action)
    done = terminated or truncated
    depth = 0

    while not done and depth < max_depth:
        next_action, _ = model.predict(
            obs,
            deterministic=rollout_deterministic,
            action_masks=clone.action_masks(),
        )
        obs, _, terminated, truncated, info = clone.step(int(next_action))
        done = terminated or truncated
        depth += 1

    return _utility(clone, info if done else None)


def _utility(env: FixedFightPPOEnv, info: dict | None) -> float:
    combat = env.env
    enemy_hp = sum(enemy.creature.hp for enemy in combat.enemies if enemy.alive)
    enemy_block = sum(enemy.creature.block for enemy in combat.enemies if enemy.alive)
    player_block = combat.player.block
    player_strength = combat.player.power_amount("strength")

    if info and info.get("result") is not None:
        result = info["result"]
        if result.won:
            return 1000.0 + result.final_hp * 10.0 - result.turns
        return (
            -1000.0
            + (combat.player.hp * 12.0)
            + player_block * 0.5
            + (combat.player.max_hp - enemy_hp) * 2.5
            + player_strength * 8.0
            - enemy_block * 2.0
            - result.turns
        )

    return (
        combat.player.hp * 10.0
        + player_block * 0.5
        + player_strength * 8.0
        - enemy_hp * 8.0
        - enemy_block * 2.0
        - combat.turn
    )
