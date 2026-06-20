from __future__ import annotations

import argparse
from pathlib import Path

from .combat_env import CombatConfig, SlS2CombatEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PPO/MaskablePPO on simplified STS2 combat.")
    parser.add_argument("--stage", choices=["01", "02", "03", "04"], default="01")
    parser.add_argument("--algo", choices=["ppo", "maskableppo"], default="maskableppo")
    parser.add_argument("--timesteps", type=int, default=50_000)
    parser.add_argument("--out", default="runs/combat_model")
    parser.add_argument("--seed", type=int, default=1)
    return parser.parse_args()


def config_for_stage(stage: str, seed: int) -> CombatConfig:
    if stage == "01":
        return CombatConfig(encounter_pool="weak", random_extra_cards=(0, 0), seed=seed)
    if stage == "02":
        return CombatConfig(encounter_pool="weak", random_extra_cards=(1, 1), seed=seed)
    if stage == "03":
        return CombatConfig(encounter_pool="strong", random_extra_cards=(3, 5), seed=seed)
    return CombatConfig(encounter_pool="elite", random_extra_cards=(5, 10), seed=seed)


def main() -> None:
    args = parse_args()
    env = SlS2CombatEnv(config_for_stage(args.stage, args.seed))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    if args.algo == "maskableppo":
        from sb3_contrib import MaskablePPO

        model = MaskablePPO("MlpPolicy", env, verbose=1, seed=args.seed)
    else:
        from stable_baselines3 import PPO

        model = PPO("MlpPolicy", env, verbose=1, seed=args.seed)
    model.learn(total_timesteps=args.timesteps)
    model.save(args.out)
    print(f"saved model to {args.out}")


if __name__ == "__main__":
    main()

