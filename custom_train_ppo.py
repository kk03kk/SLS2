from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean

from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv
from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.engine import CombatEnv
from sts2_sim.enemies import ENCOUNTERS, ENEMY_LIBRARY


# =========================
MODEL_PATH = "battle_ai_models/ppo_generic_battle.zip"
TENSORBOARD_LOG = "battle_ai_runs/custom_battle"
SEED = 6
PLAYER_HP = 80
PLAYER_MAX_HP = 80
MAX_TURNS = 100

ENCOUNTER_ID = "seapunk_weak"

DECK = [
    "strike_ironclad",
    "strike_ironclad",
    "strike_ironclad",
    "strike_ironclad",
    "body_slam",
    "stomp",
    "defend_ironclad",
    "defend_ironclad",
    "defend_ironclad",
    "bash",
]
# =========================


class CustomBattleTrainingEnv(GenericBattlePPOEnv):
    def __init__(
        self,
        *,
        seed: int | None = None,
        deck: list[str] | None = None,
        encounter_id: str = ENCOUNTER_ID,
        player_hp: int = PLAYER_HP,
        player_max_hp: int = PLAYER_MAX_HP,
        max_turns: int = MAX_TURNS,
    ) -> None:
        self.custom_deck = list(DECK if deck is None else deck)
        self.custom_encounter_id = encounter_id
        self.player_hp = player_hp
        self.player_max_hp = player_max_hp
        super().__init__(
            seed=seed,
            stage="weak",
            max_turns=max_turns,
            min_bonus_cards=0,
            max_bonus_cards=0,
        )

    def _new_episode(self, seed: int | None) -> None:
        if self.custom_encounter_id not in ENCOUNTERS:
            raise ValueError(f"Unknown encounter id: {self.custom_encounter_id}")
        for card_id in self.custom_deck:
            if card_id not in CARD_LIBRARY:
                raise ValueError(f"Unknown card id: {card_id}")

        enemy_ids = ENCOUNTERS[self.custom_encounter_id]
        enemies = [ENEMY_LIBRARY[enemy_id] for enemy_id in enemy_ids]
        self.scenario = None
        self.env = CombatEnv(
            list(self.custom_deck),
            enemies,
            player_hp=self.player_hp,
            player_max_hp=self.player_max_hp,
            seed=seed,
            max_turns=self.max_turns,
            enable_burning_blood=False,
        )
        self.initial_enemy_hp = self._enemy_hp_total(capped=True)
        self._last_result = None

    def step(self, action: int):
        obs, reward, terminated, truncated, info = super().step(action)
        result = info.get("result")
        if result is not None:
            if result.won:
                reward += max(0, 50 - result.hp_lost * 2)
            else:
                reward -= 100.0
        return obs, reward, terminated, truncated, info


def evaluate(model: MaskablePPO, *, episodes: int, seed: int, env_kwargs: dict) -> None:
    wins = 0
    hp_lost = []
    turns = []
    for idx in range(episodes):
        env = CustomBattleTrainingEnv(seed=seed + idx, **env_kwargs)
        obs, _ = env.reset(seed=seed + idx)
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

    print(f"Eval episodes: {episodes}")
    print(f"Win rate: {wins / max(1, episodes):.1%}")
    print(f"Average hp lost: {mean(hp_lost):.2f}")
    print(f"Best hp lost: {min(hp_lost)}")
    print(f"Worst hp lost: {max(hp_lost)}")
    print(f"Average turns: {mean(turns):.2f}")


def validate_setup(deck: list[str], encounter_id: str, player_hp: int, player_max_hp: int, max_turns: int) -> None:
    if encounter_id not in ENCOUNTERS:
        raise ValueError(f"Unknown encounter id: {encounter_id}")
    for card_id in deck:
        if card_id not in CARD_LIBRARY:
            raise ValueError(f"Unknown card id: {card_id}")
    if player_hp <= 0 or player_max_hp <= 0:
        raise ValueError("player HP values must be positive")
    if player_hp > player_max_hp:
        raise ValueError("--player-hp cannot be greater than --player-max-hp")
    if max_turns <= 0:
        raise ValueError("--max-turns must be positive")


def add_ppo_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--n-steps", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--n-epochs", type=int, default=8)
    parser.add_argument("--gamma", type=float, default=0.98)
    parser.add_argument("--gae-lambda", type=float, default=0.95)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--ent-coef", type=float, default=0.01)
    parser.add_argument("--clip-range", type=float, default=0.15)


def validate_ppo_args(args: argparse.Namespace) -> None:
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
    parser = argparse.ArgumentParser(
        description="Fine-tune the battle model on a custom official encounter.",
        epilog=(
            "Existing models are resumed by default. Use --fresh only when you intentionally "
            "want to start over and overwrite the model at the end."
        ),
    )
    parser.add_argument("--timesteps", type=int, default=50_000)
    parser.add_argument("--model-path", default=MODEL_PATH)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tensorboard-log", default=TENSORBOARD_LOG)
    parser.add_argument("--eval-episodes", type=int, default=50)
    parser.add_argument("--encounter-id", default=ENCOUNTER_ID)
    parser.add_argument("--player-hp", type=int, default=PLAYER_HP)
    parser.add_argument("--player-max-hp", type=int, default=PLAYER_MAX_HP)
    parser.add_argument("--max-turns", type=int, default=MAX_TURNS)
    parser.add_argument("--fresh", action="store_true", help="Ignore an existing model and train from scratch.")
    parser.add_argument("--resume", action="store_true", help="Kept for compatibility; resume is already the default.")
    add_ppo_args(parser)
    args = parser.parse_args()
    if args.timesteps <= 0:
        raise ValueError("--timesteps must be positive")
    if args.eval_episodes <= 0:
        raise ValueError("--eval-episodes must be positive")
    validate_setup(DECK, args.encounter_id, args.player_hp, args.player_max_hp, args.max_turns)
    validate_ppo_args(args)

    model_path = Path(args.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    env_kwargs = {
        "deck": list(DECK),
        "encounter_id": args.encounter_id,
        "player_hp": args.player_hp,
        "player_max_hp": args.player_max_hp,
        "max_turns": args.max_turns,
    }
    env = CustomBattleTrainingEnv(seed=args.seed, **env_kwargs)
    Path(args.tensorboard_log).mkdir(parents=True, exist_ok=True)
    print(
        "Custom battle setup: "
        f"encounter={args.encounter_id}, deck_size={len(DECK)}, "
        f"hp={args.player_hp}/{args.player_max_hp}, max_turns={args.max_turns}, "
        f"timesteps={args.timesteps}"
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
            print(f"No existing model found. Train new custom-fight model: {model_path}")
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
        return

    model.save(model_path)
    print(f"Saved model: {model_path}")
    evaluate(model, episodes=args.eval_episodes, seed=args.seed + 500_000, env_kwargs=env_kwargs)


if __name__ == "__main__":
    main()
