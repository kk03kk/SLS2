from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from sb3_contrib import MaskablePPO

from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.ppo_env import FixedFightPPOEnv
from sts2_sim.ppo_mc import select_action_with_monte_carlo
from sts2_sim.scenarios import IRONCLAD_RANDOM_BONUS_CARD_POOL


SCENARIO = "ironclad_calcified_cultist_a10_bonus"


@dataclass(frozen=True)
class CardEval:
    card_id: str
    name: str
    win_rate: float
    avg_hp_lost: float
    avg_turns: float
    worst_hp_lost: int


def evaluate_card(
    model: MaskablePPO,
    *,
    card_id: str,
    episodes: int,
    seed: int,
    deterministic: bool,
    mc_rollouts: int,
    mc_depth: int,
) -> CardEval:
    wins = 0
    hp_lost: list[int] = []
    turns: list[int] = []
    for offset in range(episodes):
        env = FixedFightPPOEnv(
            scenario=SCENARIO,
            seed=seed + offset,
            extra_card_id=card_id,
        )
        obs, _ = env.reset()
        done = False
        info = {}
        while not done:
            if mc_rollouts > 0:
                action, _ = select_action_with_monte_carlo(
                    env,
                    model,
                    rollouts=mc_rollouts,
                    max_depth=mc_depth,
                    rollout_deterministic=deterministic,
                )
            else:
                action, _ = model.predict(
                    obs,
                    deterministic=deterministic,
                    action_masks=env.action_masks(),
                )
                action = int(action)
            obs, _, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        result = info["result"]
        wins += int(result.won)
        hp_lost.append(result.hp_lost)
        turns.append(result.turns)
    return CardEval(
        card_id=card_id,
        name=CARD_LIBRARY[card_id].name,
        win_rate=wins / max(1, episodes),
        avg_hp_lost=sum(hp_lost) / max(1, len(hp_lost)),
        avg_turns=sum(turns) / max(1, len(turns)),
        worst_hp_lost=max(hp_lost) if hp_lost else 0,
    )


def write_csv(path: Path, rows: list[CardEval]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "card_id", "name", "win_rate", "avg_hp_lost", "avg_turns", "worst_hp_lost"])
        for rank, row in enumerate(rows, start=1):
            writer.writerow([
                rank,
                row.card_id,
                row.name,
                f"{row.win_rate:.6f}",
                f"{row.avg_hp_lost:.6f}",
                f"{row.avg_turns:.6f}",
                row.worst_hp_lost,
            ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank Ironclad bonus cards against high-ascension Calcified Cultist.")
    parser.add_argument("--model-path", default=f"models/ppo_{SCENARIO}.zip")
    parser.add_argument("--episodes", type=int, default=300)
    parser.add_argument("--seed", type=int, default=2_000_000)
    parser.add_argument("--csv-path", default="runs/calcified_bonus_card_rank.csv")
    parser.add_argument("--deterministic", action="store_true", default=True)
    parser.add_argument("--mc-rollouts", type=int, default=0)
    parser.add_argument("--mc-depth", type=int, default=80)
    parser.add_argument("--limit", type=int, default=0, help="Evaluate only the first N cards for a quick smoke test.")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = MaskablePPO.load(model_path, device="auto")
    card_ids = list(IRONCLAD_RANDOM_BONUS_CARD_POOL)
    if args.limit > 0:
        card_ids = card_ids[: args.limit]

    rows: list[CardEval] = []
    for index, card_id in enumerate(card_ids, start=1):
        row = evaluate_card(
            model,
            card_id=card_id,
            episodes=args.episodes,
            seed=args.seed,
            deterministic=args.deterministic,
            mc_rollouts=args.mc_rollouts,
            mc_depth=args.mc_depth,
        )
        rows.append(row)
        print(
            f"{index:02d}/{len(card_ids):02d} {row.name:<24} "
            f"win={row.win_rate:.1%} avg_loss={row.avg_hp_lost:.2f} "
            f"turns={row.avg_turns:.2f} worst={row.worst_hp_lost}"
        )

    rows.sort(key=lambda row: (row.avg_hp_lost, -row.win_rate, row.avg_turns, row.worst_hp_lost))
    write_csv(Path(args.csv_path), rows)

    print("\nTop 10:")
    for rank, row in enumerate(rows[:10], start=1):
        print(f"{rank:02d}. {row.name:<24} avg_loss={row.avg_hp_lost:.2f} win={row.win_rate:.1%}")
    print("\nBottom 10:")
    for rank, row in enumerate(rows[-10:], start=max(1, len(rows) - 9)):
        print(f"{rank:02d}. {row.name:<24} avg_loss={row.avg_hp_lost:.2f} win={row.win_rate:.1%}")
    print(f"\nCSV saved to {Path(args.csv_path)}")


if __name__ == "__main__":
    main()
