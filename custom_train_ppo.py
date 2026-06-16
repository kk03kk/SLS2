from __future__ import annotations

import argparse
from pathlib import Path

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
    "strike_ironclad",
    "defend_ironclad",
    "defend_ironclad",
    "defend_ironclad",
    "defend_ironclad",
    "bash",
]
# =========================


class CustomBattleTrainingEnv(GenericBattlePPOEnv):
    def __init__(self, *, seed: int | None = None) -> None:
        self.custom_deck = list(DECK)
        self.custom_encounter_id = ENCOUNTER_ID
        super().__init__(
            seed=seed,
            stage="weak",
            max_turns=MAX_TURNS,
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
            player_hp=PLAYER_HP,
            player_max_hp=PLAYER_MAX_HP,
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


def evaluate(model: MaskablePPO, *, episodes: int, seed: int) -> None:
    wins = 0
    hp_lost = []
    turns = []
    for idx in range(episodes):
        env = CustomBattleTrainingEnv(seed=seed + idx)
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
    print(f"Average hp lost: {sum(hp_lost) / max(1, len(hp_lost)):.2f}")
    print(f"Best hp lost: {min(hp_lost)}")
    print(f"Average turns: {sum(turns) / max(1, len(turns)):.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune the battle model on a custom official encounter.")
    parser.add_argument("--timesteps", type=int, default=50_000)
    parser.add_argument("--model-path", default=MODEL_PATH)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tensorboard-log", default=TENSORBOARD_LOG)
    parser.add_argument("--eval-episodes", type=int, default=50)
    parser.add_argument("--fresh", action="store_true", help="Ignore an existing model and train from scratch.")
    parser.add_argument("--resume", action="store_true", help="Kept for compatibility; resume is already the default.")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    env = CustomBattleTrainingEnv(seed=args.seed)

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
            n_steps=1024,
            batch_size=256,
            n_epochs=8,
            gamma=0.98,
            gae_lambda=0.95,
            learning_rate=1e-4,
            ent_coef=0.01,
            clip_range=0.15,
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
    evaluate(model, episodes=args.eval_episodes, seed=args.seed + 500_000)


if __name__ == "__main__":
    main()
