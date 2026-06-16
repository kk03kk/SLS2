from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from sb3_contrib import MaskablePPO

from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.route_env import RouteResult, UnderdocksRoutePPOEnv


@dataclass(frozen=True)
class RouteEvalSummary:
    episodes: int
    win_rate: float
    avg_hp_lost: float
    avg_final_hp: float
    avg_combats_won: float
    best: RouteResult | None
    worst_win: RouteResult | None


def card_names(card_ids: list[str]) -> str:
    return " | ".join(CARD_LIBRARY[card_id].name for card_id in card_ids)


def card_name_list(card_ids: list[str]) -> list[str]:
    return [CARD_LIBRARY[card_id].name for card_id in card_ids]


def pile_names(pile) -> list[str]:
    return [CARD_LIBRARY[card.def_id].name for card in pile]


def run_episode(
    model: MaskablePPO,
    *,
    seed: int,
    deterministic: bool,
    enable_burning_blood: bool,
) -> RouteResult:
    env = UnderdocksRoutePPOEnv(seed=seed, enable_burning_blood=enable_burning_blood)
    obs, _ = env.reset()
    done = False
    info = {}
    while not done:
        action, _ = model.predict(obs, deterministic=deterministic, action_masks=env.action_masks())
        obs, _, terminated, truncated, info = env.step(int(action))
        done = terminated or truncated
    return info["result"]


def append_route_state(lines: list[str], env: UnderdocksRoutePPOEnv) -> None:
    lines.append(f"Phase: {env.phase} | HP {env.hp}/{env.max_hp} | room {env.route_index + 1}/{len(env.route)}")
    lines.append(f"Route: {[encounter_id for _, encounter_id in env.route]}")
    lines.append(f"Deck({len(env.deck)}): {card_name_list(env.deck)}")
    if env.phase == "combat":
        combat = env.combat
        lines.append(
            f"Combat turn {combat.turn} | block {combat.player.block} | energy {combat.energy} | "
            f"str {combat.player.power_amount('strength')} weak {combat.player.power_amount('weak')} "
            f"vuln {combat.player.power_amount('vulnerable')} frail {combat.player.power_amount('frail')}"
        )
        for idx, enemy in enumerate(combat.enemies):
            if enemy.alive:
                move = combat.current_enemy_move(enemy)
                lines.append(
                    f"Enemy[{idx}] {enemy.creature.name} HP {enemy.creature.hp}/{enemy.creature.max_hp} "
                    f"block {enemy.creature.block} powers {dict(enemy.creature.powers)} intent {move.intent}"
                )
            else:
                lines.append(f"Enemy[{idx}] {enemy.creature.name} dead")
        lines.append(f"Hand: {pile_names(combat.hand)}")
        lines.append(
            f"Draw {len(combat.draw_pile)} | Discard {pile_names(combat.discard_pile)} | "
            f"Exhaust {pile_names(combat.exhaust_pile)}"
        )
    elif env.phase == "reward":
        lines.append(f"Reward choices: {card_name_list(env.reward_choices)} + Skip")
    elif env.phase == "rest":
        upgrades = [
            f"{idx}:{CARD_LIBRARY[card_id].name}->{CARD_LIBRARY[CARD_LIBRARY[card_id].upgraded_id].name}"
            for idx, card_id in enumerate(env.deck)
            if CARD_LIBRARY[card_id].upgraded_id is not None
        ]
        lines.append(f"Rest options: Rest or upgrade {upgrades}")


