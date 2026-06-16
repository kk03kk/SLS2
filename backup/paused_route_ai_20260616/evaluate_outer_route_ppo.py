from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from sb3_contrib import MaskablePPO

from route_ai.env import BattleDelegatingRouteEnv
from sts2_sim.cards import CARD_LIBRARY


def card_name(card_id: str) -> str:
    return "Skip" if card_id == "skip" else CARD_LIBRARY[card_id].name


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate route-level PPO and summarize card picks.")
    parser.add_argument("--model-path", default="route_ai_models/ppo_outer_route.zip")
    parser.add_argument("--battle-model-path", default="battle_ai_models/ppo_generic_battle.zip")
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--seed", type=int, default=200_000)
    parser.add_argument("--output", default="route_ai_reports/eval_outer_route.csv")
    parser.add_argument("--pick-summary", default="route_ai_reports/pick_summary.csv")
    args = parser.parse_args()

    env = BattleDelegatingRouteEnv(seed=args.seed, battle_model_path=args.battle_model_path)
    model = MaskablePPO.load(args.model_path, env=env, device="auto")
    rows = []
    pick_counts: Counter[str] = Counter()
    offer_counts: Counter[str] = Counter()
    upgrade_counts: Counter[str] = Counter()
    first_win_log: list[str] | None = None

    for ep in range(args.episodes):
        obs, _ = env.reset(seed=args.seed + ep)
        done = False
        info = {}
        while not done:
            action, _ = model.predict(obs, deterministic=True, action_masks=env.action_masks())
            obs, _, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
        result = info["result"]
        for offer in result.reward_offers:
            for card_id in offer:
                offer_counts[card_id] += 1
        for pick in result.picks:
            pick_counts[pick] += 1
        for upgrade in result.upgrades:
            upgrade_counts[upgrade] += 1
        if result.won and first_win_log is None:
            first_win_log = result.log
        rows.append(
            {
                "episode": ep,
                "won": int(result.won),
                "final_hp": result.final_hp,
                "combats_won": result.combats_won,
                "total_hp_lost": result.total_hp_lost,
                "picks": " | ".join(result.picks),
                "picks_names": " | ".join(card_name(pick) for pick in result.picks),
                "upgrades": " | ".join(result.upgrades),
                "rests": result.rests,
                "deck": " | ".join(result.deck),
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    pick_path = Path(args.pick_summary)
    pick_path.parent.mkdir(parents=True, exist_ok=True)
    with pick_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["card_id", "name", "picked", "offered", "pick_rate_when_offered", "upgraded"])
        all_cards = set(offer_counts) | set(pick_counts) | set(upgrade_counts)
        for card_id in sorted(all_cards, key=lambda cid: (-pick_counts[cid], card_name(cid))):
            offered = offer_counts[card_id]
            picked = pick_counts[card_id]
            writer.writerow(
                [
                    card_id,
                    card_name(card_id),
                    picked,
                    offered,
                    "" if offered == 0 else f"{picked / offered:.4f}",
                    upgrade_counts[card_id],
                ]
            )

    wins = sum(row["won"] for row in rows)
    avg_combats = sum(row["combats_won"] for row in rows) / max(1, len(rows))
    avg_hp = sum(row["final_hp"] for row in rows) / max(1, len(rows))
    print(f"Episodes: {len(rows)}")
    print(f"Win rate: {wins / max(1, len(rows)):.1%}")
    print(f"Average combats won: {avg_combats:.2f}/7")
    print(f"Average final HP: {avg_hp:.2f}")
    print("Top picks:")
    for card_id, count in pick_counts.most_common(15):
        print(f"  {card_name(card_id)}: {count}")
    print(f"Saved eval: {output}")
    print(f"Saved pick summary: {pick_path}")
    if first_win_log is not None:
        trace_path = output.parent / "first_win_outer_route_log.txt"
        trace_path.write_text("\n".join(first_win_log), encoding="utf-8")
        print(f"Saved first win log: {trace_path}")


if __name__ == "__main__":
    main()
