from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.route_env import UnderdocksRoutePPOEnv


def card_names(card_ids: list[str]) -> list[str]:
    return [CARD_LIBRARY[card_id].name for card_id in card_ids]


def pile_names(pile) -> list[str]:
    return [CARD_LIBRARY[card.def_id].name for card in pile]


def print_route_state(env: UnderdocksRoutePPOEnv) -> None:
    print(f"Phase: {env.phase} | HP {env.hp}/{env.max_hp} | room {env.route_index + 1}/{len(env.route)}")
    print(f"Route: {[encounter_id for _, encounter_id in env.route]}")
    print(f"Deck({len(env.deck)}): {card_names(env.deck)}")
    if env.phase == "combat":
        combat = env.combat
        print(
            f"Combat turn {combat.turn} | block {combat.player.block} | energy {combat.energy} | "
            f"str {combat.player.power_amount('strength')} weak {combat.player.power_amount('weak')} "
            f"vuln {combat.player.power_amount('vulnerable')} frail {combat.player.power_amount('frail')}"
        )
        for idx, enemy in enumerate(combat.enemies):
            if enemy.alive:
                move = combat.current_enemy_move(enemy)
                print(
                    f"Enemy[{idx}] {enemy.creature.name} HP {enemy.creature.hp}/{enemy.creature.max_hp} "
                    f"block {enemy.creature.block} powers {dict(enemy.creature.powers)} intent {move.intent}"
                )
            else:
                print(f"Enemy[{idx}] {enemy.creature.name} dead")
        print(f"Hand: {pile_names(combat.hand)}")
        print(f"Draw {len(combat.draw_pile)} | Discard {pile_names(combat.discard_pile)} | Exhaust {pile_names(combat.exhaust_pile)}")
    elif env.phase == "reward":
        print(f"Reward choices: {card_names(env.reward_choices)} + Skip")
    elif env.phase == "rest":
        upgrades = [
            f"{idx}:{CARD_LIBRARY[card_id].name}->{CARD_LIBRARY[CARD_LIBRARY[card_id].upgraded_id].name}"
            for idx, card_id in enumerate(env.deck)
            if CARD_LIBRARY[card_id].upgraded_id is not None
        ]
        print(f"Rest options: Rest or upgrade {upgrades}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trace every decision made by a route PPO model.")
    parser.add_argument("--model-path", default="models/ppo_underdocks_route_a0.zip")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--deterministic", action="store_true", default=True)
    parser.add_argument("--no-burning-blood", action="store_true")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = MaskablePPO.load(model_path, device="auto")
    env = UnderdocksRoutePPOEnv(
        seed=args.seed,
        enable_burning_blood=not args.no_burning_blood,
    )
    obs, _ = env.reset()
    done = False
    step_no = 0
    last_route_log_len = 0
    last_combat_log_len = len(env.combat.log) if env.phase == "combat" else 0
    info = {}

    while not done:
        step_no += 1
        print("=" * 88)
        print_route_state(env)
        action, _ = model.predict(obs, deterministic=args.deterministic, action_masks=env.action_masks())
        action = int(action)
        print(f"AI step {step_no}: {env.describe_action(action)}")
        obs, reward, terminated, truncated, info = env.step(action)

        if env.phase == "combat":
            new_combat_logs = env.combat.log[last_combat_log_len:]
            last_combat_log_len = len(env.combat.log)
            for line in new_combat_logs:
                print(f"  {line}")
        else:
            last_combat_log_len = len(env.combat.log) if hasattr(env, "combat") else 0
        new_route_logs = env.log[last_route_log_len:]
        last_route_log_len = len(env.log)
        for line in new_route_logs:
            print(f"  {line}")
        print(f"Reward: {reward:.3f}")
        done = terminated or truncated

    result = info["result"]
    print("=" * 88)
    print(f"Result: {'WIN' if result.won else 'LOSS'}")
    print(f"Final HP: {result.final_hp}/{80} | total HP loss: {result.total_hp_lost} | combats won: {result.combats_won}/7")
    print(f"Picks: {card_names([p for p in result.picks if p != 'skip'])}, skips={result.picks.count('skip')}")
    print(f"Upgrades: {result.upgrades} | rests: {result.rests}")
    print(f"Final deck({len(result.deck)}): {card_names(result.deck)}")


if __name__ == "__main__":
    main()
