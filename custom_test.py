from __future__ import annotations

from pathlib import Path

from sb3_contrib import MaskablePPO

from battle_ai.env import GenericBattlePPOEnv
from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.engine import CombatEnv
from sts2_sim.enemies import ENCOUNTERS, ENEMY_LIBRARY


# =========================
MODEL_PATH = "battle_ai_models/ppo_generic_battle.zip"
OUTPUT_PATH = "battle_ai_reports/custom_battle_trace.txt"
SEED = 12
PLAYER_HP = 80
PLAYER_MAX_HP = 80
MAX_TURNS = 80

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


def names(card_ids: list[str]) -> list[str]:
    return [CARD_LIBRARY[card_id].name for card_id in card_ids]


def main() -> None:
    if ENCOUNTER_ID not in ENCOUNTERS:
        raise ValueError(f"Unknown encounter id: {ENCOUNTER_ID}")
    for card_id in DECK:
        if card_id not in CARD_LIBRARY:
            raise ValueError(f"Unknown card id: {card_id}")

    enemy_ids = ENCOUNTERS[ENCOUNTER_ID]
    enemies = [ENEMY_LIBRARY[enemy_id] for enemy_id in enemy_ids]
    wrapper = GenericBattlePPOEnv(seed=SEED, stage="weak", max_turns=MAX_TURNS)
    model = MaskablePPO.load(MODEL_PATH, env=wrapper, device="auto")
    combat = CombatEnv(
        list(DECK),
        enemies,
        player_hp=PLAYER_HP,
        player_max_hp=PLAYER_MAX_HP,
        seed=SEED,
        max_turns=MAX_TURNS,
    )
    wrapper.env = combat
    wrapper.initial_enemy_hp = wrapper._enemy_hp_total(capped=True)
    obs = wrapper._obs()

    lines = [
        f"Seed: {SEED}",
        f"Player HP: {PLAYER_HP}/{PLAYER_MAX_HP}",
        f"Encounter: {ENCOUNTER_ID}",
        f"Enemies: {[enemy.name for enemy in enemies]}",
        f"Deck({len(DECK)}): {names(DECK)}",
        "",
    ]

    done = False
    info = {}
    step = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True, action_masks=wrapper.action_masks())
        action = int(action)
        lines.append(f"Step {step}: {wrapper.describe_action(action)}")
        before = len(combat.log)
        obs, reward, terminated, truncated, info = wrapper.step(action)
        for entry in combat.log[before:]:
            lines.append(f"  {entry}")
        enemy_text = []
        for idx, enemy in enumerate(combat.enemies):
            status = "alive" if enemy.alive else "dead"
            enemy_text.append(f"{idx}:{enemy.creature.name} {enemy.creature.hp}/{enemy.creature.max_hp} {status}")
        lines.append(
            f"  reward={reward:.3f}, player={combat.player.hp}/{combat.player.max_hp}, "
            f"block={combat.player.block}, energy={combat.energy}, enemies={enemy_text}"
        )
        lines.append("")
        done = terminated or truncated
        step += 1

    result = info["result"]
    lines.append(
        f"Result: won={result.won}, hp_lost={result.hp_lost}, "
        f"final_hp={result.final_hp}, turns={result.turns}, enemies_killed={result.enemies_killed}"
    )
    output = Path(OUTPUT_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(lines[-1])
    print(f"Saved trace: {output}")


if __name__ == "__main__":
    main()
