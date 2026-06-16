from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


CardType = Literal["attack", "skill", "power", "status", "curse"]
TargetType = Literal["enemy", "all_enemies", "self", "none"]


SINGLE_STACK_POWERS = frozenset({
    "barricade",
    "corruption",
    "hellraiser",
    "minion",
    "no_draw",
    "no_energy_gain",
    "smoggy",
})


DEBUFF_POWERS = frozenset({
    "vulnerable",
    "weak",
    "frail",
    "no_draw",
    "no_energy_gain",
    "smoggy",
})


@dataclass(frozen=True)
class CardDef:
    id: str
    name: str
    cost: int
    card_type: CardType
    target: TargetType
    effects: tuple[dict[str, Any], ...] = ()
    keywords: frozenset[str] = frozenset()
    exhausts_when_played: bool = False
    upgraded_id: str | None = None
    rarity: str = "common"


@dataclass
class CardInstance:
    def_id: str
    misc: int = 0
    free_this_turn: bool = False


@dataclass
class Creature:
    name: str
    max_hp: int
    hp: int
    block: int = 0
    powers: dict[str, int] = field(default_factory=dict)

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def gain_block(self, amount: int) -> None:
        self.block += max(0, amount)

    def add_power(self, power: str, amount: int) -> None:
        if amount == 0:
            return
        is_debuff = power in DEBUFF_POWERS or (power in {"strength", "dexterity"} and amount < 0)
        if is_debuff and self.power_amount("artifact") > 0:
            self.powers["artifact"] -= 1
            if self.powers["artifact"] <= 0:
                del self.powers["artifact"]
            return
        if power in SINGLE_STACK_POWERS and amount > 0 and power in self.powers:
            self.powers[power] = max(self.powers[power], amount)
            return
        self.powers[power] = self.powers.get(power, 0) + amount
        if self.powers[power] == 0 or (self.powers[power] < 0 and power not in {"strength", "dexterity"}):
            del self.powers[power]

    def power_amount(self, power: str) -> int:
        return self.powers.get(power, 0)


@dataclass(frozen=True)
class EnemyMove:
    id: str
    intent: str
    damage: int = 0
    hits: int = 1
    block: int = 0
    add_card_id: str | None = None
    add_card_count: int = 0
    apply_power: str | None = None
    apply_power_amount: int = 0
    apply_power_after_damage: bool = False
    apply_player_power: str | None = None
    apply_player_power_amount: int = 0
    extra_player_powers: tuple[tuple[str, int], ...] = ()
    heal: int = 0
    summon: tuple[str, ...] = ()
    self_kill: bool = False
    escape: bool = False


@dataclass(frozen=True)
class EnemyDef:
    id: str
    name: str
    min_hp: int
    max_hp: int
    ai: str
    moves: tuple[EnemyMove, ...]
    initial_powers: tuple[tuple[str, int], ...] = ()


@dataclass
class EnemyState:
    definition: EnemyDef
    creature: Creature
    move_index: int = 0
    last_move_id: str | None = None
    ritual_just_applied: bool = False
    death_processed: bool = False
    vars: dict[str, int] = field(default_factory=dict)

    @property
    def alive(self) -> bool:
        return self.creature.alive
