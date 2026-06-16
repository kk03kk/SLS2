from __future__ import annotations

import random
from dataclasses import dataclass

from sts2_sim.cards import (
    CARD_LIBRARY,
    IRONCLAD_CARD_RARITIES,
    ironclad_a0_starting_deck,
    ironclad_singleplayer_reward_pool,
)
from sts2_sim.data import EnemyDef
from sts2_sim.enemies import (
    ENEMY_LIBRARY,
    UNDERDOCKS_BOSS_ENCOUNTERS,
    UNDERDOCKS_ELITE_ENCOUNTERS,
    UNDERDOCKS_REGULAR_ENCOUNTERS,
    UNDERDOCKS_WEAK_ENCOUNTERS,
)


@dataclass(frozen=True)
class BattleScenario:
    deck: list[str]
    enemies: list[EnemyDef]
    player_hp: int
    player_max_hp: int
    encounter_id: str
    stage: str


STAGE_ENCOUNTERS: dict[str, dict[str, list[str]]] = {
    "weak": UNDERDOCKS_WEAK_ENCOUNTERS,
    "regular": UNDERDOCKS_REGULAR_ENCOUNTERS,
    "elite": UNDERDOCKS_ELITE_ENCOUNTERS,
    "boss": UNDERDOCKS_BOSS_ENCOUNTERS,
}


RARITY_WEIGHTS = {
    "common": 0.65,
    "uncommon": 0.28,
    "rare": 0.07,
}


def all_battle_card_ids() -> tuple[str, ...]:
    return tuple(sorted(CARD_LIBRARY))


def sample_reward_card(rng: random.Random) -> str:
    pool = ironclad_singleplayer_reward_pool()
    weights = [RARITY_WEIGHTS.get(IRONCLAD_CARD_RARITIES.get(card_id, "common"), 0.2) for card_id in pool]
    return rng.choices(pool, weights=weights, k=1)[0]


def maybe_upgrade(card_id: str, rng: random.Random, upgrade_chance: float) -> str:
    upgraded_id = CARD_LIBRARY[card_id].upgraded_id
    if upgraded_id is not None and rng.random() < upgrade_chance:
        return upgraded_id
    return card_id


def sample_ironclad_deck(
    rng: random.Random,
    *,
    min_bonus_cards: int = 0,
    max_bonus_cards: int = 15,
    upgrade_chance: float = 0.18,
) -> list[str]:
    deck = list(ironclad_a0_starting_deck())
    bonus_count = rng.randint(min_bonus_cards, max_bonus_cards)
    for _ in range(bonus_count):
        deck.append(maybe_upgrade(sample_reward_card(rng), rng, upgrade_chance))
    for idx, card_id in enumerate(deck):
        deck[idx] = maybe_upgrade(card_id, rng, upgrade_chance * 0.25)
    rng.shuffle(deck)
    return deck


def stage_for_curriculum(curriculum: str, episode_index: int, rng: random.Random) -> str:
    if curriculum == "all":
        return rng.choices(["weak", "regular", "elite", "boss"], weights=[0.25, 0.4, 0.25, 0.1], k=1)[0]
    if curriculum in STAGE_ENCOUNTERS:
        return curriculum
    raise ValueError(f"Unknown battle stage: {curriculum}")


def sample_encounter(rng: random.Random, stage: str) -> tuple[str, list[EnemyDef]]:
    if stage == "all":
        encounter_pool = {
            **UNDERDOCKS_WEAK_ENCOUNTERS,
            **UNDERDOCKS_REGULAR_ENCOUNTERS,
            **UNDERDOCKS_ELITE_ENCOUNTERS,
            **UNDERDOCKS_BOSS_ENCOUNTERS,
        }
    else:
        encounter_pool = STAGE_ENCOUNTERS[stage]
    encounter_id = rng.choice(tuple(encounter_pool))
    enemies = [ENEMY_LIBRARY[enemy_id] for enemy_id in encounter_pool[encounter_id]]
    return encounter_id, enemies


def sample_battle_scenario(
    rng: random.Random,
    *,
    stage: str,
    episode_index: int,
    min_bonus_cards: int = 0,
    max_bonus_cards: int = 15,
) -> BattleScenario:
    actual_stage = stage_for_curriculum(stage, episode_index, rng)
    max_hp = rng.randint(68, 82)
    player_hp = rng.randint(max(1, int(max_hp * 0.35)), max_hp)
    deck = sample_ironclad_deck(
        rng,
        min_bonus_cards=min_bonus_cards,
        max_bonus_cards=max_bonus_cards,
        upgrade_chance=0.12 if actual_stage == "weak" else 0.22,
    )
    encounter_id, enemies = sample_encounter(rng, actual_stage)
    return BattleScenario(
        deck=deck,
        enemies=enemies,
        player_hp=player_hp,
        player_max_hp=max_hp,
        encounter_id=encounter_id,
        stage=actual_stage,
    )
