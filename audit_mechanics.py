from __future__ import annotations

import argparse
import random
import traceback

import numpy as np

from sts2_sim.cards import ironclad_a0_starting_deck, ironclad_singleplayer_reward_pool
from sts2_sim.engine import CombatEnv
from sts2_sim.enemies import (
    ENCOUNTERS,
    ENEMY_LIBRARY,
    UNDERDOCKS_BOSS_ENCOUNTERS,
    UNDERDOCKS_ELITE_ENCOUNTERS,
    UNDERDOCKS_REGULAR_ENCOUNTERS,
    UNDERDOCKS_WEAK_ENCOUNTERS,
)
from sts2_sim.route_env import UnderdocksRoutePPOEnv


UNDERDOCKS_ENCOUNTERS = {
    **UNDERDOCKS_WEAK_ENCOUNTERS,
    **UNDERDOCKS_REGULAR_ENCOUNTERS,
    **UNDERDOCKS_ELITE_ENCOUNTERS,
    **UNDERDOCKS_BOSS_ENCOUNTERS,
}


def random_deck(seed: int, extra_cards: int) -> list[str]:
    pool = ironclad_singleplayer_reward_pool()
    rng = random.Random(seed)
    return ironclad_a0_starting_deck() + rng.sample(pool, min(extra_cards, len(pool)))


def audit_encounters(runs_per_encounter: int, extra_cards: int) -> list[str]:
    failures: list[str] = []
    for encounter_id, enemy_ids in UNDERDOCKS_ENCOUNTERS.items():
        for seed in range(runs_per_encounter):
            env = CombatEnv(
                random_deck(seed, extra_cards),
                [ENEMY_LIBRARY[enemy_id] for enemy_id in enemy_ids],
                seed=seed,
                max_turns=90,
            )
            rng = random.Random(seed * 1009 + len(encounter_id))
            try:
                done = False
                steps = 0
                while not done and steps < 350:
                    legal = env.legal_actions()
                    _, _, done, _ = env.step(rng.choice(legal))
                    steps += 1
                if not done:
                    failures.append(f"{encounter_id} seed={seed}: did not finish in {steps} steps")
            except Exception:
                failures.append(f"{encounter_id} seed={seed}: {traceback.format_exc()}")
    return failures


def audit_routes(episodes: int) -> list[str]:
    failures: list[str] = []
    rng = np.random.default_rng(12345)
    for seed in range(episodes):
        env = UnderdocksRoutePPOEnv(seed=seed)
        try:
            _, _ = env.reset()
            done = False
            steps = 0
            info = {}
            while not done and steps < 1200:
                legal = np.flatnonzero(env.action_masks())
                if len(legal) == 0:
                    raise RuntimeError(f"No legal actions in phase {env.phase}")
                _, _, terminated, truncated, info = env.step(int(rng.choice(legal)))
                done = terminated or truncated
                steps += 1
            if not done:
                failures.append(f"route seed={seed}: did not finish in {steps} steps")
            elif "result" not in info:
                failures.append(f"route seed={seed}: finished without result info")
        except Exception:
            failures.append(f"route seed={seed}: {traceback.format_exc()}")
    return failures


def audit_edge_cases() -> list[str]:
    failures: list[str] = []

    try:
        env = CombatEnv(["strike_ironclad"], [ENEMY_LIBRARY["seapunk"]], seed=1)
        enemy = env.enemies[0].creature
        env.player.add_power("flame_barrier", 4)
        enemy.add_power("flame_barrier", 4)
        env.deal_damage_from(enemy, 6, dealer=env.player)
        if env.player.hp != 76:
            failures.append(f"Flame Barrier reflection expected player hp 76, got {env.player.hp}")
    except Exception:
        failures.append("Flame Barrier edge case failed:\n" + traceback.format_exc())

    try:
        env = CombatEnv(["strike_ironclad"], [ENEMY_LIBRARY["seapunk"]], seed=1)
        enemy = env.enemies[0].creature
        env.player.add_power("thorns", 3)
        enemy.add_power("thorns", 3)
        env.deal_damage_from(enemy, 6, dealer=env.player)
        if env.player.hp != 77:
            failures.append(f"Thorns reflection expected player hp 77, got {env.player.hp}")
    except Exception:
        failures.append("Thorns edge case failed:\n" + traceback.format_exc())

    try:
        env = UnderdocksRoutePPOEnv(seed=1)
        env.route = [("boss", "waterfall_giant_boss")]
        env.route_index = 0
        env.combat = env._new_combat("waterfall_giant_boss")
        giant = env.combat.enemies[0].creature
        giant.hp = 1
        giant.add_power("steam_eruption", 15)
        attack = next(action for action in env.combat.legal_actions() if action[0] >= 0)
        _, reward, terminated, _, _ = env.step(env.combat_action_to_index[attack])
        if reward > 1000 or terminated:
            failures.append(f"Waterfall Giant blow-up reward/terminal suspicious: reward={reward} terminated={terminated}")
        if env._enemy_hp_total() > ENEMY_LIBRARY["waterfall_giant"].max_hp:
            failures.append(f"Waterfall Giant route HP total leaked: {env._enemy_hp_total()}")
    except Exception:
        failures.append("Waterfall Giant edge case failed:\n" + traceback.format_exc())

    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit dark harbor combat mechanics for crashes and reward leaks.")
    parser.add_argument("--runs-per-encounter", type=int, default=20)
    parser.add_argument("--route-episodes", type=int, default=50)
    parser.add_argument("--extra-cards", type=int, default=8)
    args = parser.parse_args()

    failures = []
    failures.extend(audit_edge_cases())
    failures.extend(audit_encounters(args.runs_per_encounter, args.extra_cards))
    failures.extend(audit_routes(args.route_episodes))

    total = len(UNDERDOCKS_ENCOUNTERS) * args.runs_per_encounter + args.route_episodes
    print(f"Audited encounter runs: {len(UNDERDOCKS_ENCOUNTERS) * args.runs_per_encounter}")
    print(f"Audited route episodes: {args.route_episodes}")
    print(f"Edge cases: 3")
    print(f"Failures: {len(failures)}")
    for failure in failures[:20]:
        print("=" * 80)
        print(failure)
    if failures:
        raise SystemExit(1)
    print(f"OK: {total + 3} checks passed")


if __name__ == "__main__":
    main()
