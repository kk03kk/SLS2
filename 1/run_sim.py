from __future__ import annotations

import argparse

from sts2_sim.agents import RandomAgent, SimpleAttackAgent
from sts2_sim.cards import ironclad_a10_starting_deck
from sts2_sim.enemies import ENCOUNTERS, ENEMY_LIBRARY
from sts2_sim.engine import CombatEnv
from sts2_sim.evaluation import evaluate, run_combat
from sts2_sim.scenarios import build_ironclad_seapunk_42_env, ironclad_seapunk_42_deck


def build_enemies(encounter_id: str):
    return [ENEMY_LIBRARY[enemy_id] for enemy_id in ENCOUNTERS[encounter_id]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local headless STS2 combat simulator.")
    parser.add_argument("--encounter", choices=sorted(ENCOUNTERS), default="two_small_slimes")
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--agent", choices=["random", "simple"], default="random")
    parser.add_argument("--scenario", choices=["ironclad_seapunk_42"], default=None)
    parser.add_argument("--single", action="store_true", help="Print one detailed combat log.")
    args = parser.parse_args()

    if args.scenario == "ironclad_seapunk_42":
        deck = ironclad_seapunk_42_deck()
        enemies = build_enemies("seapunk_weak")
        player_hp = 42
        encounter_name = "seapunk_weak"
    else:
        deck = ironclad_a10_starting_deck()
        enemies = build_enemies(args.encounter)
        player_hp = 80
        encounter_name = args.encounter
    agent = RandomAgent(seed=args.seed) if args.agent == "random" else SimpleAttackAgent()

    if args.single:
        if args.scenario == "ironclad_seapunk_42":
            env = build_ironclad_seapunk_42_env(seed=args.seed)
        else:
            env = CombatEnv(deck, enemies, seed=args.seed, player_hp=player_hp)
        run_combat(env, agent, verbose=True)
        return

    summary = evaluate(deck, enemies, runs=args.runs, seed=args.seed, player_hp=player_hp)
    print(f"Encounter: {encounter_name}")
    print(f"Runs: {summary.runs}")
    print(f"Win rate: {summary.win_rate:.1%}")
    print(f"Average HP lost: {summary.avg_hp_lost:.2f}")
    print(f"Average turns: {summary.avg_turns:.2f}")
    print(f"Worst 10% HP lost: {summary.worst_10pct_hp_lost:.2f}")
    print(f"HP lost std: {summary.hp_lost_std:.2f}")


if __name__ == "__main__":
    main()
