from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable


@dataclass(frozen=True)
class CardDef:
    id: str
    cost: int
    type: str
    rarity: str
    target: str
    pool: str
    damage: int = 0
    block: int = 0
    vulnerable: int = 0
    weak: int = 0
    strength: int = 0
    draw: int = 0
    exhaust: bool = False
    note: str = ""

    def upgraded(self) -> "CardDef":
        upgrades = {
            "StrikeIronclad": {"damage": self.damage + 3},
            "DefendIronclad": {"block": self.block + 3},
            "Bash": {"damage": self.damage + 2, "vulnerable": self.vulnerable + 1},
            "PommelStrike": {"damage": self.damage + 1, "draw": self.draw + 1},
            "ShrugItOff": {"block": self.block + 3},
            "Inflame": {"strength": self.strength + 1},
            "TwinStrike": {"damage": self.damage + 4},
            "Thunderclap": {"damage": self.damage + 2},
            "IronWave": {"damage": self.damage + 2, "block": self.block + 2},
            "Uppercut": {"damage": self.damage + 3, "vulnerable": self.vulnerable + 1, "weak": self.weak + 1},
        }
        return replace(self, **upgrades.get(self.id, {}))


@dataclass(frozen=True)
class EnemyMove:
    id: str
    damage: int = 0
    hits: int = 1
    block: int = 0
    strength: int = 0
    vulnerable: int = 0
    weak: int = 0


MovePicker = Callable[[int], EnemyMove]


@dataclass(frozen=True)
class EnemyDef:
    id: str
    encounter_pool: str
    max_hp: int
    moves: tuple[EnemyMove, ...]
    note: str = ""

    def move_for_turn(self, turn: int) -> EnemyMove:
        return self.moves[turn % len(self.moves)]


CARDS: dict[str, CardDef] = {
    "StrikeIronclad": CardDef("StrikeIronclad", 1, "Attack", "Basic", "AnyEnemy", "ironclad", damage=6, note="decompiled exact: 6 damage, +3 upgrade"),
    "DefendIronclad": CardDef("DefendIronclad", 1, "Skill", "Basic", "Self", "ironclad", block=5, note="decompiled exact: 5 block, +3 upgrade"),
    "Bash": CardDef("Bash", 2, "Attack", "Basic", "AnyEnemy", "ironclad", damage=8, vulnerable=2, note="decompiled exact: 8 damage + 2 Vulnerable"),
    "PommelStrike": CardDef("PommelStrike", 1, "Attack", "Common", "AnyEnemy", "ironclad", damage=9, draw=1),
    "ShrugItOff": CardDef("ShrugItOff", 1, "Skill", "Common", "Self", "ironclad", block=8, draw=1),
    "Inflame": CardDef("Inflame", 1, "Power", "Uncommon", "Self", "ironclad", strength=2, exhaust=True),
    "TwinStrike": CardDef("TwinStrike", 1, "Attack", "Common", "AnyEnemy", "ironclad", damage=10, note="approximated as total damage"),
    "Thunderclap": CardDef("Thunderclap", 1, "Attack", "Common", "AllEnemies", "ironclad", damage=4, vulnerable=1),
    "IronWave": CardDef("IronWave", 1, "Attack", "Common", "AnyEnemy", "ironclad", damage=5, block=5),
    "Uppercut": CardDef("Uppercut", 2, "Attack", "Uncommon", "AnyEnemy", "ironclad", damage=13, vulnerable=1, weak=1),
    "Anger": CardDef("Anger", 0, "Attack", "Common", "AnyEnemy", "ironclad", damage=6),
    "PerfectedStrike": CardDef("PerfectedStrike", 2, "Attack", "Common", "AnyEnemy", "ironclad", damage=18, note="approximated for compact first environment"),
}

IRONCLAD_STARTER_DECK = (
    ["StrikeIronclad"] * 5
    + ["DefendIronclad"] * 4
    + ["Bash"]
)

IRONCLAD_REWARD_POOL = (
    "PommelStrike",
    "ShrugItOff",
    "Inflame",
    "TwinStrike",
    "Thunderclap",
    "IronWave",
    "Uppercut",
    "Anger",
    "PerfectedStrike",
)

ENEMIES: dict[str, EnemyDef] = {
    "TrainingJawWorm": EnemyDef(
        "TrainingJawWorm",
        "weak",
        42,
        (EnemyMove("CHOMP", damage=7), EnemyMove("BELLOW", strength=3, block=6), EnemyMove("THRASH", damage=11)),
        "STS-like weak proxy; used before full FuzzyWurmCrawler mechanics are implemented.",
    ),
    "FuzzyWurmCrawler": EnemyDef(
        "FuzzyWurmCrawler",
        "weak",
        56,
        (EnemyMove("ACID_GOOP", damage=4), EnemyMove("INHALE", strength=7)),
        "decompiled: 55-57 HP, AcidGoop 4, Inhale +7 Strength at A0.",
    ),
    "Cultist": EnemyDef(
        "Cultist",
        "weak",
        50,
        (EnemyMove("INCANTATION", strength=3), EnemyMove("DARK_STRIKE", damage=6), EnemyMove("DARK_STRIKE", damage=6)),
        "training proxy for scaling enemy behavior.",
    ),
    "SlimesWeak": EnemyDef(
        "SlimesWeak",
        "weak",
        36,
        (EnemyMove("LICK", weak=1), EnemyMove("TACKLE", damage=8)),
        "single-body proxy for multi-slime weak encounter.",
    ),
    "StrongPoolDummy": EnemyDef(
        "StrongPoolDummy",
        "strong",
        85,
        (EnemyMove("HEAVY", damage=14), EnemyMove("GUARD", block=12), EnemyMove("DOUBLE", damage=8, hits=2)),
    ),
    "EliteSentinel": EnemyDef(
        "EliteSentinel",
        "elite",
        120,
        (EnemyMove("OPENING", damage=18), EnemyMove("FORTIFY", block=15, strength=2), EnemyMove("BEAM", damage=10, hits=2)),
    ),
    "BossPrototype": EnemyDef(
        "BossPrototype",
        "boss",
        240,
        (EnemyMove("SLAM", damage=22), EnemyMove("CHARGE", strength=4, block=20), EnemyMove("BURST", damage=9, hits=3)),
    ),
}

ENCOUNTER_POOLS: dict[str, tuple[str, ...]] = {
    "weak": ("TrainingJawWorm", "FuzzyWurmCrawler", "Cultist", "SlimesWeak"),
    "strong": ("StrongPoolDummy",),
    "elite": ("EliteSentinel",),
    "boss": ("BossPrototype",),
}

