from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from sts2_sim.route_env import UnderdocksRoutePPOEnv


def evaluate_model(model: MaskablePPO, *, episodes: int, seed: int) -> tuple[float, float, float, float]:
    wins = 0
    hp_lost: list[int] = []
    combats_won: list[int] = []
    final_hp: list[int] = []
    for offset in range(episodes):
        env = UnderdocksRoutePPOEnv(seed=seed + offset)
        obs, _ = env.reset()
        done = False
        info = {}
        while not done:
            action, _ = model.predict(obs, deterministic=True, action_masks=env.action_masks())
            obs, _, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
        result = info["result"]
        wins += int(result.won)
        hp_lost.append(result.total_hp_lost)
        combats_won.append(result.combats_won)
        final_hp.append(result.final_hp)
    return (
        wins / max(1, episodes),
        sum(hp_lost) / max(1, len(hp_lost)),
        sum(combats_won) / max(1, len(combats_won)),
        sum(final_hp) / max(1, len(final_hp)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train MaskablePPO on the Underdocks act route.")
    parser.add_argument("--timesteps", type=int, default=300_000)
    parser.add_argument("--model-path", default="models/ppo_underdocks_route_a0.zip")
    parser.add_argument("--resume", action="store_true", help="Continue training from --model-path if it exists.")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--eval-episodes", type=int, default=100)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tensorboard-log", default="runs/ppo_underdocks_route_a0")
    parser.add_argument(
        "--no-burning-blood",
        action="store_true",
        help="Disable Ironclad starter relic healing. Default keeps it enabled.",
    )
    args = parser.parse_args()

    model_path = Path(args.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    Path(args.tensorboard_log).mkdir(parents=True, exist_ok=True)

    env = UnderdocksRoutePPOEnv(
        seed=args.seed,
        enable_burning_blood=not args.no_burning_blood,
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
            gamma=0.995,
            gae_lambda=0.95,
            learning_rate=3e-4,
            ent_coef=0.03,
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
        print(f"Training interrupted. Saved current model: {model_path}")
        return
    model.save(model_path)
    print(f"Saved model: {model_path}")

    win_rate, avg_hp_lost, avg_combats_won, avg_final_hp = evaluate_model(
        model,
        episodes=args.eval_episodes,
        seed=args.seed + 1_000_000,
    )
    print(f"Eval episodes: {args.eval_episodes}")
    print(f"Win rate: {win_rate:.1%}")
    print(f"Average total HP loss: {avg_hp_lost:.2f}")
    print(f"Average combats won: {avg_combats_won:.2f}/7")
    print(f"Average final HP: {avg_final_hp:.2f}")


if __name__ == "__main__":
    main()
