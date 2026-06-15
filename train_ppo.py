from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from sts2_sim.ppo_env import FixedFightPPOEnv
from sts2_sim.scenarios import SCENARIO_BUILDERS


def evaluate_model(model: MaskablePPO, *, scenario: str, episodes: int, seed: int) -> tuple[float, float, float]:
    wins = 0
    hp_lost: list[int] = []
    turns: list[int] = []
    for offset in range(episodes):
        env = FixedFightPPOEnv(scenario=scenario, seed=seed + offset)
        obs, _ = env.reset()
        done = False
        info = {}
        while not done:
            action, _ = model.predict(obs, deterministic=True, action_masks=env.action_masks())
            obs, _, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
        result = info["result"]
        wins += int(result.won)
        hp_lost.append(result.hp_lost)
        turns.append(result.turns)
    return (
        wins / max(1, episodes),
        sum(hp_lost) / max(1, len(hp_lost)),
        sum(turns) / max(1, len(turns)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train MaskablePPO on a fixed STS2 fight.")
    parser.add_argument("--scenario", choices=sorted(SCENARIO_BUILDERS), default="ironclad_seapunk_42")
    parser.add_argument("--timesteps", type=int, default=100_000)
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--resume", action="store_true", help="Continue training from --model-path if it exists.")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--eval-episodes", type=int, default=100)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tensorboard-log", default=None)
    args = parser.parse_args()

    model_path = Path(args.model_path or f"models/ppo_{args.scenario}.zip")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    tensorboard_log = args.tensorboard_log or f"runs/ppo_{args.scenario}"
    Path(tensorboard_log).mkdir(parents=True, exist_ok=True)

    env = FixedFightPPOEnv(scenario=args.scenario, seed=args.seed)

    if args.resume and model_path.exists():
        print(f"继续训练已有模型: {model_path}")
        model = MaskablePPO.load(model_path, env=env, device=args.device)
        reset_num_timesteps = False
    else:
        print(f"开始训练新模型: {model_path}")
        model = MaskablePPO(
            "MlpPolicy",
            env,
            seed=args.seed,
            verbose=1,
            device=args.device,
            tensorboard_log=tensorboard_log,
            n_steps=1024,
            batch_size=256,
            n_epochs=8,
            gamma=0.98,
            gae_lambda=0.95,
            learning_rate=3e-4,
            ent_coef=0.02,
            clip_range=0.2,
        )
        reset_num_timesteps = True

    model.learn(
        total_timesteps=args.timesteps,
        reset_num_timesteps=reset_num_timesteps,
        tb_log_name="maskable_ppo",
        progress_bar=True,
    )
    model.save(model_path)
    print(f"模型已保存: {model_path}")

    win_rate, avg_hp_lost, avg_turns = evaluate_model(
        model,
        scenario=args.scenario,
        episodes=args.eval_episodes,
        seed=args.seed + 1_000_000,
    )
    print(f"评估局数: {args.eval_episodes}")
    print(f"胜率: {win_rate:.1%}")
    print(f"平均战损: {avg_hp_lost:.2f}")
    print(f"平均回合: {avg_turns:.2f}")


if __name__ == "__main__":
    main()
