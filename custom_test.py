from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv
from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.data import CardInstance, Creature
from sts2_sim.engine import CombatEnv
from sts2_sim.enemies import ENCOUNTERS, ENEMY_LIBRARY


# =========================
MODEL_PATH = "battle_ai_models/ppo_generic_battle.zip"
OUTPUT_PATH = "battle_ai_reports/custom_battle_trace.txt"
SEED = 999
PLAYER_HP = 80
PLAYER_MAX_HP = 80
MAX_TURNS = 80

ENCOUNTER_ID = "sludge_spinner_weak"

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


def card_name(card_id: str) -> str:
    return CARD_LIBRARY[card_id].name


def instance_name(card: CardInstance) -> str:
    return card_name(card.def_id)


def deck_names(card_ids: list[str]) -> list[str]:
    return [card_name(card_id) for card_id in card_ids]


def format_powers(creature: Creature) -> str:
    if not creature.powers:
        return "-"
    return ", ".join(f"{power}:{amount}" for power, amount in sorted(creature.powers.items()))


def format_hand(env: CombatEnv) -> str:
    if not env.hand:
        return "(empty)"
    return " | ".join(
        f"[{idx}] {instance_name(card)} cost={env.effective_cost(CARD_LIBRARY[card.def_id], card)}"
        for idx, card in enumerate(env.hand)
    )


def format_pile(pile: list[CardInstance], *, limit: int = 12) -> str:
    if not pile:
        return "(empty)"
    names = [instance_name(card) for card in pile]
    shown = names[:limit]
    suffix = "" if len(names) <= limit else f" ... +{len(names) - limit}"
    return ", ".join(shown) + suffix


def format_player(env: CombatEnv) -> str:
    player = env.player
    return (
        f"HP {player.hp}/{player.max_hp}, block {player.block}, energy {env.energy}, "
        f"powers [{format_powers(player)}]"
    )


def format_enemies(env: CombatEnv) -> list[str]:
    rows = []
    for idx, enemy in enumerate(env.enemies):
        creature = enemy.creature
        if enemy.alive:
            move = env.current_enemy_move(enemy)
            status = f"intent {move.intent} ({move.id})"
        else:
            status = "dead"
        rows.append(
            f"[{idx}] {creature.name}: HP {creature.hp}/{creature.max_hp}, block {creature.block}, "
            f"powers [{format_powers(creature)}], {status}"
        )
    return rows


def append_section(lines: list[str], title: str) -> None:
    lines.append("")
    lines.append(title)
    lines.append("-" * len(title))


def append_state(lines: list[str], env: CombatEnv, *, label: str) -> None:
    lines.append(f"{label}:")
    lines.append(f"  Player: {format_player(env)}")
    lines.append("  Enemies:")
    for row in format_enemies(env):
        lines.append(f"    {row}")
    lines.append(f"  Hand: {format_hand(env)}")
    lines.append(
        f"  Piles: draw={len(env.draw_pile)} [{format_pile(env.draw_pile)}]; "
        f"discard={len(env.discard_pile)} [{format_pile(env.discard_pile)}]; "
        f"exhaust={len(env.exhaust_pile)} [{format_pile(env.exhaust_pile)}]"
    )


def append_log_entries(lines: list[str], entries: list[str]) -> None:
    if not entries:
        lines.append("  Log: (no new events)")
        return
    lines.append("  Log:")
    for entry in entries:
        lines.append(f"    - {entry}")


def validate_setup(deck: list[str], encounter_id: str) -> None:
    if encounter_id not in ENCOUNTERS:
        raise ValueError(f"Unknown encounter id: {encounter_id}")
    for card_id in deck:
        if card_id not in CARD_LIBRARY:
            raise ValueError(f"Unknown card id: {card_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one custom battle and write a readable battle trace.")
    parser.add_argument("--model-path", default=MODEL_PATH)
    parser.add_argument("--output-path", default=OUTPUT_PATH)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--encounter-id", default=ENCOUNTER_ID)
    parser.add_argument("--player-hp", type=int, default=PLAYER_HP)
    parser.add_argument("--player-max-hp", type=int, default=PLAYER_MAX_HP)
    parser.add_argument("--max-turns", type=int, default=MAX_TURNS)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--stochastic", action="store_true", help="Sample from the policy instead of greedy play.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    deck = list(DECK)
    validate_setup(deck, args.encounter_id)

    enemy_ids = ENCOUNTERS[args.encounter_id]
    enemies = [ENEMY_LIBRARY[enemy_id] for enemy_id in enemy_ids]
    wrapper = GenericBattlePPOEnv(seed=args.seed, stage="weak", max_turns=args.max_turns)
    model = MaskablePPO.load(args.model_path, env=wrapper, device=args.device)
    combat = CombatEnv(
        deck,
        enemies,
        player_hp=args.player_hp,
        player_max_hp=args.player_max_hp,
        seed=args.seed,
        max_turns=args.max_turns,
    )
    wrapper.env = combat
    wrapper.initial_enemy_hp = wrapper._enemy_hp_total(capped=True)
    obs = wrapper._obs()

    lines = [
        "Custom Battle Trace",
        "===================",
        f"Seed: {args.seed}",
        f"Model: {args.model_path}",
        f"Policy: {'stochastic' if args.stochastic else 'deterministic'}",
        f"Player HP: {args.player_hp}/{args.player_max_hp}",
        f"Encounter: {args.encounter_id}",
        f"Enemies: {[enemy.name for enemy in enemies]}",
        f"Deck ({len(deck)}): {deck_names(deck)}",
    ]

    append_section(lines, f"Turn {combat.turn} Start")
    append_log_entries(lines, combat.log)
    append_state(lines, combat, label="After opening draw")

    done = False
    info = {}
    step = 0
    current_turn = combat.turn
    while not done:
        if combat.turn != current_turn:
            current_turn = combat.turn
            append_section(lines, f"Turn {current_turn} Start")
            append_state(lines, combat, label="Start state")

        action, _ = model.predict(
            obs,
            deterministic=not args.stochastic,
            action_masks=wrapper.action_masks(),
        )
        action = int(action)
        action_text = wrapper.describe_action(action)
        before_log = len(combat.log)
        before_turn = combat.turn

        lines.append("")
        lines.append(f"Turn {before_turn}, Action {step + 1}: {action_text}")
        obs, reward, terminated, truncated, info = wrapper.step(action)
        append_log_entries(lines, combat.log[before_log:])
        lines.append(f"  Reward: {reward:.3f}")
        append_state(lines, combat, label="After action")

        done = terminated or truncated
        step += 1

    result = info["result"]
    append_section(lines, "Final Result")
    lines.append(
        f"Won: {result.won}; HP lost: {result.hp_lost}; final HP: {result.final_hp}; "
        f"turns: {result.turns}; enemies killed: {result.enemies_killed}; actions: {step}"
    )

    output = Path(args.output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(lines[-1])
    print(f"Saved trace: {output}")


if __name__ == "__main__":
    main()
