from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

from sts2_sim.agents import RandomAgent
from sts2_sim.engine import CombatEnv, CombatResult


@dataclass(frozen=True)
class EvaluationSummary:
    runs: int
    win_rate: float
    avg_hp_lost: float
    avg_turns: float
    worst_10pct_hp_lost: float
    hp_lost_std: float


def run_combat(env: CombatEnv, agent, *, verbose: bool = False) -> CombatResult:
    done = False
    while not done:
        action = agent.choose_action(env)
        _, _, done, info = env.step(action)
    result = info["result"]
    if verbose:
        for line in result.log:
            print(line)
        print(f"Result: {'WIN' if result.won else 'LOSS'}, final HP {result.final_hp}, turns {result.turns}")
    return result


def evaluate(
    deck: list[str],
    enemy_defs: list,
    *,
    runs: int = 100,
    seed: int = 0,
    player_hp: int = 80,
) -> EvaluationSummary:
    results: list[CombatResult] = []
    for offset in range(runs):
        run_seed = seed + offset
        env = CombatEnv(deck, enemy_defs, seed=run_seed, player_hp=player_hp)
        agent = RandomAgent(seed=run_seed)
        results.append(run_combat(env, agent))
    hp_lost = [result.hp_lost for result in results]
    worst_count = max(1, runs // 10)
    worst = sorted(hp_lost, reverse=True)[:worst_count]
    return EvaluationSummary(
        runs=runs,
        win_rate=sum(1 for result in results if result.won) / runs,
        avg_hp_lost=mean(hp_lost),
        avg_turns=mean(result.turns for result in results),
        worst_10pct_hp_lost=mean(worst),
        hp_lost_std=pstdev(hp_lost) if len(hp_lost) > 1 else 0.0,
    )
