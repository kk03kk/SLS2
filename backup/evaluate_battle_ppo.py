r"""
#   批量测试战斗内模型强不强。它会随机生成指定 stage 的战斗，统计胜率、平均战损、平均回合数。
#
# 常用运行：
#   conda activate DL
#   cd D:\SLS2
#   python evaluate_battle_ppo.py --episodes 500 --stage all
#
# 只测某一类：
#   python evaluate_battle_ppo.py --episodes 500 --stage weak
#   python evaluate_battle_ppo.py --episodes 500 --stage regular
#   python evaluate_battle_ppo.py --episodes 300 --stage elite
#   python evaluate_battle_ppo.py --episodes 300 --stage boss
#
# 输出：
#   默认保存到 D:\SLS2\battle_ai_reports\eval_generic_battle.csv
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a generic battle-only PPO model.")
    parser.add_argument("--model-path", default="battle_ai_models/ppo_generic_battle.zip")
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--seed", type=int, default=100_000)
    parser.add_argument(
        "--stage",
        choices=["weak", "regular", "elite", "boss", "all"],
        default="all",
    )
    parser.add_argument("--stochastic", action="store_true", help="Sample from the policy instead of taking its best action.")
    parser.add_argument("--output", default="battle_ai_reports/eval_generic_battle.csv")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    env = GenericBattlePPOEnv(seed=args.seed, stage=args.stage)
    model = MaskablePPO.load(args.model_path, env=env, device="auto")

    rows = []
    by_stage = defaultdict(lambda: {"n": 0, "wins": 0, "hp_lost": 0, "turns": 0})
    for idx in range(args.episodes):
        obs, _ = env.reset(seed=args.seed + idx)
        done = False
        info = {}
        while not done:
            action, _ = model.predict(obs, deterministic=not args.stochastic, action_masks=env.action_masks())
            obs, _, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
        result = info["result"]
        scenario = env.scenario
        row = {
            "episode": idx,
            "stage": scenario.stage,
            "encounter": scenario.encounter_id,
            "won": int(result.won),
            "hp_lost": result.hp_lost,
            "final_hp": result.final_hp,
            "turns": result.turns,
            "deck_size": len(scenario.deck),
        }
        rows.append(row)
        bucket = by_stage[scenario.stage]
        bucket["n"] += 1
        bucket["wins"] += int(result.won)
        bucket["hp_lost"] += result.hp_lost
        bucket["turns"] += result.turns

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    wins = sum(row["won"] for row in rows)
    avg_hp = sum(row["hp_lost"] for row in rows) / max(1, len(rows))
    avg_turns = sum(row["turns"] for row in rows) / max(1, len(rows))
    print(f"Episodes: {len(rows)}")
    print(f"Win rate: {wins / max(1, len(rows)):.1%}")
    print(f"Average hp lost: {avg_hp:.2f}")
    print(f"Average turns: {avg_turns:.2f}")
    print("By stage:")
    for stage, stats in sorted(by_stage.items()):
        n = stats["n"]
        print(
            f"  {stage}: win={stats['wins'] / max(1, n):.1%}, "
            f"avg_hp_lost={stats['hp_lost'] / max(1, n):.2f}, avg_turns={stats['turns'] / max(1, n):.2f}, n={n}"
        )
    print(f"Saved csv: {output}")


if __name__ == "__main__":
    main()
