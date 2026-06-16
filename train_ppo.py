from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train a generic battle-only Maskable PPO model.",
        epilog=(
            "Existing models are resumed by default. Use --fresh only when you intentionally "
            "want to start over and overwrite the model at the end."
        ),
    )
    parser.add_argument("--timesteps", type=int, default=500_000)
    parser.add_argument("--model-path", default="battle_ai_models/ppo_generic_battle.zip")
    parser.add_argument("--resume", action="store_true", help="Compatibility flag; resume is already the default.")
    parser.add_argument("--fresh", action="store_true", help="Start from scratch even if --model-path exists.")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument(
        "--stage",
        choices=["weak", "regular", "elite", "boss", "all"],
        default="all",
        help="Encounter curriculum used for sampling training battles.",
    )
    parser.add_argument("--min-bonus-cards", type=int, default=3)
    parser.add_argument("--max-bonus-cards", type=int, default=15)
    parser.add_argument("--max-turns", type=int, default=60)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tensorboard-log", default="battle_ai_runs/generic_battle")
    parser.add_argument("--n-steps", type=int, default=2048)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--n-epochs", type=int, default=8)
    parser.add_argument("--gamma", type=float, default=0.985)
    parser.add_argument("--gae-lambda", type=float, default=0.95)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--ent-coef", type=float, default=0.015)
    parser.add_argument("--clip-range", type=float, default=0.2)
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.timesteps <= 0:
        raise ValueError("--timesteps must be positive")
    if args.max_turns <= 0:
        raise ValueError("--max-turns must be positive")
    if args.min_bonus_cards < 0 or args.max_bonus_cards < 0:
        raise ValueError("bonus card counts must be non-negative")
    if args.min_bonus_cards > args.max_bonus_cards:
        raise ValueError("--min-bonus-cards cannot be greater than --max-bonus-cards")
    if args.n_steps <= 0:
        raise ValueError("--n-steps must be positive")
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be positive")
    if args.batch_size > args.n_steps:
        raise ValueError("--batch-size should not be greater than --n-steps for a single-env PPO run")
    if args.n_epochs <= 0:
        raise ValueError("--n-epochs must be positive")
    if not 0 < args.gamma <= 1:
        raise ValueError("--gamma must be in (0, 1]")
    if not 0 < args.gae_lambda <= 1:
        raise ValueError("--gae-lambda must be in (0, 1]")
    if args.learning_rate <= 0:
        raise ValueError("--learning-rate must be positive")
    if args.ent_coef < 0:
        raise ValueError("--ent-coef must be non-negative")
    if args.clip_range <= 0:
        raise ValueError("--clip-range must be positive")


def main() -> None:
    args = build_parser().parse_args()
    validate_args(args)

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
    print(
        "Training setup: "
        f"stage={args.stage}, timesteps={args.timesteps}, seed={args.seed}, "
        f"bonus_cards={args.min_bonus_cards}-{args.max_bonus_cards}, max_turns={args.max_turns}"
    )
    print(
        "PPO setup: "
        f"n_steps={args.n_steps}, batch_size={args.batch_size}, n_epochs={args.n_epochs}, "
        f"gamma={args.gamma}, gae_lambda={args.gae_lambda}, lr={args.learning_rate}, "
        f"ent_coef={args.ent_coef}, clip_range={args.clip_range}"
    )

    if model_path.exists() and not args.fresh:
        print(f"Resume existing model: {model_path}")
        model = MaskablePPO.load(
            model_path,
            env=env,
            device=args.device,
            tensorboard_log=args.tensorboard_log,
        )
        reset_num_timesteps = False
    else:
        if model_path.exists() and args.fresh:
            print(f"Fresh training requested. Existing model will be overwritten when training finishes: {model_path}")
        else:
            print(f"No existing model found. Train new model: {model_path}")
        model = MaskablePPO(
            "MlpPolicy",
            env,
            seed=args.seed,
            verbose=1,
            device=args.device,
            tensorboard_log=args.tensorboard_log,
            n_steps=args.n_steps,
            batch_size=args.batch_size,
            n_epochs=args.n_epochs,
            gamma=args.gamma,
            gae_lambda=args.gae_lambda,
            learning_rate=args.learning_rate,
            ent_coef=args.ent_coef,
            clip_range=args.clip_range,
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
