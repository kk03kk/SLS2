from __future__ import annotations

import random

from sts2_sim.cards import CARD_LIBRARY, IRONCLAD_SINGLEPLAYER_POOL
from sts2_sim.enemies import ENCOUNTERS, ENEMY_LIBRARY
from sts2_sim.engine import CombatEnv


IRONCLAD_SEAPUNK_42_DECK = (
    ["strike_ironclad"] * 3
    + ["defend_ironclad"] * 4
    + [
        "ascenders_bane",
        "bash",
        "sword_boomerang",
        "inflame",
        "headbutt",
        "thunderclap",
    ]
)

IRONCLAD_TERROR_EEL_A9_32_DECK = (
    ["strike_ironclad"] * 2
    + ["strike_ironclad_plus"] * 2
    + ["defend_ironclad"] * 3
    + [
        "bash",
        "ascenders_bane",
        "body_slam_plus",
        "stomp",
        "dominate",
        "headbutt",
        "armaments_plus",
        "anger",
    ]
)

IRONCLAD_A10_BASE_DECK = (
    ["strike_ironclad"] * 5
    + ["defend_ironclad"] * 4
    + ["bash"]
    + ["ascenders_bane"]
)

IRONCLAD_RANDOM_BONUS_CARD_POOL = tuple(
    card_id
    for card_id in IRONCLAD_SINGLEPLAYER_POOL
    if card_id not in {"strike_ironclad", "defend_ironclad", "bash"}
)


def ironclad_seapunk_42_deck() -> list[str]:
    return list(IRONCLAD_SEAPUNK_42_DECK)


def ironclad_terror_eel_a9_32_deck() -> list[str]:
    return list(IRONCLAD_TERROR_EEL_A9_32_DECK)


def ironclad_a10_base_deck() -> list[str]:
    return list(IRONCLAD_A10_BASE_DECK)


def ironclad_calcified_cultist_a10_bonus_deck(
    *,
    seed: int | None = None,
    extra_card_id: str | None = None,
) -> list[str]:
    if extra_card_id is None:
        extra_card_id = random.Random(seed).choice(IRONCLAD_RANDOM_BONUS_CARD_POOL)
    if extra_card_id not in IRONCLAD_RANDOM_BONUS_CARD_POOL:
        raise ValueError(f"Invalid Ironclad bonus card: {extra_card_id}")
    return ironclad_a10_base_deck() + [extra_card_id]


def build_enemies(encounter_id: str):
    return [ENEMY_LIBRARY[enemy_id] for enemy_id in ENCOUNTERS[encounter_id]]


def build_ironclad_seapunk_42_env(
    *,
    seed: int | None = None,
    max_turns: int = 30,
    enable_burning_blood: bool = False,
    extra_card_id: str | None = None,
) -> CombatEnv:
    return CombatEnv(
        ironclad_seapunk_42_deck(),
        build_enemies("seapunk_weak"),
        player_hp=42,
        seed=seed,
        max_turns=max_turns,
        enable_burning_blood=enable_burning_blood,
    )


def build_ironclad_terror_eel_a9_32_env(
    *,
    seed: int | None = None,
    max_turns: int = 40,
    enable_burning_blood: bool = False,
    extra_card_id: str | None = None,
) -> CombatEnv:
    return CombatEnv(
        ironclad_terror_eel_a9_32_deck(),
        build_enemies("terror_eel_a9_elite"),
        player_hp=32,
        seed=seed,
        max_turns=max_turns,
        enable_burning_blood=enable_burning_blood,
    )


def build_ironclad_calcified_cultist_a10_bonus_env(
    *,
    seed: int | None = None,
    max_turns: int = 30,
    enable_burning_blood: bool = False,
    extra_card_id: str | None = None,
) -> CombatEnv:
    return CombatEnv(
        ironclad_calcified_cultist_a10_bonus_deck(seed=seed, extra_card_id=extra_card_id),
        [ENEMY_LIBRARY["calcified_cultist_a10"]],
        player_hp=80,
        seed=seed,
        max_turns=max_turns,
        enable_burning_blood=enable_burning_blood,
    )


SCENARIO_BUILDERS = {
    "ironclad_seapunk_42": build_ironclad_seapunk_42_env,
    "ironclad_terror_eel_a9_32": build_ironclad_terror_eel_a9_32_env,
    "ironclad_calcified_cultist_a10_bonus": build_ironclad_calcified_cultist_a10_bonus_env,
}


SCENARIO_DECKS = {
    "ironclad_seapunk_42": ironclad_seapunk_42_deck,
    "ironclad_terror_eel_a9_32": ironclad_terror_eel_a9_32_deck,
    "ironclad_calcified_cultist_a10_bonus": ironclad_calcified_cultist_a10_bonus_deck,
}
