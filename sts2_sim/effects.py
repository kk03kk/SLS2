from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from sts2_sim.data import CardDef, Creature
from sts2_sim.data import CardInstance

if TYPE_CHECKING:
    from sts2_sim.engine import CombatEnv


EffectHandler = Callable[["CombatEnv", CardDef, dict[str, Any], Creature | None], None]


EFFECT_HANDLERS: dict[str, EffectHandler] = {}


def effect_handler(effect_type: str) -> Callable[[EffectHandler], EffectHandler]:
    def decorate(fn: EffectHandler) -> EffectHandler:
        EFFECT_HANDLERS[effect_type] = fn
        return fn

    return decorate


def apply_effect(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    effect_type = str(effect["type"])
    handler = EFFECT_HANDLERS.get(effect_type)
    if handler is None:
        raise ValueError(f"Unknown effect type: {effect_type}")
    handler(env, card, effect, target)


@effect_handler("deal_damage")
def _deal_damage(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError(f"{card.name} needs a damage target")
    hits = int(effect.get("hits", 1))
    for _ in range(hits):
        damage = env.calculate_damage(env.player, target, int(effect["amount"]))
        dealt = env.deal_damage(target, damage)
        env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("deal_damage_all")
def _deal_damage_all(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    hits = int(effect.get("hits", 1))
    for enemy in env.alive_enemies():
        for _ in range(hits):
            damage = env.calculate_damage(env.player, enemy.creature, int(effect["amount"]))
            dealt = env.deal_damage(enemy.creature, damage)
            env.log.append(f"{card.name} deals {dealt} to {enemy.creature.name}")


@effect_handler("gain_block")
def _gain_block(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    block = int(effect["amount"]) + env.player.power_amount("dexterity")
    if env.player.power_amount("frail") > 0:
        block = int(block * 0.75)
    env.gain_block(env.player, block, source=card.name)


@effect_handler("draw_cards")
def _draw_cards(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    env.draw_cards(int(effect["amount"]))


@effect_handler("gain_energy")
def _gain_energy(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    amount = int(effect["amount"])
    env.gain_energy(amount, source=card.name)


@effect_handler("lose_hp")
def _lose_hp(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    amount = int(effect["amount"])
    lost = env.lose_hp(env.player, amount, source=card)
    env.log.append(f"Player loses {lost} HP")


@effect_handler("apply_power")
def _apply_power(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    recipient = str(effect.get("recipient", "target"))
    actual_target = env.player if recipient == "self" else target
    if actual_target is None:
        raise ValueError(f"{card.name} needs a power target")
    power = str(effect["power"])
    amount = int(effect["amount"])
    actual_target.add_power(power, amount)
    if power in {"crimson_mantle", "inferno"}:
        context = env.power_context(actual_target, power)
        context.data["self_damage"] = context.data.get("self_damage", 0) + 1
    if power == "juggling" and actual_target == env.player:
        env.power_context(actual_target, "juggling").data["attacks_played"] = env.attacks_played_this_turn
    env.log.append(f"{actual_target.name} gains {power} {amount}")
    if power == "vulnerable" and actual_target != env.player and env.player.power_amount("vicious"):
        env.draw_cards(env.player.power_amount("vicious"))


@effect_handler("apply_power_all_enemies")
def _apply_power_all_enemies(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    power = str(effect["power"])
    amount = int(effect["amount"])
    for enemy in env.alive_enemies():
        enemy.creature.add_power(power, amount)
        env.log.append(f"{enemy.creature.name} gains {power} {amount}")
        if power == "vulnerable" and env.player.power_amount("vicious"):
            env.draw_cards(env.player.power_amount("vicious"))


@effect_handler("add_card_to_discard")
def _add_card_to_discard(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    card_id = str(effect["card_id"])
    count = int(effect.get("count", 1))
    for _ in range(count):
        env.discard_pile.append(CardInstance(card_id))
    env.log.append(f"{card.name} adds {count} {env.card_name(card_id)} to discard")


@effect_handler("add_card_to_hand")
def _add_card_to_hand(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    card_id = str(effect["card_id"])
    count = int(effect.get("count", 1))
    for _ in range(count):
        env.add_to_hand(CardInstance(card_id), source=card.name)
    env.log.append(f"{card.name} adds {count} {env.card_name(card_id)} to hand")


@effect_handler("exhaust_from_hand")
def _exhaust_from_hand(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    mode = str(effect.get("mode", "chosen"))
    candidates = env.hand_indices()
    if not candidates:
        return
    if mode == "random":
        hand_index = env.rng.choice(candidates)
    else:
        hand_index = env.choose_hand_card(candidates, purpose="exhaust")
    env.exhaust_from_hand(hand_index, caused_by_ethereal=False)


@effect_handler("upgrade_from_hand")
def _upgrade_from_hand(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    candidates = [idx for idx, card_instance in enumerate(env.hand) if env.is_upgradable(card_instance.def_id)]
    if not candidates:
        return
    if bool(effect.get("all", False)):
        for idx in reversed(candidates):
            env.upgrade_hand_card(idx)
    else:
        env.upgrade_hand_card(env.choose_hand_card(candidates, purpose="upgrade"))


@effect_handler("move_discard_to_draw_top")
def _move_discard_to_draw_top(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if not env.discard_pile:
        return
    idx = env.choose_pile_card(env.discard_pile, purpose="draw_top")
    card_instance = env.discard_pile.pop(idx)
    env.draw_pile.append(card_instance)
    env.log.append(f"{card.name} puts {env.card_name(card_instance.def_id)} on top of draw pile")


@effect_handler("exhaust_non_attacks_gain_block")
def _exhaust_non_attacks_gain_block(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    block = int(effect["block"])
    candidates = [
        idx for idx, card_id in enumerate(env.hand)
        if env.card_def(card_id.def_id).card_type != "attack"
    ]
    for idx in reversed(candidates):
        env.exhaust_from_hand(idx, caused_by_ethereal=False)
        env.gain_block(env.player, block, source=card.name)


@effect_handler("fiend_fire")
def _fiend_fire(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Fiend Fire needs a target")
    hit_count = len(env.hand)
    for idx in reversed(range(len(env.hand))):
        env.exhaust_from_hand(idx, caused_by_ethereal=False)
    for _ in range(hit_count):
        damage = env.calculate_damage(env.player, target, int(effect["amount"]))
        dealt = env.deal_damage(target, damage)
        env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("body_slam")
def _body_slam(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Body Slam needs a target")
    damage = env.calculate_damage(env.player, target, env.player.block)
    dealt = env.deal_damage(target, damage)
    env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("perfected_strike")
def _perfected_strike(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Perfected Strike needs a target")
    base = int(effect["base"])
    per_strike = int(effect["per_strike"])
    strike_count = sum(
        1 for card_instance in env.all_combat_cards(include_current=True)
        if "strike" in env.card_def(card_instance.def_id).keywords
    )
    damage = env.calculate_damage(env.player, target, base + per_strike * strike_count)
    dealt = env.deal_damage(target, damage)
    env.log.append(f"{card.name} deals {dealt} to {target.name} ({strike_count} Strike cards)")


@effect_handler("rampage")
def _rampage(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Rampage needs a target")
    card_instance = env.current_card_instance
    bonus = card_instance.misc if card_instance is not None else 0
    damage = env.calculate_damage(env.player, target, int(effect["amount"]) + bonus)
    dealt = env.deal_damage(target, damage)
    env.log.append(f"{card.name} deals {dealt} to {target.name}")
    if card_instance is not None:
        card_instance.misc += int(effect["increase"])
        env.log.append(f"{card.name} grows by {int(effect['increase'])} damage")


@effect_handler("whirlwind")
def _whirlwind(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    hits = env.energy
    env.energy = 0
    amount = int(effect["amount"])
    if hits <= 0:
        env.log.append("Whirlwind has no energy to spend")
        return
    for _ in range(hits):
        for enemy in env.alive_enemies():
            damage = env.calculate_damage(env.player, enemy.creature, amount)
            dealt = env.deal_damage(enemy.creature, damage)
            env.log.append(f"{card.name} deals {dealt} to {enemy.creature.name}")


@effect_handler("random_enemy_damage")
def _random_enemy_damage(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    hits = int(effect.get("hits", 1))
    amount = int(effect["amount"])
    for _ in range(hits):
        enemies = env.alive_enemies()
        if not enemies:
            return
        enemy = env.rng.choice(enemies)
        damage = env.calculate_damage(env.player, enemy.creature, amount)
        dealt = env.deal_damage(enemy.creature, damage)
        env.log.append(f"{card.name} deals {dealt} to {enemy.creature.name}")


@effect_handler("ashen_strike")
def _ashen_strike(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Ashen Strike needs a target")
    amount = int(effect["base"]) + int(effect["per_exhaust"]) * len(env.exhaust_pile)
    dealt = env.deal_damage(target, env.calculate_damage(env.player, target, amount))
    env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("bully")
def _bully(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Bully needs a target")
    amount = int(effect["base"]) + int(effect["per_vulnerable"]) * target.power_amount("vulnerable")
    dealt = env.deal_damage(target, env.calculate_damage(env.player, target, amount))
    env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("conditional_damage_all")
def _conditional_damage_all(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    minimum_exhaust = int(effect.get("minimum_exhaust", 0))
    if len(env.exhaust_pile) < minimum_exhaust:
        env.log.append(f"{card.name} condition not met")
        return
    amount = int(effect["amount"])
    for enemy in env.alive_enemies():
        dealt = env.deal_damage(enemy.creature, env.calculate_damage(env.player, enemy.creature, amount))
        env.log.append(f"{card.name} deals {dealt} to {enemy.creature.name}")


@effect_handler("hp_loss_then_block")
def _hp_loss_then_block(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    lost = env.lose_hp(env.player, int(effect["hp_loss"]), source=card)
    env.log.append(f"Player loses {lost} HP")
    env.gain_block(env.player, int(effect["block"]), source=card.name)


@effect_handler("if_exhausted_this_turn_gain_energy")
def _if_exhausted_this_turn_gain_energy(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if env.cards_exhausted_this_turn:
        amount = int(effect["amount"])
        env.gain_energy(amount, source=card.name)
    else:
        env.log.append(f"{card.name} has no exhausted card to fuel it")


@effect_handler("if_exhausted_this_turn_gain_block")
def _if_exhausted_this_turn_gain_block(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    times = 2 if env.cards_exhausted_this_turn else 1
    for _ in range(times):
        env.gain_block(env.player, int(effect["amount"]), source=card.name)


@effect_handler("damage_if_lost_hp")
def _damage_if_lost_hp(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError(f"{card.name} needs a target")
    hits = int(effect.get("hits_if_lost", 1)) if env.hp_lost_this_turn else 1
    for _ in range(hits):
        dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
        env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("tear_asunder")
def _tear_asunder(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Tear Asunder needs a target")
    hits = 1 + env.damage_events_received
    for _ in range(hits):
        dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
        env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("pillage")
def _pillage(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Pillage needs a target")
    dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
    env.log.append(f"{card.name} deals {dealt} to {target.name}")
    while True:
        if len(env.hand) >= env.max_hand_size:
            return
        before = len(env.hand)
        env.draw_cards(1)
        if len(env.hand) == before:
            return
        if env.card_def(env.hand[-1].def_id).card_type != "attack":
            return


@effect_handler("auto_play_from_draw")
def _auto_play_from_draw(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    count = int(effect.get("count", 1))
    if bool(effect.get("x_cost", False)):
        count = env.energy + int(effect.get("bonus", 0))
        env.energy = 0
    env.auto_play_from_draw(count, force_exhaust=bool(effect.get("force_exhaust", False)))


@effect_handler("add_random_attack_to_hand")
def _add_random_attack_to_hand(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    from sts2_sim.cards import ironclad_singleplayer_generation_pool

    generation_pool = set(ironclad_singleplayer_generation_pool())
    attacks = [
        card_id for card_id, card_def in env.card_library_items()
        if card_id in generation_pool
        and card_def.card_type == "attack"
        and "unplayable" not in card_def.keywords
    ]
    if not attacks:
        return
    card_id = env.rng.choice(attacks)
    env.add_to_hand(CardInstance(card_id, free_this_turn=True), source=card.name)
    env.log.append(f"{card.name} creates {env.card_name(card_id)}")


@effect_handler("heal")
def _heal(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    amount = int(effect["amount"])
    env.player.hp = min(env.player.max_hp, env.player.hp + amount)
    env.log.append(f"Player heals {amount} HP")


@effect_handler("transform_attacks_to_strikes")
def _transform_attacks_to_strikes(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    for card_instance in env.hand:
        if env.card_def(card_instance.def_id).card_type == "attack":
            card_instance.def_id = str(effect.get("card_id", "strike_ironclad_plus" if bool(effect.get("upgraded", False)) else "strike_ironclad"))
            card_instance.misc = 0
            card_instance.free_this_turn = False
    env.log.append(f"{card.name} transforms hand attacks")


@effect_handler("gain_energy_per_attack_in_hand")
def _gain_energy_per_attack_in_hand(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    amount = sum(1 for card_instance in env.hand if env.card_def(card_instance.def_id).card_type == "attack")
    env.gain_energy(amount, source=card.name)
    env.player.add_power("no_energy_gain", 1)


@effect_handler("stoke")
def _stoke(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    count = len(env.hand)
    for idx in reversed(range(len(env.hand))):
        env.exhaust_from_hand(idx, caused_by_ethereal=False)
    from sts2_sim.cards import ironclad_singleplayer_generation_pool

    pool = ironclad_singleplayer_generation_pool()
    for _ in range(count):
        card_id = env.rng.choice(pool)
        if bool(effect.get("upgraded", False)):
            upgraded_id = env.card_def(card_id).upgraded_id
            if upgraded_id is not None:
                card_id = upgraded_id
        env.add_to_hand(CardInstance(card_id), source=card.name)
    env.log.append(f"{card.name} replaces hand with {count} card(s)")


@effect_handler("thrash")
def _thrash(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Thrash needs a target")
    amount = int(effect["amount"]) + (env.current_card_instance.misc if env.current_card_instance else 0)
    for _ in range(2):
        dealt = env.deal_damage(target, env.calculate_damage(env.player, target, amount))
        env.log.append(f"{card.name} deals {dealt} to {target.name}")
    attacks = [idx for idx, inst in enumerate(env.hand) if env.card_def(inst.def_id).card_type == "attack"]
    if attacks and env.current_card_instance is not None:
        idx = env.rng.choice(attacks)
        bonus = env.estimate_card_damage_var(env.hand[idx])
        env.exhaust_from_hand(idx, caused_by_ethereal=False)
        env.current_card_instance.misc += bonus
        env.log.append(f"{card.name} gains {bonus} damage")


@effect_handler("molten_fist")
def _molten_fist(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Molten Fist needs a target")
    dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
    env.log.append(f"{card.name} deals {dealt} to {target.name}")
    if not target.alive:
        return
    vulnerable = target.power_amount("vulnerable")
    if vulnerable <= 0:
        return
    target.add_power("vulnerable", vulnerable)
    env.log.append(f"{target.name} gains vulnerable {vulnerable}")
    if env.player.power_amount("vicious"):
        env.draw_cards(env.player.power_amount("vicious"))


@effect_handler("dismantle")
def _dismantle(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Dismantle needs a target")
    hits = 2 if target.power_amount("vulnerable") > 0 else 1
    for _ in range(hits):
        dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
        env.log.append(f"{card.name} deals {dealt} to {target.name}")


@effect_handler("dominate")
def _dominate(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Dominate needs a target")
    amount = int(effect["vulnerable"])
    target.add_power("vulnerable", amount)
    env.log.append(f"{target.name} gains vulnerable {amount}")
    if env.player.power_amount("vicious"):
        env.draw_cards(env.player.power_amount("vicious"))
    strength = target.power_amount("vulnerable")
    env.player.add_power("strength", strength)
    env.log.append(f"Ironclad gains strength {strength}")


@effect_handler("fight_me")
def _fight_me(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Fight Me needs a target")
    for _ in range(int(effect["hits"])):
        dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
        env.log.append(f"{card.name} deals {dealt} to {target.name}")
    env.player.add_power("strength", int(effect["player_strength"]))
    target.add_power("strength", int(effect["enemy_strength"]))
    env.log.append(f"Ironclad gains strength {int(effect['player_strength'])}")
    env.log.append(f"{target.name} gains strength {int(effect['enemy_strength'])}")


@effect_handler("mangle")
def _mangle(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Mangle needs a target")
    dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
    env.log.append(f"{card.name} deals {dealt} to {target.name}")
    loss = int(effect["strength_loss"])
    target.add_power("strength", -loss)
    target.add_power("mangle_strength_down", loss)
    env.log.append(f"{target.name} loses {loss} Strength this turn")


@effect_handler("setup_strike")
def _setup_strike(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Setup Strike needs a target")
    dealt = env.deal_damage(target, env.calculate_damage(env.player, target, int(effect["amount"])))
    env.log.append(f"{card.name} deals {dealt} to {target.name}")
    strength = int(effect["strength"])
    env.player.add_power("strength", strength)
    env.player.add_power("setup_strike_strength", strength)
    env.log.append(f"Ironclad gains {strength} temporary Strength")


@effect_handler("feed")
def _feed(env: "CombatEnv", card: CardDef, effect: dict[str, Any], target: Creature | None) -> None:
    if target is None:
        raise ValueError("Feed needs a target")
    was_alive = target.alive
    damage = env.calculate_damage(env.player, target, int(effect["amount"]))
    dealt = env.deal_damage(target, damage)
    env.log.append(f"{card.name} deals {dealt} to {target.name}")
    if was_alive and not target.alive:
        gain = int(effect["max_hp"])
        env.player.max_hp += gain
        env.player.hp += gain
        env.log.append(f"Feed grants {gain} max HP")
