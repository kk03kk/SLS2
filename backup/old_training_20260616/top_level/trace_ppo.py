from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.ppo_mc import select_action_with_monte_carlo
from sts2_sim.ppo_env import FixedFightPPOEnv
from sts2_sim.scenarios import SCENARIO_BUILDERS


def names(pile) -> list[str]:
    return [CARD_LIBRARY[card.def_id].name for card in pile]


def print_state(env: FixedFightPPOEnv) -> None:
    combat = env.env
    enemy = combat.enemies[0]
    move = combat.current_enemy_move(enemy)
    print(
        f"回合 {combat.turn} | 玩家 HP {combat.player.hp}/{combat.player.max_hp} "
        f"格挡 {combat.player.block} 能量 {combat.energy} 力量 {combat.player.power_amount('strength')}"
    )
    print(
        f"敌人 {enemy.creature.name} HP {enemy.creature.hp}/{enemy.creature.max_hp} "
        f"格挡 {enemy.creature.block} 力量 {enemy.creature.power_amount('strength')} "
        f"易伤 {enemy.creature.power_amount('vulnerable')} | 意图 {move.intent}"
    )
    print(f"手牌: {names(combat.hand)}")
    print(f"抽牌堆 {len(combat.draw_pile)} | 弃牌堆: {names(combat.discard_pile)} | 消耗堆: {names(combat.exhaust_pile)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Show every decision made by a trained PPO model.")
    parser.add_argument("--scenario", choices=sorted(SCENARIO_BUILDERS), default="ironclad_seapunk_42")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--extra-card", default=None, help="Fix the bonus card for scenarios that support it.")
    parser.add_argument("--deterministic", action="store_true", default=True)
    parser.add_argument("--mc-rollouts", type=int, default=0, help="Rollouts per legal action. 0 means pure PPO.")
    parser.add_argument("--mc-depth", type=int, default=80, help="Maximum simulated future steps per rollout.")
    parser.add_argument("--mc-deterministic", action="store_true", help="Use deterministic PPO during MC rollouts.")
    parser.add_argument("--mc-show", type=int, default=5, help="How many MC candidate scores to print.")
    args = parser.parse_args()

    model_path = Path(args.model_path or f"models/ppo_{args.scenario}.zip")
    if not model_path.exists():
        raise FileNotFoundError(f"找不到模型: {model_path}")

    env = FixedFightPPOEnv(scenario=args.scenario, seed=args.seed, extra_card_id=args.extra_card)
    model = MaskablePPO.load(model_path, device="auto")
    obs, _ = env.reset()
    done = False
    step_no = 0
    last_log_len = len(env.env.log)

    while not done:
        step_no += 1
        print("=" * 72)
        print_state(env)
        if args.mc_rollouts > 0:
            action, scores = select_action_with_monte_carlo(
                env,
                model,
                rollouts=args.mc_rollouts,
                max_depth=args.mc_depth,
                rollout_deterministic=args.mc_deterministic,
            )
            print(f"蒙特卡洛候选估分，rollouts={args.mc_rollouts}:")
            for score in scores[: max(1, args.mc_show)]:
                print(
                    f"  {env.describe_action(score.action)} | "
                    f"平均 {score.average_score:.2f} "
                    f"最好 {score.best_score:.2f} "
                    f"最差 {score.worst_score:.2f}"
                )
        else:
            action, _ = model.predict(obs, deterministic=args.deterministic, action_masks=env.action_masks())
            action = int(action)
        print(f"AI 第 {step_no} 步选择: {env.describe_action(action)}")
        obs, reward, terminated, truncated, info = env.step(action)
        new_logs = env.env.log[last_log_len:]
        last_log_len = len(env.env.log)
        for line in new_logs:
            print(f"  {line}")
        print(f"本步奖励: {reward:.3f}")
        done = terminated or truncated

    result = info["result"]
    print("=" * 72)
    print(f"结果: {'胜利' if result.won else '失败'} | 最终 HP {result.final_hp} | 战损 {result.hp_lost} | 回合 {result.turns}")


if __name__ == "__main__":
    main()
