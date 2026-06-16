r"""
#   让模型打一场随机战斗，并把每一步操作、出牌、伤害、格挡、敌人行动都保存成详细日志。
#
# 常用运行：
#   python trace_battle_ppo.py --stage all --seed 123
#
# 换种子看另一局：
#   python trace_battle_ppo.py --stage elite --seed 456
#
# 输出：
#   默认保存到 D:\SLS2\battle_ai_reports\trace_generic_battle.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a detailed battle trace for a generic PPO model.")
    parser.add_argument("--model-path", default="battle_ai_models/ppo_generic_battle.zip")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument(
        "--stage",
        choices=["weak", "regular", "elite", "boss", "all"],
        default="all",
    )
    parser.add_argument("--output", default="battle_ai_reports/trace_generic_battle.txt")
    parser.add_argument("--stochastic", action="store_true", help="Sample from the policy instead of taking its best action.")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    env = GenericBattlePPOEnv(seed=args.seed, stage=args.stage)
    model = MaskablePPO.load(args.model_path, env=env, device="auto")

    obs, _ = env.reset(seed=args.seed)
    lines = [env.scenario_summary(), ""]
    done = False
    info = {}
    step_index = 0
    while not done:
        action, _ = model.predict(obs, deterministic=not args.stochastic, action_masks=env.action_masks())
        lines.append(f"Step {step_index}: {env.describe_action(int(action))}")
        before_len = len(env.env.log)
        obs, reward, terminated, truncated, info = env.step(int(action))
        for entry in env.env.log[before_len:]:
            lines.append(f"  {entry}")
        lines.append(f"  reward={reward:.3f}, hp={env.env.player.hp}/{env.env.player.max_hp}, block={env.env.player.block}")
        lines.append("")
        done = terminated or truncated
        step_index += 1

    result = info["result"]
    lines.append(f"Result: won={result.won}, hp_lost={result.hp_lost}, final_hp={result.final_hp}, turns={result.turns}")
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved trace: {output}")
    print(lines[-1])


if __name__ == "__main__":
    main()
