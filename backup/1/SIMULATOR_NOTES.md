# STS2 Headless Simulator Notes

## Goal

Build a clean, fast, no-UI combat simulator that uses the decompiled game files as rule references, without copying the game implementation.

The simulator is intentionally single-player first. Decompiled multiplayer-specific logic such as net actions, synchronization, voting, and multiplayer scaling is out of scope unless it affects a single-player rule.

## Current Scope

The simulator can already run complete combats with:

- player HP, block, energy
- draw pile, hand, discard pile, exhaust pile
- draw, shuffle, discard, exhaust, ethereal
- single-target attacks
- all-enemy attacks
- multi-hit attacks
- block gain
- card draw
- generated cards into discard or hand
- status/curse cards used by current encounters
- strength, dexterity, vulnerable, weak
- Power hooks for card played, card exhausted, block gained, player turn end, and block clearing
- damage hooks for HP-loss modification, damage received, and enemy turn end
- enemy intents and simple move state machines
- Ritual-style enemy scaling
- random and simple baseline agents
- batch evaluation metrics

## Implemented Card Samples

- Strike
- Defend
- Bash
- Ascender's Bane
- Slimed
- Anger
- Pommel Strike
- Shrug It Off
- Inflame
- Thunderclap
- Twin Strike
- Barricade
- Feel No Pain
- Rage
- Dark Embrace
- Juggernaut
- Flame Barrier
- Buffer Debug
- Intangible Debug

The `Debug` cards are temporary harness cards for validating generic powers before their real source cards are migrated.

## Implemented Encounter Samples

- Small Twig Slime
- Small Leaf Slime
- Medium Twig Slime
- Calcified Cultist

## Full Compatibility Plan

Full card compatibility is possible, but it should be done incrementally:

1. Keep expanding generic effects before adding many cards.
2. Add Power hooks for combat start, turn start, turn end, card played, card drawn, damage dealt, damage received, and death.
3. Add choice effects for cards that ask the player to discard, exhaust, select from piles, or choose generated cards.
4. Add per-card custom handlers only when a card cannot be represented with generic effects.
5. Migrate one card pool at a time, starting with Ironclad.
6. Add automated checks that each migrated card can be played in a smoke-test combat.

The intended shape is data-first: most cards should be `CardDef` data plus generic effects, while unusual cards get a small custom handler.
