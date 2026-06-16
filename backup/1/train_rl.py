from __future__ import annotations

import argparse
from pathlib import Path

from sts2_sim.agents import RandomAgent, SimpleAttackAgent
from sts2_sim.cards import ironclad_a10_starting_deck
from sts2_sim.enemies import ENCOUNTERS, ENEMY_LIBRARY
from sts2_sim.evaluation import run_combat
from sts2_sim.engine import CombatEnv
from sts2_sim.rl import QAgent, evaluate_q_agent, load_q_table, save_q_table, train_q_learning


def build_enemies(encounter_id: str):
    return [ENEMY_LIBRARY[enemy_id] for enemy_id in ENCOUNTERS[encounter_id]]


def evaluate_baseline(deck: list[str], enemies: list, *, runs: int, seed: int, agent_name: str) -> tuple[float, float, float]:
    wins = 0
    hp_lost: list[int] = []
    turns: list[int] = []
    for offset in range(runs):
        run_seed = seed + offset
        env = CombatEnv(deck, enemies, seed=run_seed)
        if agent_name == "simple":
            agent = SimpleAttackAgent()
        else:
            agent = RandomAgent(seed=run_seed)
        result = run_combat(env, agent)
        wins += int(result.won)
        hp_lost.append(result.hp_lost)
        turns.append(result.turns)
    return (
        wins / runs,
        sum(hp_lost) / runs,
        sum(turns) / runs,
    )


def print_eval_line(label: str, win_rate: float, avg_hp_lost: float, avg_turns: float) -> None:
    print(f"{label}: win={win_rate:.1%}, avg_hp_lost={avg_hp_lost:.2f}, avg_turns={avg_turns:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a tiny tabular Q-learning combat agent.")
    parser.add_argument("--encounter", choices=sorted(ENCOUNTERS), default="medium_slime")
    parser.add_argument("--episodes", type=int, default=5000)
    parser.add_argument("--eval-runs", type=int, default=300)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--alpha", type=float, default=0.25)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--epsilon-start", type=float, default=0.35)
    parser.add_argument("--epsilon-end", type=float, default=0.03)
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--output", default="q_table.json")
    parser.add_argument("--load", default=None, help="Skip training and evaluate an existing q_table.json.")
    parser.add_argument("--show-one", action="store_true", help="Print one greedy Q-agent combat log after training.")
    args = parser.parse_args()

    deck = ironclad_a10_starting_deck()
    enemies = build_enemies(args.encounter)

    print(f"Deck: A10 Ironclad starter deck ({len(deck)} cards)")
    print(f"Encounter: {args.encounter}")
    print(f"Eval runs: {args.eval_runs}")
    print()

    random_eval = evaluate_baseline(deck, enemies, runs=args.eval_runs, seed=args.seed + 20_000, agent_name="random")
    simple_eval = evaluate_baseline(deck, enemies, runs=args.eval_runs, seed=args.seed + 30_000, agent_name="simple")
    print_eval_line("Random baseline", *random_eval)
    print_eval_line("Simple baseline", *simple_eval)
    print()

    if args.load:
        q_table, metadata = load_q_table(args.load)
        print(f"Loaded Q table: {args.load}")
        if metadata:
            print(f"Metadata: {metadata}")
    else:
        print(f"Training episodes: {args.episodes}")
        q_table = train_q_learning(
            deck,
            enemies,
            episodes=args.episodes,
            seed=args.seed,
            alpha=args.alpha,
            gamma=args.gamma,
            epsilon_start=args.epsilon_start,
            epsilon_end=args.epsilon_end,
            max_turns=args.max_turns,
        )
        metadata = {
            "encounter": args.encounter,
            "episodes": args.episodes,
            "seed": args.seed,
            "alpha": args.alpha,
            "gamma": args.gamma,
            "epsilon_start": args.epsilon_start,
            "epsilon_end": args.epsilon_end,
            "max_turns": args.max_turns,
            "deck": deck,
        }
        save_q_table(args.output, q_table, metadata)
        print(f"Saved Q table: {Path(args.output).resolve()}")

    stats = evaluate_q_agent(
        q_table,
        deck,
        enemies,
        runs=args.eval_runs,
        seed=args.seed + 40_000,
        max_turns=args.max_turns,
    )
    print()
    print_eval_line("Q agent", stats.win_rate, stats.avg_hp_lost, stats.avg_turns)
    print(f"Q states: {stats.states}")
    print(f"Q state-actions: {stats.actions}")

    if args.show_one:
        print()
        env = CombatEnv(deck, enemies, seed=args.seed + 50_000, max_turns=args.max_turns)
        result = run_combat(env, QAgent(q_table, seed=args.seed), verbose=True)
        print(f"Detailed result: {'WIN' if result.won else 'LOSS'}, HP lost={result.hp_lost}")


if __name__ == "__main__":
    main()