def trace_episode_to_lines(
    model: MaskablePPO,
    *,
    seed: int,
    deterministic: bool,
    enable_burning_blood: bool,
) -> tuple[RouteResult, list[str]]:
    env = UnderdocksRoutePPOEnv(seed=seed, enable_burning_blood=enable_burning_blood)
    obs, _ = env.reset()
    done = False
    step_no = 0
    last_route_log_len = 0
    last_combat_log_len = len(env.combat.log) if env.phase == "combat" else 0
    info = {}
    lines: list[str] = [
        f"Seed: {seed}",
        f"Burning Blood: {enable_burning_blood}",
        "",
    ]

    while not done:
        step_no += 1
        lines.append("=" * 88)
        append_route_state(lines, env)
        action, _ = model.predict(obs, deterministic=deterministic, action_masks=env.action_masks())
        action = int(action)
        lines.append(f"AI step {step_no}: {env.describe_action(action)}")
        obs, reward, terminated, truncated, info = env.step(action)

        if env.phase == "combat":
            new_combat_logs = env.combat.log[last_combat_log_len:]
            last_combat_log_len = len(env.combat.log)
            for line in new_combat_logs:
                lines.append(f"  {line}")
        else:
            last_combat_log_len = len(env.combat.log) if hasattr(env, "combat") else 0
        new_route_logs = env.log[last_route_log_len:]
        last_route_log_len = len(env.log)
        for line in new_route_logs:
            lines.append(f"  {line}")
        lines.append(f"Reward: {reward:.3f}")
        done = terminated or truncated

    result = info["result"]
    lines.append("=" * 88)
    lines.append(f"Result: {'WIN' if result.won else 'LOSS'}")
    lines.append(f"Final HP: {result.final_hp}/80 | total HP loss: {result.total_hp_lost} | combats won: {result.combats_won}/7")
    lines.append(f"Picks: {card_name_list([p for p in result.picks if p != 'skip'])}, skips={result.picks.count('skip')}")
    lines.append(f"Upgrades: {result.upgrades} | rests: {result.rests}")
    lines.append(f"Final deck({len(result.deck)}): {card_name_list(result.deck)}")
    return result, lines


def evaluate(
    model: MaskablePPO,
    *,
    episodes: int,
    seed: int,
    deterministic: bool,
    enable_burning_blood: bool,
) -> tuple[RouteEvalSummary, list[tuple[int, RouteResult]]]:
    rows: list[tuple[int, RouteResult]] = []
    for offset in range(episodes):
        episode_seed = seed + offset
        rows.append(
            (
                episode_seed,
                run_episode(
                    model,
                    seed=episode_seed,
                    deterministic=deterministic,
                    enable_burning_blood=enable_burning_blood,
                ),
            )
        )
    wins = [result for _, result in rows if result.won]
    best = min(wins, key=lambda r: (r.total_hp_lost, -r.final_hp, len(r.deck))) if wins else None
    worst_win = max(wins, key=lambda r: (r.total_hp_lost, -r.final_hp)) if wins else None
    summary = RouteEvalSummary(
        episodes=episodes,
        win_rate=len(wins) / max(1, episodes),
        avg_hp_lost=sum(r.total_hp_lost for _, r in rows) / max(1, episodes),
        avg_final_hp=sum(r.final_hp for _, r in rows) / max(1, episodes),
        avg_combats_won=sum(r.combats_won for _, r in rows) / max(1, episodes),
        best=best,
        worst_win=worst_win,
    )
    return summary, rows


def write_csv(path: Path, rows: list[tuple[int, RouteResult]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "seed",
                "won",
                "final_hp",
                "total_hp_lost",
                "combats_won",
                "route",
                "picks",
                "upgrades",
                "rests",
                "deck",
            ]
        )
        for seed, result in rows:
            writer.writerow(
                [
                    seed,
                    int(result.won),
                    result.final_hp,
                    result.total_hp_lost,
                    result.combats_won,
                    " | ".join(result.route),
                    " | ".join(result.picks),
                    " | ".join(result.upgrades),
                    result.rests,
                    " | ".join(result.deck),
                ]
            )


