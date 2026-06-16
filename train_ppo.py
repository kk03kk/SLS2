r"""
训练“战斗内模型”。模型只负责一场战斗里怎么出牌、打哪个目标、什么时候结束回合。
#
# 常用运行：
#   python train_battle_ppo.py --timesteps 1000000 --stage all --resume
#
# stage 包含 5 类：
#   weak     弱怪
#   regular  普通怪
#   elite    精英
#   boss     Boss
#   all      上面全部混合
#
# 常用参数：
#   --resume                  继续训练已有模型
#   --min-bonus-cards 5       每局卡组至少额外加 5 张随机牌
#   --max-bonus-cards 10      每局卡组最多额外加 10 张随机牌
#   --tensorboard-log 路径    给这次训练单独保存曲线日志
#
# 默认模型保存到：
#   D:\SLS2\battle_ai_models\ppo_generic_battle.zip
"""
from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a generic battle-only Maskable PPO model.")
    parser.add_argument("--timesteps", type=int, default=500_000)
    parser.add_argument("--model-path", default="battle_ai_models/ppo_generic_battle.zip")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument(
        "--stage",
        choices=["weak", "regular", "elite", "boss", "all"],
        default="all",
    )
    parser.add_argument("--min-bonus-cards", type=int, default=3)
    parser.add_argument("--max-bonus-cards", type=int, default=15)
    parser.add_argument("--max-turns", type=int, default=60)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tensorboard-log", default="battle_ai_runs/generic_battle")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    Path(args.tensorboard_log).mkdir(parents=True, exist_ok=True)

    env = GenericBattlePPOEnv(
        seed=args.seed,
        stage=args.stage,
        max_turns=args.max_turns,
        min_bonus_cards=args.min_bonus_cards,
        max_bonus_cards=args.max_bonus_cards,
    )

    if args.resume and model_path.exists():
        print(f"Resume model: {model_path}")
        model = MaskablePPO.load(model_path, env=env, device=args.device)
        reset_num_timesteps = False
    else:
        print(f"Train new model: {model_path}")
        model = MaskablePPO(
            "MlpPolicy",
            env,
            seed=args.seed,
            verbose=1,
            device=args.device,
            tensorboard_log=args.tensorboard_log,
            n_steps=2048,
            batch_size=512,
            n_epochs=8,
            gamma=0.985,
            gae_lambda=0.95,
            learning_rate=3e-4,
            ent_coef=0.015,
            clip_range=0.2,
        )
        reset_num_timesteps = True

    try:
        model.learn(
            total_timesteps=args.timesteps,
            reset_num_timesteps=reset_num_timesteps,
            tb_log_name="maskable_ppo",
            progress_bar=True,
        )
    except KeyboardInterrupt:
        model.save(model_path)
        print(f"Interrupted. Saved model: {model_path}")
        raise

    model.save(model_path)
    print(f"Saved model: {model_path}")


if __name__ == "__main__":
    main()
