from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from sts2_sim.data import CardDef, CardInstance, Creature

if TYPE_CHECKING:
    from sts2_sim.engine import CombatEnv


@dataclass
class PowerContext:
    data: dict[str, int] = field(default_factory=dict)


PowerHook = Callable[..., None]


class PowerRegistry:
    def __init__(self) -> None:
        self.after_card_played: dict[str, PowerHook] = {}
        self.after_card_exhausted: dict[str, PowerHook] = {}
        self.after_block_gained: dict[str, PowerHook] = {}
        self.modify_hp_loss: dict[str, PowerHook] = {}
        self.after_damage_received: dict[str, PowerHook] = {}
        self.after_hp_lost: dict[str, PowerHook] = {}
        self.after_player_turn_start: dict[str, PowerHook] = {}
        self.after_player_turn_end: dict[str, PowerHook] = {}
        self.after_enemy_turn_end: dict[str, PowerHook] = {}
        self.should_clear_block: dict[str, Callable[[Creature], bool]] = {}


POWER_REGISTRY = PowerRegistry()


def register_after_card_played(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_card_played[power_id] = fn
        return fn

    return decorate


def register_after_card_exhausted(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_card_exhausted[power_id] = fn
        return fn

    return decorate


def register_after_block_gained(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_block_gained[power_id] = fn
        return fn

    return decorate


def register_modify_hp_loss(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.modify_hp_loss[power_id] = fn
        return fn

    return decorate


def register_after_damage_received(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_damage_received[power_id] = fn
        return fn

    return decorate


def register_after_hp_lost(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_hp_lost[power_id] = fn
        return fn

    return decorate


def register_after_player_turn_start(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_player_turn_start[power_id] = fn
        return fn

    return decorate


def register_after_player_turn_end(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_player_turn_end[power_id] = fn
        return fn

    return decorate


def register_after_enemy_turn_end(power_id: str):
    def decorate(fn: PowerHook) -> PowerHook:
        POWER_REGISTRY.after_enemy_turn_end[power_id] = fn
        return fn

    return decorate


def register_should_clear_block(power_id: str):
    def decorate(fn: Callable[[Creature], bool]) -> Callable[[Creature], bool]:
        POWER_REGISTRY.should_clear_block[power_id] = fn
        return fn

    return decorate


@register_should_clear_block("barricade")
def _barricade_should_clear_block(owner: Creature) -> bool:
    return False


@register_after_card_exhausted("feel_no_pain")
def _feel_no_pain_after_exhaust(env: "CombatEnv", owner: Creature, amount: int, card: CardDef, caused_by_ethereal: bool) -> None:
    env.gain_block(owner, amount, source="Feel No Pain", counts_for_unmovable=False)


@register_after_card_played("rage")
def _rage_after_card_played(env: "CombatEnv", owner: Creature, amount: int, card: CardDef) -> None:
    if card.card_type == "attack":
        env.gain_block(owner, amount, source="Rage", counts_for_unmovable=False)


@register_after_card_played("juggling")
def _juggling_after_card_played(env: "CombatEnv", owner: Creature, amount: int, card: CardDef) -> None:
    if card.card_type != "attack":
        return
    context = env.power_context(owner, "juggling")
    context.data["attacks_played"] = context.data.get("attacks_played", 0) + 1
    if context.data["attacks_played"] == 3:
        for _ in range(amount):
            misc = env.last_played_card_instance.misc if env.last_played_card_instance is not None else 0
            env.add_to_hand(CardInstance(card.id, misc=misc), source="Juggling")
        env.log.append(f"Juggling creates {amount} {card.name}")


@register_after_card_played("smoggy")
def _smoggy_after_card_played(env: "CombatEnv", owner: Creature, amount: int, card: CardDef) -> None:
    if owner != env.player or card.card_type != "skill":
        return
    env.power_context(owner, "smoggy").data["skill_locked"] = 1
    env.log.append("Smoggy clouds the remaining skills")


@register_after_player_turn_end("rage")
def _rage_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.powers.pop("rage", None)
    env.log.append("Rage wears off")


@register_after_player_turn_end("no_draw")
def _no_draw_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.powers.pop("no_draw", None)
    env.log.append("No Draw wears off")


@register_after_player_turn_end("juggling")
def _juggling_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    env.power_context(owner, "juggling").data["attacks_played"] = 0


@register_after_player_turn_end("no_energy_gain")
def _no_energy_gain_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.powers.pop("no_energy_gain", None)
    env.log.append("No Energy Gain wears off")


@register_after_player_turn_end("one_two_punch")
def _one_two_punch_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.powers.pop("one_two_punch", None)
    env.log.append("One Two Punch wears off")


@register_after_player_turn_end("smoggy")
def _smoggy_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    env.power_context(owner, "smoggy").data["skill_locked"] = 0


@register_after_player_turn_start("demon_form")
def _demon_form_after_turn_start(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.add_power("strength", amount)
    env.log.append(f"Demon Form grants {amount} Strength")


@register_after_player_turn_start("aggression")
def _aggression_after_turn_start(env: "CombatEnv", owner: Creature, amount: int) -> None:
    attack_indices = [
        idx for idx, card_instance in enumerate(env.discard_pile)
        if env.card_def(card_instance.def_id).card_type == "attack"
    ]
    env.rng.shuffle(attack_indices)
    moved = 0
    for idx in sorted(attack_indices[:amount], reverse=True):
        card_instance = env.discard_pile.pop(idx)
        env.add_to_hand(card_instance, source="Aggression")
        if env.is_upgradable(card_instance.def_id):
            env.upgrade_card_instance(card_instance)
        moved += 1
    if moved:
        env.log.append(f"Aggression returns {moved} attack card(s)")


@register_after_player_turn_start("crimson_mantle")
def _crimson_mantle_after_turn_start(env: "CombatEnv", owner: Creature, amount: int) -> None:
    self_damage = env.power_context(owner, "crimson_mantle").data.get("self_damage", 1)
    env.lose_hp(owner, self_damage, source=None)
    env.gain_block(owner, amount, source="Crimson Mantle", counts_for_unmovable=False)


@register_after_player_turn_start("inferno")
def _inferno_after_turn_start(env: "CombatEnv", owner: Creature, amount: int) -> None:
    self_damage = env.power_context(owner, "inferno").data.get("self_damage", 1)
    env.lose_hp(owner, self_damage, source=None)


@register_after_player_turn_start("plating")
def _plating_after_turn_start(env: "CombatEnv", owner: Creature, amount: int) -> None:
    if env.turn > 1:
        owner.add_power("plating", -1)


@register_after_player_turn_end("plating")
def _plating_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    env.gain_block(owner, amount, source="Stone Armor", counts_for_unmovable=False)


@register_after_enemy_turn_end("plating")
def _plating_after_enemy_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    if owner != env.player and owner.alive:
        env.enemy_gain_block(owner, amount, source="Plating")


@register_after_hp_lost("inferno")
def _inferno_after_hp_lost(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, source: CardDef | None) -> None:
    return


@register_after_damage_received("inferno")
def _inferno_after_damage_received(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> None:
    if hp_loss <= 0 or env.current_side != "player":
        return
    for enemy in env.alive_enemies():
        dealt = env.deal_damage(enemy.creature, amount)
        env.log.append(f"Inferno deals {dealt} to {enemy.creature.name}")


@register_after_hp_lost("rupture")
def _rupture_after_hp_lost(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, source: CardDef | None) -> None:
    if hp_loss <= 0 or env.current_side != "player":
        return
    if source is not None and source == env.current_card_def:
        env.pending_rupture_strength += amount
    else:
        owner.add_power("strength", amount)
        env.log.append(f"Rupture grants {amount} Strength")


@register_after_card_exhausted("dark_embrace")
def _dark_embrace_after_exhaust(env: "CombatEnv", owner: Creature, amount: int, card: CardDef, caused_by_ethereal: bool) -> None:
    if caused_by_ethereal:
        context = env.power_context(owner, "dark_embrace")
        context.data["ethereal_count"] = context.data.get("ethereal_count", 0) + 1
    else:
        env.draw_cards(amount)


@register_after_player_turn_end("dark_embrace")
def _dark_embrace_after_turn_end(env: "CombatEnv", owner: Creature, amount: int) -> None:
    context = env.power_context(owner, "dark_embrace")
    ethereal_count = context.data.get("ethereal_count", 0)
    if ethereal_count:
        env.draw_cards(amount * ethereal_count)
        context.data["ethereal_count"] = 0


@register_after_block_gained("juggernaut")
def _juggernaut_after_block(env: "CombatEnv", owner: Creature, amount: int, block_amount: int) -> None:
    if block_amount <= 0:
        return
    targets = env.alive_enemies()
    if not targets:
        return
    enemy = env.rng.choice(targets)
    dealt = env.deal_damage(enemy.creature, amount)
    env.log.append(f"Juggernaut deals {dealt} to {enemy.creature.name}")


@register_after_damage_received("flame_barrier")
def _flame_barrier_after_damage(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> None:
    if dealer is None:
        return
    dealt = env.deal_damage_from(dealer, amount, dealer=None)
    env.log.append(f"Flame Barrier deals {dealt} to {dealer.name}")


@register_after_damage_received("shriek")
def _shriek_after_damage(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> None:
    if hp_loss <= 0 or owner.hp > amount:
        return
    for enemy in env.enemies:
        if enemy.creature == owner and enemy.definition.ai == "terror_eel":
            enemy.move_index = 2
            owner.powers.pop("shriek", None)
            env.log.append(f"{owner.name}'s Shriek triggers a stun")
            return


@register_after_damage_received("asleep")
def _asleep_after_damage(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> None:
    if hp_loss <= 0 or owner == env.player:
        return
    owner.powers.pop("plating", None)
    owner.powers.pop("asleep", None)
    for enemy in env.enemies:
        if enemy.creature == owner and enemy.definition.ai == "lagavulin_matriarch":
            enemy.vars["wake_stun"] = 1
            enemy.move_index = 1
            env.log.append(f"{owner.name} wakes up")
            return


@register_after_damage_received("skittish")
def _skittish_after_damage(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> None:
    if hp_loss <= 0 or owner == env.player or env.current_side != "player" or env.current_card_def is None:
        return
    context = env.power_context(owner, "skittish")
    if context.data.get("blocked_this_turn", 0):
        return
    context.data["blocked_this_turn"] = 1
    env.enemy_gain_block(owner, amount, source="Skittish")


@register_after_damage_received("thorns")
def _thorns_after_damage(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> None:
    if dealer is None:
        return
    dealt = env.deal_damage_from(dealer, amount, dealer=None)
    env.log.append(f"{owner.name}'s Thorns deals {dealt} to {dealer.name}")


@register_after_enemy_turn_end("flame_barrier")
def _flame_barrier_after_enemy_turn(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.powers.pop("flame_barrier", None)
    env.log.append("Flame Barrier wears off")


@register_modify_hp_loss("buffer")
def _buffer_modify_hp_loss(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> int:
    if hp_loss <= 0:
        return hp_loss
    owner.add_power("buffer", -1)
    env.log.append("Buffer prevents HP loss")
    return 0


@register_modify_hp_loss("intangible")
def _intangible_modify_hp_loss(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> int:
    if hp_loss <= 1:
        return hp_loss
    env.log.append("Intangible reduces HP loss to 1")
    return 1


@register_modify_hp_loss("hardened_shell")
def _hardened_shell_modify_hp_loss(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> int:
    if hp_loss <= 0:
        return hp_loss
    context = env.power_context(owner, "hardened_shell")
    received = context.data.get("damage_received_this_turn", 0)
    remaining = max(0, amount - received)
    return min(hp_loss, remaining)


@register_after_damage_received("hardened_shell")
def _hardened_shell_after_damage(env: "CombatEnv", owner: Creature, amount: int, hp_loss: int, dealer: Creature | None) -> None:
    if hp_loss <= 0:
        return
    context = env.power_context(owner, "hardened_shell")
    context.data["damage_received_this_turn"] = context.data.get("damage_received_this_turn", 0) + hp_loss


@register_after_enemy_turn_end("intangible")
def _intangible_after_enemy_turn(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.add_power("intangible", -1)


@register_after_enemy_turn_end("colossus")
def _colossus_after_enemy_turn(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.add_power("colossus", -1)


@register_after_enemy_turn_end("mangle_strength_down")
def _mangle_after_enemy_turn(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.add_power("strength", amount)
    owner.powers.pop("mangle_strength_down", None)
    env.log.append(f"Mangle strength loss wears off on {owner.name}")


@register_after_player_turn_end("setup_strike_strength")
def _setup_strike_after_player_turn(env: "CombatEnv", owner: Creature, amount: int) -> None:
    owner.add_power("strength", -amount)
    owner.powers.pop("setup_strike_strength", None)
    env.log.append("Setup Strike Strength wears off")