def write_summary(path: Path, summary: RouteEvalSummary, rows: list[tuple[int, RouteResult]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wins = [(seed, result) for seed, result in rows if result.won]
    combats_counts: dict[int, int] = {}
    upgrade_counts: dict[int, int] = {}
    for _, result in rows:
        combats_counts[result.combats_won] = combats_counts.get(result.combats_won, 0) + 1
        upgrade_counts[len(result.upgrades)] = upgrade_counts.get(len(result.upgrades), 0) + 1
    with path.open("w", encoding="utf-8") as f:
        f.write(f"Episodes: {summary.episodes}\n")
        f.write(f"Wins: {len(wins)}\n")
        f.write(f"Win rate: {summary.win_rate:.2%}\n")
        f.write(f"Average total HP loss: {summary.avg_hp_lost:.2f}\n")
        f.write(f"Average final HP: {summary.avg_final_hp:.2f}\n")
        f.write(f"Average combats won: {summary.avg_combats_won:.2f}/7\n")
        f.write(f"Combats won distribution: {dict(sorted(combats_counts.items()))}\n")
        f.write(f"Upgrade count distribution: {dict(sorted(upgrade_counts.items()))}\n")
        if wins:
            first_seed, first_win = wins[0]
            f.write(f"First win seed: {first_seed}\n")
            f.write(f"First win final HP: {first_win.final_hp}\n")
            f.write(f"First win route: {first_win.route}\n")
            f.write(f"First win picks: {first_win.picks}\n")
            f.write(f"First win upgrades: {first_win.upgrades}\n")
        else:
            f.write("First win seed: none\n")


def print_result(title: str, result: RouteResult | None) -> None:
    print(f"\n{title}:")
    if result is None:
        print("  none")
        return
    print(f"  final_hp={result.final_hp} hp_lost={result.total_hp_lost} combats={result.combats_won}/7")
    print(f"  route={result.route}")
    print(f"  picks={result.picks}")
    print(f"  upgrades={result.upgrades} rests={result.rests}")
    print(f"  deck={card_names(result.deck)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a route PPO model over many random routes.")
    parser.add_argument("--model-path", default="models/ppo_underdocks_route_a0.zip")
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--seed", type=int, default=2_000_000)
    parser.add_argument("--csv-path", default="runs/underdocks_route_eval.csv")
    parser.add_argument("--summary-path", default="runs/underdocks_route_eval_summary.txt")
    parser.add_argument("--first-win-log-path", default="runs/underdocks_route_first_win_trace.txt")
    parser.add_argument("--deterministic", action="store_true", default=True)
    parser.add_argument("--no-burning-blood", action="store_true")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = MaskablePPO.load(model_path, device="auto")
    summary, rows = evaluate(
        model,
        episodes=args.episodes,
        seed=args.seed,
        deterministic=args.deterministic,
        enable_burning_blood=not args.no_burning_blood,
    )
    write_csv(Path(args.csv_path), rows)
    write_summary(Path(args.summary_path), summary, rows)

    first_win = next(((seed, result) for seed, result in rows if result.won), None)
    if first_win is not None:
        first_win_seed, _ = first_win
        traced_result, trace_lines = trace_episode_to_lines(
            model,
            seed=first_win_seed,
            deterministic=args.deterministic,
            enable_burning_blood=not args.no_burning_blood,
        )
        if not traced_result.won:
            trace_lines.append("")
            trace_lines.append("WARNING: first win seed did not reproduce as a win during trace.")
        first_win_log_path = Path(args.first_win_log_path)
        first_win_log_path.parent.mkdir(parents=True, exist_ok=True)
        first_win_log_path.write_text("\n".join(trace_lines) + "\n", encoding="utf-8")

    print(f"Episodes: {summary.episodes}")
    print(f"Win rate: {summary.win_rate:.1%}")
    print(f"Average total HP loss: {summary.avg_hp_lost:.2f}")
    print(f"Average final HP: {summary.avg_final_hp:.2f}")
    print(f"Average combats won: {summary.avg_combats_won:.2f}/7")
    print_result("Best win", summary.best)
    print_result("Worst win", summary.worst_win)
    print(f"\nCSV saved to {Path(args.csv_path)}")
    print(f"Summary saved to {Path(args.summary_path)}")
    if first_win is None:
        print("No wins found; first win trace was not written.")
    else:
        print(f"First win trace saved to {Path(args.first_win_log_path)}")


if __name__ == "__main__":
    main()
