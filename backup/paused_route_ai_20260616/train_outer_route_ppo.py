from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from route_ai.env import BattleDelegatingRouteEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Train route-level PPO while delegating combats to a battle model.")
    parser.add_argument("--timesteps", type=int, default=200_000)
    parser.add_argument("--model-path", default="route_ai_models/ppo_outer_route.zip")
    parser.add_argument("--battle-model-path", default="battle_ai_models/ppo_generic_battle.zip")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tensorboard-log", default="route_ai_runs/outer_route")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    Path(args.tensorboard_log).mkdir(parents=True, exist_ok=True)

    env = BattleDelegatingRouteEnv(seed=args.seed, battle_model_path=args.battle_model_path)
    if args.resume and model_path.exists():
        print(f"Resume outer route model: {model_path}")
        model = MaskablePPO.load(model_path, env=env, device=args.device)
        reset_num_timesteps = False
    else:
        print(f"Train new outer route model: {model_path}")
        model = MaskablePPO(
            "MlpPolicy",
            env,
            seed=args.seed,
            verbose=1,
            device=args.device,
            tensorboard_log=args.tensorboard_log,
            n_steps=1024,
            batch_size=256,
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
        print(f"Interrupted. Saved model: {model_path}")
        return
    model.save(model_path)
    print(f"Saved model: {model_path}")


if __name__ == "__main__":
    main()

