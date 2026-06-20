from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECOMPILED = ROOT / "decompiled"
READ = ROOT / "READ"
OUT = ROOT / "sls2_rl" / "generated_data"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_cards() -> list[dict]:
    pool_by_card: dict[str, str] = {}
    for path in (DECOMPILED / "MegaCrit.Sts2.Core.Models.CardPools").glob("*CardPool.cs"):
        text = read(path)
        title = re.search(r'public override string Title => "([^"]+)"', text)
        pool = title.group(1) if title else path.stem.replace("CardPool", "").lower()
        for name in re.findall(r"ModelDb\.Card<([A-Za-z0-9_]+)>\(\)", text):
            pool_by_card[name] = pool

    cards = []
    for path in (DECOMPILED / "MegaCrit.Sts2.Core.Models.Cards").glob("*.cs"):
        text = read(path)
        cls = re.search(r"public sealed class ([A-Za-z0-9_]+) : CardModel", text)
        ctor = re.search(r": base\((-?\d+), CardType\.([A-Za-z]+), CardRarity\.([A-Za-z]+), TargetType\.([A-Za-z]+)\)", text)
        if not cls or not ctor:
            continue
        vars_found = []
        for m in re.finditer(r"new (?:(DamageVar|BlockVar)\((-?\d+(?:\.\d+)?)m|PowerVar<([A-Za-z0-9_]+)>\((-?\d+(?:\.\d+)?)m)", text):
            if m.group(1):
                vars_found.append({"kind": m.group(1).replace("Var", ""), "value": float(m.group(2))})
            else:
                vars_found.append({"kind": m.group(3), "value": float(m.group(4))})
        cards.append(
            {
                "id": cls.group(1),
                "cost": int(ctor.group(1)),
                "type": ctor.group(2),
                "rarity": ctor.group(3),
                "target": ctor.group(4),
                "pool": pool_by_card.get(cls.group(1), "unknown"),
                "vars": vars_found,
                "source": str(path.relative_to(ROOT)),
            }
        )
    return sorted(cards, key=lambda c: (c["pool"], c["id"]))


def extract_enemies() -> list[dict]:
    enemies = []
    for path in (DECOMPILED / "MegaCrit.Sts2.Core.Models.Monsters").glob("*.cs"):
        text = read(path)
        cls = re.search(r"public (?:sealed )?class ([A-Za-z0-9_]+) : MonsterModel", text)
        if not cls:
            continue
        min_hp = re.search(r"public override int MinInitialHp => .*?(\d+)\)?;", text)
        max_hp = re.search(r"public override int MaxInitialHp => .*?(\d+)\)?;", text)
        intents = sorted(set(re.findall(r"new (?:SingleAttackIntent|MultiAttackIntent|BuffIntent|DebuffIntent|BlockIntent)\(([^)]*)\)", text)))
        enemies.append(
            {
                "id": cls.group(1),
                "min_hp_raw": min_hp.group(0).split("=>", 1)[1].strip(" ;") if min_hp else "",
                "max_hp_raw": max_hp.group(0).split("=>", 1)[1].strip(" ;") if max_hp else "",
                "intent_args": intents,
                "source": str(path.relative_to(ROOT)),
            }
        )
    return sorted(enemies, key=lambda e: e["id"])


def extract_encounters() -> list[dict]:
    encounters = []
    for path in (DECOMPILED / "MegaCrit.Sts2.Core.Models.Encounters").glob("*.cs"):
        text = read(path)
        cls = re.search(r"public sealed class ([A-Za-z0-9_]+) : EncounterModel", text)
        if not cls:
            continue
        monsters = sorted(set(re.findall(r"ModelDb\.Monster<([A-Za-z0-9_]+)>\(\)", text)))
        room = re.search(r"RoomType => RoomType\.([A-Za-z]+)", text)
        is_weak = "public override bool IsWeak => true" in text
        encounters.append(
            {
                "id": cls.group(1),
                "room_type": room.group(1) if room else "",
                "is_weak": is_weak,
                "monsters": monsters,
                "source": str(path.relative_to(ROOT)),
            }
        )
    return sorted(encounters, key=lambda e: e["id"])


def write_markdown(cards: list[dict], enemies: list[dict], encounters: list[dict]) -> None:
    READ.mkdir(exist_ok=True)
    by_pool: dict[str, list[dict]] = {}
    for card in cards:
        by_pool.setdefault(card["pool"], []).append(card)
    lines = ["# 卡牌数据抽取\n", "来源：`decompiled/MegaCrit.Sts2.Core.Models.Cards` 与 `CardPools`。当前环境先实现战士核心子集，其余卡牌已抽取基础元数据，后续逐张补效果。\n"]
    for pool, items in sorted(by_pool.items()):
        lines.append(f"\n## {pool} ({len(items)})\n")
        lines.append("| id | cost | type | rarity | target | vars |\n| --- | ---: | --- | --- | --- | --- |\n")
        for c in items:
            vars_text = ", ".join(f"{v['kind']}={v['value']:g}" for v in c["vars"])
            lines.append(f"| {c['id']} | {c['cost']} | {c['type']} | {c['rarity']} | {c['target']} | {vars_text} |\n")
    (READ / "Cards.md").write_text("".join(lines), encoding="utf-8")

    lines = ["# 敌人与遭遇数据抽取\n", "来源：`Models.Monsters` 与 `Models.Encounters`。复杂状态机的精确动作需要后续逐怪物翻译，本文件先记录 HP 表达式、意图片段、遭遇组成。\n\n"]
    lines.append(f"## 敌人 ({len(enemies)})\n")
    lines.append("| id | min hp raw | max hp raw | intent snippets |\n| --- | --- | --- | --- |\n")
    for e in enemies:
        intents = "<br>".join(e["intent_args"][:4])
        lines.append(f"| {e['id']} | `{e['min_hp_raw']}` | `{e['max_hp_raw']}` | `{intents}` |\n")
    lines.append(f"\n## 遭遇 ({len(encounters)})\n")
    lines.append("| id | room | weak | monsters |\n| --- | --- | --- | --- |\n")
    for enc in encounters:
        lines.append(f"| {enc['id']} | {enc['room_type']} | {enc['is_weak']} | {', '.join(enc['monsters'])} |\n")
    (READ / "Enemies.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cards = extract_cards()
    enemies = extract_enemies()
    encounters = extract_encounters()
    (OUT / "cards.json").write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "enemies.json").write_text(json.dumps(enemies, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "encounters.json").write_text(json.dumps(encounters, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(cards, enemies, encounters)
    print(f"cards={len(cards)} enemies={len(enemies)} encounters={len(encounters)}")


if __name__ == "__main__":
    main()
