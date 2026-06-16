r"""
#   固定一套测试种子，分别测试 weak / regular / elite / boss / all 五类战斗。
#   这是以后判断“模型到底有没有变强”的主仪表盘，比混在一起的 TensorBoard 更清楚。
#
# 常用运行：
#   python battle_model_benchmark.py --label after_training_001
#
# 快速检查：
#   python battle_model_benchmark.py --quick --label quick_check_001
#
# 输出：
#   D:\SLS2\battle_ai_reports\benchmarks\history.csv       历史基准数据
#   D:\SLS2\battle_ai_reports\benchmarks\progress.png      进步曲线图
#   D:\SLS2\battle_ai_reports\benchmarks\xxx_summary.md    本次测试摘要
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv


BENCHMARK_SUITES = (
    ("weak", 120, 110_000),
    ("regular", 120, 120_000),
    ("elite", 80, 130_000),
    ("boss", 80, 140_000),
    ("all", 120, 150_000),
)


def evaluate_stage(
    model: MaskablePPO,
    *,
    stage: str,
    episodes: int,
    seed: int,
    details_path: Path,
) -> dict[str, float | int | str]:
    env = GenericBattlePPOEnv(seed=seed, stage=stage)
    rows = []
    by_encounter = defaultdict(lambda: {"n": 0, "wins": 0, "hp_lost": 0, "turns": 0})
    for idx in range(episodes):
        obs, _ = env.reset(seed=seed + idx)
        done = False
        info = {}
        while not done:
            action, _ = model.predict(obs, deterministic=True, action_masks=env.action_masks())
            obs, _, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
        result = info["result"]
        scenario = env.scenario
        row = {
            "stage_suite": stage,
            "episode": idx,
            "scenario_stage": scenario.stage,
            "encounter": scenario.encounter_id,
            "won": int(result.won),
            "hp_lost": result.hp_lost,
            "final_hp": result.final_hp,
            "turns": result.turns,
            "deck_size": len(scenario.deck),
        }
        rows.append(row)
        bucket = by_encounter[scenario.encounter_id]
        bucket["n"] += 1
        bucket["wins"] += int(result.won)
        bucket["hp_lost"] += result.hp_lost
        bucket["turns"] += result.turns

    details_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not details_path.exists()
    with details_path.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

    wins = sum(row["won"] for row in rows)
    return {
        "stage": stage,
        "episodes": episodes,
        "win_rate": wins / max(1, episodes),
        "avg_hp_lost": sum(row["hp_lost"] for row in rows) / max(1, episodes),
        "avg_final_hp": sum(row["final_hp"] for row in rows) / max(1, episodes),
        "avg_turns": sum(row["turns"] for row in rows) / max(1, episodes),
    }


def append_history(history_path: Path, label: str, model_path: str, summaries: list[dict]) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not history_path.exists()
    now = datetime.now().isoformat(timespec="seconds")
    with history_path.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "time",
                "label",
                "model_path",
                "stage",
                "episodes",
                "win_rate",
                "avg_hp_lost",
                "avg_final_hp",
                "avg_turns",
            ])
        for summary in summaries:
            writer.writerow([
                now,
                label,
                model_path,
                summary["stage"],
                summary["episodes"],
                f"{summary['win_rate']:.6f}",
                f"{summary['avg_hp_lost']:.6f}",
                f"{summary['avg_final_hp']:.6f}",
                f"{summary['avg_turns']:.6f}",
            ])


def write_markdown(path: Path, label: str, summaries: list[dict]) -> None:
    lines = [
        f"# Battle Model Benchmark: {label}",
        "",
        "| Stage | Episodes | Win Rate | Avg HP Lost | Avg Final HP | Avg Turns |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        lines.append(
            f"| {summary['stage']} | {summary['episodes']} | "
            f"{summary['win_rate']:.1%} | {summary['avg_hp_lost']:.2f} | "
            f"{summary['avg_final_hp']:.2f} | {summary['avg_turns']:.2f} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_history(history_path: Path, output_path: Path) -> None:
    if not history_path.exists():
        return
    rows = list(csv.DictReader(history_path.open(encoding="utf-8-sig")))
    if not rows:
        return
    stages = []
    labels = []
    by_stage: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for row in rows:
        stage = row["stage"]
        label = row["label"]
        if stage not in stages:
            stages.append(stage)
        if label not in labels:
            labels.append(label)
        by_stage[stage].append((label, float(row["win_rate"]), float(row["avg_hp_lost"])))

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    for stage in stages:
        data = by_stage[stage]
        xs = list(range(len(data)))
        axes[0].plot(xs, [item[1] for item in data], marker="o", label=stage)
        axes[1].plot(xs, [item[2] for item in data], marker="o", label=stage)
    axes[0].set_title("Win Rate On Fixed Benchmark Seeds")
    axes[0].set_ylabel("Win rate")
    axes[0].set_ylim(-0.02, 1.02)
    axes[0].grid(True, alpha=0.25)
    axes[1].set_title("Average HP Lost On Fixed Benchmark Seeds")
    axes[1].set_ylabel("HP lost")
    axes[1].set_xlabel("Benchmark run")
    axes[1].grid(True, alpha=0.25)
    axes[0].legend(ncol=5, fontsize=9)
    axes[1].legend(ncol=5, fontsize=9)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a fixed benchmark suite for the battle model.")
    parser.add_argument("--model-path", default="battle_ai_models/ppo_generic_battle.zip")
    parser.add_argument("--label", default=None, help="Name for this benchmark row, e.g. after_1m_all_5_10.")
    parser.add_argument("--quick", action="store_true", help="Use fewer episodes for a faster check.")
    parser.add_argument("--out-dir", default="battle_ai_reports/benchmarks")
    args = parser.parse_args()

    label = args.label or datetime.now().strftime("run_%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    details_path = out_dir / f"{label}_details.csv"
    history_path = out_dir / "history.csv"
    chart_path = out_dir / "progress.png"
    markdown_path = out_dir / f"{label}_summary.md"

    bootstrap_env = GenericBattlePPOEnv(seed=1, stage="weak")
    model = MaskablePPO.load(args.model_path, env=bootstrap_env, device="auto")

    summaries = []
    for stage, episodes, seed in BENCHMARK_SUITES:
        actual_episodes = max(20, episodes // 4) if args.quick else episodes
        print(f"Evaluating {stage}: {actual_episodes} episodes")
        summaries.append(
            evaluate_stage(
                model,
                stage=stage,
                episodes=actual_episodes,
                seed=seed,
                details_path=details_path,
            )
        )

    append_history(history_path, label, args.model_path, summaries)
    write_markdown(markdown_path, label, summaries)
    plot_history(history_path, chart_path)

    print("\nBenchmark summary:")
    for summary in summaries:
        print(
            f"{summary['stage']}: win={summary['win_rate']:.1%}, "
            f"hp_lost={summary['avg_hp_lost']:.2f}, final_hp={summary['avg_final_hp']:.2f}, "
            f"turns={summary['avg_turns']:.2f}"
        )
    print(f"\nSaved summary: {markdown_path}")
    print(f"Saved details: {details_path}")
    print(f"Saved history: {history_path}")
    print(f"Saved chart: {chart_path}")


if __name__ == "__main__":
    main()
