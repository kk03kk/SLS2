from __future__ import annotations

import random
from dataclasses import dataclass, field

from sts2_sim.cards import CARD_LIBRARY
from sts2_sim.data import CardDef, CardInstance, Creature, EnemyDef, EnemyMove, EnemyState
from sts2_sim.enemies import ENEMY_LIBRARY
from sts2_sim.effects import apply_effect
from sts2_sim.powers import POWER_REGISTRY, PowerContext


END_TURN = (-1, None)
MAX_HAND_SIZE = 10
Action = tuple[int, int | None] | tuple[int, int | None, int | None]


@dataclass
class CombatResult:
    won: bool
    turns: int
    hp_lost: int
    final_hp: int
    enemies_killed: int
    log: list[str] = field(default_factory=list)


class CombatEnv:
    max_hand_size = MAX_HAND_SIZE

    def __init__(
        self,
        deck: list[str],
        enemies: list[EnemyDef],
        *,
        player_hp: int = 80,
        player_max_hp: int | None = None,
        seed: int | None = None,
        draw_per_turn: int = 5,
        energy_per_turn: int = 3,
        max_turns: int = 100,
        enable_burning_blood: bool = False,
    ) -> None:
        self.deck_ids = list(deck)
        self.enemy_defs = list(enemies)
        self.starting_hp = player_hp
        self.player_max_hp = player_hp if player_max_hp is None else player_max_hp
        self.draw_per_turn = draw_per_turn
        self.energy_per_turn = energy_per_turn
        self.max_turns = max_turns
        self.enable_burning_blood = enable_burning_blood
        self.rng = random.Random(seed)
        self.log: list[str] = []
        self._power_contexts: dict[tuple[int, str], PowerContext] = {}
        self.current_card_instance: CardInstance | None = None
        self.current_card_def: CardDef | None = None
        self.current_choice_index: int | None = None
        self.last_played_card_instance: CardInstance | None = None
        self.pending_rupture_strength = 0
        self.reset()

    def reset(self) -> dict:
        self.player = Creature("Ironclad", self.player_max_hp, self.starting_hp)
        self.energy = self.energy_per_turn
        self.turn = 0
        self.hp_lost_this_turn = 0
        self.hp_lost_this_combat = 0
        self.damage_events_received = 0
        self.cards_exhausted_this_turn = 0
        self.block_gains_this_turn = 0
        self.attacks_played_this_turn = 0
        self.current_side = "player"
        self.draw_pile = [CardInstance(card_id) for card_id in self.deck_ids]
        self.discard_pile: list[CardInstance] = []
        self.hand: list[CardInstance] = []
        self.exhaust_pile: list[CardInstance] = []
        self.removed_pile: list[CardInstance] = []
        self.play_pile: list[CardInstance] = []
        self.rng.shuffle(self.draw_pile)
        self.enemies = [self._create_enemy(enemy_def) for enemy_def in self.enemy_defs]
        self.log = []
        self._power_contexts = {}
        self.current_card_instance = None
        self.current_card_def = None
        self.current_choice_index = None
        self.last_played_card_instance = None
        self.pending_rupture_strength = 0
        self._start_player_turn()
        return self.observation()

    def observation(self) -> dict:
        return {
            "turn": self.turn,
            "player": {
                "hp": self.player.hp,
                "max_hp": self.player.max_hp,
                "block": self.player.block,
                "energy": self.energy,
                "powers": dict(self.player.powers),
            },
            "hand": [CARD_LIBRARY[card.def_id].name for card in self.hand],
            "enemies": [
                {
                    "name": enemy.creature.name,
                    "hp": enemy.creature.hp,
                    "max_hp": enemy.creature.max_hp,
                    "block": enemy.creature.block,
                    "powers": dict(enemy.creature.powers),
                    "intent": self.current_enemy_move(enemy).intent if enemy.alive else "dead",
                }
                for enemy in self.enemies
            ],
            "draw": len(self.draw_pile),
            "discard": len(self.discard_pile),
            "exhaust": len(self.exhaust_pile),
        }

    def legal_actions(self) -> list[Action]:
        actions: list[Action] = [END_TURN]
        alive_targets = [idx for idx, enemy in enumerate(self.enemies) if enemy.alive]
        for hand_idx, card_id in enumerate(self.hand):
            card = CARD_LIBRARY[card_id.def_id]
            if not self.can_play(card, card_id):
                continue
            choice_indices = self._effect_choice_indices(hand_idx, card)
            if card.target == "enemy":
                for target_idx in alive_targets:
                    actions.extend(self._expand_action_choices(hand_idx, target_idx, choice_indices))
            elif card.target == "all_enemies":
                actions.extend(self._expand_action_choices(hand_idx, None, choice_indices))
            else:
                actions.extend(self._expand_action_choices(hand_idx, None, choice_indices))
        return actions

    def step(self, action: Action) -> tuple[dict, int, bool, dict]:
        if action == END_TURN:
            self.end_player_turn()
        else:
            self.play_card(*action)
        done = self.is_done()
        reward = self._reward(done)
        return self.observation(), reward, done, {"result": self.result() if done else None}

    def play_card(
        self,
        hand_index: int,
        target_index: int | None = None,
        choice_index: int | None = None,
    ) -> None:
        if hand_index < 0 or hand_index >= len(self.hand):
            raise ValueError(f"Invalid hand index: {hand_index}")
        card_instance = self.hand[hand_index]
        card = CARD_LIBRARY[card_instance.def_id]
        if not self.can_play(card, card_instance):
            raise ValueError(f"Cannot play card: {card.name}")
        if card.target == "enemy":
            if target_index is None or target_index >= len(self.enemies) or not self.enemies[target_index].alive:
                raise ValueError(f"Invalid target for {card.name}: {target_index}")
            target = self.enemies[target_index].creature
        elif card.target == "all_enemies":
            target = None
        else:
            target = self.player

        self.energy -= self.effective_cost(card, card_instance)
        if self.player.power_amount("free_attack") and card.card_type == "attack":
            self.player.add_power("free_attack", -1)
        self.hand.pop(hand_index)
        self.log.append(f"Player plays {card.name}" + (f" -> {target.name}" if card.target == "enemy" else ""))
        self.current_card_instance = card_instance
        self.current_card_def = card
        self.current_choice_index = choice_index
        self.pending_rupture_strength = 0
        play_count = 1
        if card.card_type == "attack" and self.player.power_amount("one_two_punch") > 0:
            play_count += 1
            self.player.add_power("one_two_punch", -1)
            self.log.append(f"One Two Punch repeats {card.name}")
        for _ in range(play_count):
            for effect in card.effects:
                apply_effect(self, card, effect, target)
        if self.pending_rupture_strength:
            self.player.add_power("strength", self.pending_rupture_strength)
            self.log.append(f"Rupture grants {self.pending_rupture_strength} Strength")
            self.pending_rupture_strength = 0
        self.last_played_card_instance = card_instance
        self.current_card_instance = None
        self.current_card_def = None
        self.current_choice_index = None
        self._trigger_after_card_played(card)
        self.last_played_card_instance = None
        if card.card_type == "attack":
            self.attacks_played_this_turn += 1
        card_instance.free_this_turn = False
        if "exhaust" in card.keywords or (self.player.power_amount("corruption") and card.card_type == "skill"):
            self.exhaust_card(card_instance, caused_by_ethereal=False)
        elif card.exhausts_when_played:
            self.removed_pile.append(card_instance)
            self.log.append(f"{card.name} leaves combat")
        else:
            self.discard_pile.append(card_instance)

    def can_play(self, card: CardDef, card_instance: CardInstance | None = None) -> bool:
        if "unplayable" in card.keywords:
            return False
        if (
            card.card_type == "skill"
            and self.player.power_amount("smoggy") > 0
            and self.power_context(self.player, "smoggy").data.get("skill_locked", 0)
        ):
            return False
        if card.cost < 0 and not self._is_x_cost_card(card):
            return False
        return self.energy >= self.effective_cost(card, card_instance)

    def effective_cost(self, card: CardDef, card_instance: CardInstance | None = None) -> int:
        if self._is_x_cost_card(card):
            return 0
        if card_instance is not None and card_instance.free_this_turn and card.cost > 0:
            return 0
        if card.id in {"stomp", "stomp_plus"}:
            return max(0, card.cost - self.attacks_played_this_turn)
        if self.player.power_amount("free_attack") and card.card_type == "attack" and card.cost > 0:
            return 0
        if self.player.power_amount("corruption") and card.card_type == "skill" and card.cost > 0:
            return 0
        return max(0, card.cost)

    def _is_x_cost_card(self, card: CardDef) -> bool:
        return card.cost < 0 and any(bool(effect.get("x_cost", False)) for effect in card.effects)

    def end_player_turn(self) -> None:
        self.log.append("Player ends turn")
        self._stampede_autoplay()
        self._howl_from_beyond_autoplay()
        remaining_hand = self.hand
        self.hand = []
        for card_instance in remaining_hand:
            card = CARD_LIBRARY[card_instance.def_id]
            card_instance.free_this_turn = False
            if card.id == "beckon":
                lost = self.lose_hp(self.player, 6, source=card)
                self.log.append(f"Beckon deals {lost} HP loss at end of turn")
            if "ethereal" in card.keywords:
                self.exhaust_card(card_instance, caused_by_ethereal=True)
            else:
                self.discard_pile.append(card_instance)
        for pile in (self.draw_pile, self.discard_pile, self.exhaust_pile):
            for card_instance in pile:
                card_instance.free_this_turn = False
        self._trigger_after_player_turn_end()
        self._enemy_turn()
        if not self.is_done():
            self._start_player_turn()

    def is_done(self) -> bool:
        return self.player.hp <= 0 or not self._combat_relevant_enemies_alive() or self.turn >= self.max_turns

    def result(self) -> CombatResult:
        won = self.player.hp > 0 and not self._combat_relevant_enemies_alive()
        final_hp = max(0, self.player.hp)
        if won and self.enable_burning_blood:
            final_hp = min(self.player.max_hp, final_hp + 6)
        return CombatResult(
            won=won,
            turns=self.turn,
            hp_lost=self.starting_hp - final_hp,
            final_hp=final_hp,
            enemies_killed=sum(1 for enemy in self.enemies if not enemy.alive),
            log=list(self.log),
        )

    def current_enemy_move(self, enemy: EnemyState) -> EnemyMove:
        return enemy.definition.moves[enemy.move_index]

    def alive_enemies(self) -> list[EnemyState]:
        return [enemy for enemy in self.enemies if enemy.alive]

    def _combat_relevant_enemies_alive(self) -> bool:
        return any(enemy.alive and enemy.creature.power_amount("minion") <= 0 for enemy in self.enemies)

    def card_name(self, card_id: str) -> str:
        return CARD_LIBRARY[card_id].name

    def card_def(self, card_id: str) -> CardDef:
        return CARD_LIBRARY[card_id]

    def card_library_items(self):
        return CARD_LIBRARY.items()

    def power_context(self, owner: Creature, power_id: str) -> PowerContext:
        key = (id(owner), power_id)
        if key not in self._power_contexts:
            self._power_contexts[key] = PowerContext()
        return self._power_contexts[key]

    def gain_block(
        self,
        creature: Creature,
        amount: int,
        *,
        source: str = "Block",
        counts_for_unmovable: bool = True,
    ) -> None:
        if (
            counts_for_unmovable
            and creature == self.player
            and self.player.power_amount("unmovable") > self.block_gains_this_turn
        ):
            amount *= 2
        creature.gain_block(amount)
        if creature == self.player and counts_for_unmovable:
            self.block_gains_this_turn += 1
        self.log.append(f"{creature.name} gains {max(0, amount)} block from {source}")
        self._trigger_after_block_gained(creature, max(0, amount))

    def enemy_gain_block(self, creature: Creature, amount: int, *, source: str = "Block") -> None:
        creature.gain_block(amount)
        self.log.append(f"{creature.name} gains {max(0, amount)} block from {source}")

    def gain_energy(self, amount: int, *, source: str = "Energy") -> None:
        if self.player.power_amount("no_energy_gain"):
            self.log.append("No Energy Gain prevents energy gain")
            return
        self.energy += amount
        self.log.append(f"{source} grants {amount} energy")

    def add_to_hand(self, card_instance: CardInstance, *, source: str = "Card") -> None:
        if len(self.hand) >= self.max_hand_size:
            card_instance.free_this_turn = False
            self.discard_pile.append(card_instance)
            self.log.append(f"{source} sends {CARD_LIBRARY[card_instance.def_id].name} to discard because hand is full")
            return
        self.hand.append(card_instance)

    def exhaust_card(self, card_instance: CardInstance, *, caused_by_ethereal: bool) -> None:
        card = CARD_LIBRARY[card_instance.def_id]
        self.exhaust_pile.append(card_instance)
        self.cards_exhausted_this_turn += 1
        suffix = " at end of turn" if caused_by_ethereal else ""
        self.log.append(f"{card.name} exhausts{suffix}")
        self._trigger_after_card_exhausted(card, caused_by_ethereal)
        if card.id in {"drum_of_battle", "drum_of_battle_plus"}:
            amount = 3 if card.id == "drum_of_battle_plus" else 2
            self.gain_energy(amount, source=card.name)

    def exhaust_from_hand(self, hand_index: int, *, caused_by_ethereal: bool) -> None:
        card_instance = self.hand.pop(hand_index)
        self.exhaust_card(card_instance, caused_by_ethereal=caused_by_ethereal)

    def hand_indices(self, *, exclude_card_id: str | None = None) -> list[int]:
        return [
            idx for idx, card_id in enumerate(self.hand)
            if exclude_card_id is None or card_id.def_id != exclude_card_id
        ]

    def choose_hand_card(self, candidates: list[int], *, purpose: str) -> int:
        if self.current_choice_index is not None and self.current_choice_index in candidates:
            return self.current_choice_index
        if purpose == "upgrade":
            return max(candidates, key=lambda idx: self._card_upgrade_score(self.hand[idx].def_id))
        if purpose == "exhaust":
            return min(candidates, key=lambda idx: self._card_keep_score(self.hand[idx].def_id))
        return candidates[0]

    def choose_pile_card(self, pile: list[CardInstance], *, purpose: str) -> int:
        if purpose == "draw_top":
            if self.current_choice_index is not None:
                if self.current_choice_index < 0 or self.current_choice_index >= len(pile):
                    raise ValueError(f"Invalid pile choice index: {self.current_choice_index}")
                return self.current_choice_index
            return max(range(len(pile)), key=lambda idx: self._card_keep_score(pile[idx].def_id))
        return len(pile) - 1

    def _effect_choice_indices(self, hand_idx: int, card: CardDef) -> list[int | None]:
        needs_discard_choice = any(effect.get("type") == "move_discard_to_draw_top" for effect in card.effects)
        if needs_discard_choice and self.discard_pile:
            return list(range(len(self.discard_pile)))
        needs_exhaust_choice = any(
            effect.get("type") == "exhaust_from_hand" and effect.get("mode", "chosen") != "random"
            for effect in card.effects
        )
        if needs_exhaust_choice and len(self.hand) > 1:
            return list(range(len(self.hand) - 1))
        needs_upgrade_choice = any(
            effect.get("type") == "upgrade_from_hand" and not bool(effect.get("all", False))
            for effect in card.effects
        )
        if needs_upgrade_choice:
            post_play_hand = [
                card_instance
                for idx, card_instance in enumerate(self.hand)
                if idx != hand_idx
            ]
            candidates = [
                idx for idx, card_instance in enumerate(post_play_hand)
                if self.is_upgradable(card_instance.def_id)
            ]
            if candidates:
                return candidates
        return [None]

    def _expand_action_choices(
        self,
        hand_idx: int,
        target_idx: int | None,
        choice_indices: list[int | None],
    ) -> list[Action]:
        if choice_indices == [None]:
            return [(hand_idx, target_idx)]
        return [(hand_idx, target_idx, choice_idx) for choice_idx in choice_indices]

    def is_upgradable(self, card_id: str) -> bool:
        return CARD_LIBRARY[card_id].upgraded_id is not None

    def upgrade_hand_card(self, hand_index: int) -> None:
        card_instance = self.hand[hand_index]
        self.upgrade_card_instance(card_instance)

    def upgrade_card_instance(self, card_instance: CardInstance) -> None:
        card_id = card_instance.def_id
        upgraded_id = CARD_LIBRARY[card_id].upgraded_id
        if upgraded_id is None:
            return
        card_instance.def_id = upgraded_id
        self.log.append(f"{CARD_LIBRARY[card_id].name} upgrades to {CARD_LIBRARY[upgraded_id].name}")

    def _card_keep_score(self, card_id: str) -> int:
        card = CARD_LIBRARY[card_id]
        score = 0
        if card.card_type == "curse":
            score -= 100
        if card.card_type == "status":
            score -= 40
        if "unplayable" in card.keywords:
            score -= 40
        if card.card_type == "attack":
            score += 20
        if card.card_type == "power":
            score += 15
        score -= max(card.cost, 0)
        return score

    def _card_upgrade_score(self, card_id: str) -> int:
        card = CARD_LIBRARY[card_id]
        if card.upgraded_id is None:
            return -999
        if card.card_type == "attack":
            return 30
        if card.card_type == "skill":
            return 20
        return 10

    def _create_enemy(self, enemy_def: EnemyDef) -> EnemyState:
        hp = self.rng.randint(enemy_def.min_hp, enemy_def.max_hp)
        enemy = EnemyState(enemy_def, Creature(enemy_def.name, hp, hp))
        for power, amount in enemy_def.initial_powers:
            enemy.creature.add_power(power, amount)
        if enemy_def.ai == "rat_backup":
            enemy.vars["turns_until_summonable"] = 2
            enemy.vars["call_for_backup_count"] = 0
        if enemy_def.ai == "waterfall_giant":
            enemy.vars["pressure_gun_damage"] = 20
        return enemy

    def _start_player_turn(self) -> None:
        self.current_side = "player"
        self.turn += 1
        self.hp_lost_this_turn = 0
        self.cards_exhausted_this_turn = 0
        self.block_gains_this_turn = 0
        self.attacks_played_this_turn = 0
        if self._should_clear_block(self.player):
            self.player.block = 0
        self.energy = self.energy_per_turn + self.player.power_amount("pyre")
        self.log.append(f"-- Turn {self.turn} --")
        for enemy in self.enemies:
            if enemy.creature.power_amount("hardened_shell"):
                self.power_context(enemy.creature, "hardened_shell").data["damage_received_this_turn"] = 0
            if enemy.creature.power_amount("skittish"):
                self.power_context(enemy.creature, "skittish").data["blocked_this_turn"] = 0
        if self.turn == 1:
            for enemy in self.enemies:
                plating = enemy.creature.power_amount("plating")
                if enemy.alive and plating:
                    self.enemy_gain_block(enemy.creature, plating, source="Plating")
        self._trigger_after_player_turn_start()
        innate_drawn = self._draw_innate_cards() if self.turn == 1 else 0
        self.draw_cards(max(0, self.draw_per_turn - innate_drawn))

    def _draw_innate_cards(self) -> int:
        innate_indices = [
            idx for idx, card_instance in enumerate(self.draw_pile)
            if "innate" in CARD_LIBRARY[card_instance.def_id].keywords
        ]
        drawn = 0
        for idx in sorted(innate_indices, reverse=True):
            if len(self.hand) >= self.max_hand_size:
                break
            card_instance = self.draw_pile.pop(idx)
            self.hand.append(card_instance)
            drawn += 1
            self.log.append(f"Draw {CARD_LIBRARY[card_instance.def_id].name}")
            self._hellraiser_after_draw(len(self.hand) - 1)
        return drawn

    def _enemy_turn(self) -> None:
        self.current_side = "enemy"
        for enemy in self.enemies:
            if not enemy.alive or self.player.hp <= 0:
                continue
            if enemy.creature.power_amount("plating") > 0 and self.turn > 1:
                enemy.creature.add_power("plating", -1)
            if self._should_clear_block(enemy.creature):
                enemy.creature.block = 0
            if enemy.vars.get("ravenous_stun", 0) > 0:
                enemy.vars["ravenous_stun"] -= 1
                self.log.append(f"{enemy.creature.name} is stunned by Ravenous")
                continue
            if enemy.vars.get("wake_stun", 0) > 0:
                enemy.vars["wake_stun"] -= 1
                self.log.append(f"{enemy.creature.name} wakes up stunned")
                enemy.move_index = 1
                continue
            move = self.current_enemy_move(enemy)
            self.log.append(f"{enemy.creature.name} uses {move.id}")
            self._perform_enemy_move(enemy, move)
            enemy.last_move_id = move.id
            self._advance_enemy_move(enemy)
        self._after_enemy_side_turn_end()
        self.current_side = "player"

    def _perform_enemy_move(self, enemy: EnemyState, move: EnemyMove) -> None:
        if move.block:
            self.enemy_gain_block(enemy.creature, move.block, source=move.id)
        if move.apply_power and not move.apply_power_after_damage:
            enemy.creature.add_power(move.apply_power, move.apply_power_amount)
            if move.apply_power == "ritual":
                enemy.ritual_just_applied = True
            self.log.append(f"{enemy.creature.name} gains {move.apply_power} {move.apply_power_amount}")
        if move.apply_player_power:
            self.player.add_power(move.apply_player_power, move.apply_player_power_amount)
            self.log.append(f"Ironclad gains {move.apply_player_power} {move.apply_player_power_amount}")
        for power, amount in move.extra_player_powers:
            self.player.add_power(power, amount)
            self.log.append(f"Ironclad gains {power} {amount}")
        if move.heal:
            before = enemy.creature.hp
            enemy.creature.hp = min(enemy.creature.max_hp, enemy.creature.hp + move.heal)
            self.log.append(f"{enemy.creature.name} heals {enemy.creature.hp - before}")
        if move.id == "about_to_blow":
            enemy.vars["about_to_blow"] = 2
            self.log.append(f"{enemy.creature.name} is stunned before eruption")
        if move.id == "explode":
            move_damage = enemy.vars.get("steam_eruption_damage", move.damage)
        elif move.id == "pressure_gun":
            move_damage = enemy.vars.get("pressure_gun_damage", move.damage)
            enemy.vars["pressure_gun_damage"] = move_damage + 5
        else:
            move_damage = move.damage
        if move.add_card_id:
            for _ in range(move.add_card_count):
                self.discard_pile.append(CardInstance(move.add_card_id))
            self.log.append(f"{enemy.creature.name} adds {move.add_card_count} {CARD_LIBRARY[move.add_card_id].name} to discard")
        for summon_id in move.summon:
            if summon_id in ENEMY_LIBRARY:
                summoned = self._create_enemy(ENEMY_LIBRARY[summon_id])
                self.enemies.append(summoned)
                self.log.append(f"{enemy.creature.name} summons {summoned.creature.name}")
        if move.id == "beckon":
            self._add_card_to_draw_random(CardInstance("beckon"))
            self.discard_pile.append(CardInstance("beckon"))
            self.log.append(f"{enemy.creature.name} adds 2 Beckon")
        elif move.id == "gaze":
            self.discard_pile.append(CardInstance("beckon"))
            self.log.append(f"{enemy.creature.name} adds 1 Beckon")
        if move.id == "call_for_backup":
            next_count = max(
                (rat.vars.get("call_for_backup_count", 0) for rat in self.enemies if rat.definition.ai == "rat_backup"),
                default=0,
            ) + 1
            for rat in self.enemies:
                if rat.definition.ai == "rat_backup":
                    rat.vars["call_for_backup_count"] = next_count
        for _ in range(move.hits):
            if move_damage:
                base_damage = move_damage
                vigor = enemy.creature.power_amount("vigor")
                if vigor:
                    base_damage += vigor
                    enemy.creature.powers.pop("vigor", None)
                    self.log.append(f"{enemy.creature.name}'s Vigor adds {vigor} damage")
                damage = self.calculate_damage(enemy.creature, self.player, base_damage)
                dealt = self.deal_damage_from(self.player, damage, dealer=enemy.creature)
                self.log.append(f"{enemy.creature.name} hits player for {dealt}")
                suck = enemy.creature.power_amount("suck")
                if dealt > 0 and suck:
                    enemy.creature.add_power("strength", suck)
                    self.log.append(f"{enemy.creature.name}'s Suck grants {suck} Strength")
        if move.apply_power and move.apply_power_after_damage:
            enemy.creature.add_power(move.apply_power, move.apply_power_amount)
            if move.apply_power == "ritual":
                enemy.ritual_just_applied = True
            self.log.append(f"{enemy.creature.name} gains {move.apply_power} {move.apply_power_amount}")
        if move.self_kill and enemy.alive:
            enemy.creature.hp = 0
            self.log.append(f"{enemy.creature.name} dies after {move.id}")
            self._process_death_if_needed(enemy.creature)
        if move.escape and enemy.alive:
            enemy.creature.hp = 0
            self.log.append(f"{enemy.creature.name} escapes")
            enemy.death_processed = True

    def _advance_enemy_move(self, enemy: EnemyState) -> None:
        ai = enemy.definition.ai
        if ai == "repeat":
            enemy.move_index = 0
        elif ai == "cultist":
            enemy.move_index = 1
        elif ai == "random_no_repeat":
            choices = list(range(len(enemy.definition.moves)))
            if len(choices) > 1:
                choices.remove(enemy.move_index)
            enemy.move_index = self.rng.choice(choices)
        elif ai == "weighted_random":
            if enemy.last_move_id == "sticky":
                enemy.move_index = 0
            else:
                enemy.move_index = 0 if self.rng.random() < 2 / 3 else 1
        elif ai == "cycle":
            enemy.move_index = (enemy.move_index + 1) % len(enemy.definition.moves)
        elif ai == "random_any":
            enemy.move_index = self.rng.randrange(len(enemy.definition.moves))
        elif ai == "haunted_ship":
            enemy.move_index = 1 if enemy.move_index in {0, 2} else 2
        elif ai == "living_fog":
            enemy.move_index = 1 if enemy.move_index in {0, 2} else 2
        elif ai == "rat_backup":
            self._advance_two_tailed_rat(enemy)
        elif ai == "gardener":
            enemy.move_index = (enemy.move_index + 1) % len(enemy.definition.moves)
        elif ai == "skulking_colony":
            enemy.move_index = (enemy.move_index + 1) % len(enemy.definition.moves)
        elif ai == "lagavulin_matriarch":
            if enemy.creature.power_amount("asleep") > 0:
                enemy.move_index = 0
            elif enemy.move_index == 0:
                enemy.move_index = 1
            elif enemy.move_index == 1:
                enemy.move_index = 2
            elif enemy.move_index == 2:
                enemy.move_index = 3
            elif enemy.move_index == 3:
                enemy.move_index = 4
            else:
                enemy.move_index = 1
        elif ai == "soul_fysh":
            enemy.move_index = (enemy.move_index + 1) % len(enemy.definition.moves)
        elif ai == "waterfall_giant":
            if enemy.vars.get("about_to_blow", 0):
                enemy.move_index = 7
            elif enemy.move_index == 0:
                enemy.move_index = 1
            elif enemy.move_index in {1, 2, 3, 4}:
                enemy.move_index += 1
            else:
                enemy.move_index = 1
        elif ai == "terror_eel":
            if enemy.move_index == 0:
                enemy.move_index = 1
            elif enemy.move_index == 1:
                enemy.move_index = 0
            elif enemy.move_index == 2:
                enemy.move_index = 3
            else:
                enemy.move_index = 0
        elif ai == "sequence":
            enemy.move_index = min(enemy.move_index + 1, len(enemy.definition.moves) - 1)
        else:
            enemy.move_index = 0

    def _advance_two_tailed_rat(self, enemy: EnemyState) -> None:
        if enemy.last_move_id != "call_for_backup":
            enemy.vars["turns_until_summonable"] = enemy.vars.get("turns_until_summonable", 2) - 1
        can_summon = (
            enemy.vars.get("turns_until_summonable", 2) <= 0
            and enemy.vars.get("call_for_backup_count", 0) < 3
            and sum(1 for other in self.enemies if other.alive and other.definition.ai == "rat_backup") < 6
            and not any(
                other.alive
                and other is not enemy
                and other.definition.ai == "rat_backup"
                and self.current_enemy_move(other).id == "call_for_backup"
                for other in self.enemies
            )
        )
        choices = [0, 1, 2]
        if enemy.move_index in choices and len(choices) > 1:
            choices.remove(enemy.move_index)
        if can_summon and self.rng.random() < 0.75:
            enemy.move_index = 3
        else:
            enemy.move_index = self.rng.choice(choices)

    def _after_enemy_side_turn_end(self) -> None:
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            ritual = enemy.creature.power_amount("ritual")
            if ritual:
                if enemy.ritual_just_applied:
                    enemy.ritual_just_applied = False
                else:
                    enemy.creature.add_power("strength", ritual)
                    self.log.append(f"{enemy.creature.name}'s Ritual grants {ritual} Strength")
            if enemy.creature.power_amount("asleep") > 0:
                if enemy.creature.power_amount("asleep") <= 1:
                    enemy.creature.powers.pop("plating", None)
                enemy.creature.add_power("asleep", -1)
                if enemy.creature.power_amount("asleep") <= 0 and enemy.definition.ai == "lagavulin_matriarch":
                    enemy.move_index = 1
                    self.log.append(f"{enemy.creature.name} wakes up naturally")
        self._tick_power(self.player, "vulnerable")
        self._tick_power(self.player, "weak")
        self._tick_power(self.player, "frail")
        for enemy in self.enemies:
            self._tick_power(enemy.creature, "vulnerable")
            self._tick_power(enemy.creature, "weak")
            self._tick_power(enemy.creature, "frail")
        self._trigger_after_enemy_turn_end()

    def _tick_power(self, creature: Creature, power: str) -> None:
        if creature.power_amount(power) > 0:
            creature.add_power(power, -1)

    def _iter_creatures(self) -> list[Creature]:
        return [self.player] + [enemy.creature for enemy in self.enemies]

    def _trigger_after_card_played(self, card: CardDef) -> None:
        for creature in self._iter_creatures():
            for power_id, amount in list(creature.powers.items()):
                handler = POWER_REGISTRY.after_card_played.get(power_id)
                if handler:
                    handler(self, creature, amount, card)

    def _trigger_after_card_exhausted(self, card: CardDef, caused_by_ethereal: bool) -> None:
        for creature in self._iter_creatures():
            for power_id, amount in list(creature.powers.items()):
                handler = POWER_REGISTRY.after_card_exhausted.get(power_id)
                if handler:
                    handler(self, creature, amount, card, caused_by_ethereal)

    def _trigger_after_block_gained(self, creature: Creature, block_amount: int) -> None:
        for power_id, amount in list(creature.powers.items()):
            handler = POWER_REGISTRY.after_block_gained.get(power_id)
            if handler:
                handler(self, creature, amount, block_amount)

    def _modify_hp_loss(self, creature: Creature, hp_loss: int, dealer: Creature | None) -> int:
        modified = hp_loss
        for power_id, amount in list(creature.powers.items()):
            handler = POWER_REGISTRY.modify_hp_loss.get(power_id)
            if handler:
                modified = handler(self, creature, amount, modified, dealer)
        return max(0, modified)

    def _trigger_after_damage_received(self, creature: Creature, hp_loss: int, dealer: Creature | None) -> None:
        for power_id, amount in list(creature.powers.items()):
            handler = POWER_REGISTRY.after_damage_received.get(power_id)
            if handler:
                handler(self, creature, amount, hp_loss, dealer)

    def _trigger_after_hp_lost(self, creature: Creature, hp_loss: int, source: CardDef | None) -> None:
        for power_id, amount in list(creature.powers.items()):
            handler = POWER_REGISTRY.after_hp_lost.get(power_id)
            if handler:
                handler(self, creature, amount, hp_loss, source)

    def _trigger_after_player_turn_start(self) -> None:
        for power_id, amount in list(self.player.powers.items()):
            handler = POWER_REGISTRY.after_player_turn_start.get(power_id)
            if handler:
                handler(self, self.player, amount)

    def _trigger_after_player_turn_end(self) -> None:
        for power_id, amount in list(self.player.powers.items()):
            handler = POWER_REGISTRY.after_player_turn_end.get(power_id)
            if handler:
                handler(self, self.player, amount)

    def _trigger_after_enemy_turn_end(self) -> None:
        for creature in self._iter_creatures():
            for power_id, amount in list(creature.powers.items()):
                handler = POWER_REGISTRY.after_enemy_turn_end.get(power_id)
                if handler:
                    handler(self, creature, amount)

    def _should_clear_block(self, creature: Creature) -> bool:
        for power_id in list(creature.powers):
            handler = POWER_REGISTRY.should_clear_block.get(power_id)
            if handler and not handler(creature):
                return False
        return True

    def calculate_damage(self, attacker: Creature, target: Creature, base_damage: int) -> int:
        amount = base_damage + attacker.power_amount("strength")
        if attacker.power_amount("weak") > 0:
            amount = int(amount * 0.75)
        if target.power_amount("vulnerable") > 0:
            vulnerable_multiplier = 1.5
            if attacker == self.player and self.player.power_amount("cruelty") > 0:
                vulnerable_multiplier += self.player.power_amount("cruelty") / 100
            amount = int(amount * vulnerable_multiplier)
        if target == self.player and target.power_amount("colossus") > 0 and attacker.power_amount("vulnerable") > 0:
            amount = int(amount * 0.5)
        if target == self.player and target.power_amount("tank") > 0:
            amount *= 2
        return max(0, amount)

    def deal_damage(self, target: Creature, amount: int) -> int:
        dealer = self.player if self.current_side == "player" else None
        return self.deal_damage_from(target, amount, dealer=dealer)

    def deal_damage_from(self, target: Creature, amount: int, dealer: Creature | None = None) -> int:
        was_alive = target.alive
        blocked = min(target.block, amount)
        target.block -= blocked
        hp_damage = amount - blocked
        hp_damage = self._modify_hp_loss(target, hp_damage, dealer)
        target.hp = max(0, target.hp - hp_damage)
        if target == self.player and hp_damage > 0:
            self.hp_lost_this_turn += hp_damage
            self.hp_lost_this_combat += hp_damage
            self.damage_events_received += 1
        self._trigger_after_damage_received(target, hp_damage, dealer)
        if was_alive and not target.alive:
            self._process_death_if_needed(target)
        return hp_damage

    def lose_hp(self, target: Creature, amount: int, *, source: CardDef | None = None) -> int:
        was_alive = target.alive
        hp_loss = min(target.hp, max(0, amount))
        hp_loss = self._modify_hp_loss(target, hp_loss, dealer=None)
        target.hp -= hp_loss
        if target == self.player and hp_loss > 0:
            self.hp_lost_this_turn += hp_loss
            self.hp_lost_this_combat += hp_loss
            self.damage_events_received += 1
        self._trigger_after_damage_received(target, hp_loss, dealer=None)
        self._trigger_after_hp_lost(target, hp_loss, source)
        if was_alive and not target.alive:
            self._process_death_if_needed(target)
        return hp_loss

    def _process_death_if_needed(self, creature: Creature) -> None:
        enemy = next((candidate for candidate in self.enemies if candidate.creature == creature), None)
        if enemy is None or enemy.death_processed:
            return
        steam = creature.power_amount("steam_eruption")
        if enemy.definition.ai == "waterfall_giant" and steam > 0 and not enemy.vars.get("about_to_blow", 0):
            enemy.vars["about_to_blow"] = 1
            enemy.vars["steam_eruption_damage"] = steam
            creature.powers.pop("steam_eruption", None)
            creature.max_hp = 999999999
            creature.hp = creature.max_hp
            enemy.move_index = 6
            self.log.append(f"{creature.name} is about to blow for {steam}")
            return
        enemy.death_processed = True
        if creature.power_amount("surprise") > 0 or enemy.definition.id == "gremlin_merc":
            for summon_id in ("sneaky_gremlin", "fat_gremlin"):
                summoned = self._create_enemy(ENEMY_LIBRARY[summon_id])
                self.enemies.append(summoned)
                self.log.append(f"{creature.name}'s Surprise summons {summoned.creature.name}")
        for other in self.enemies:
            if other is enemy or not other.alive:
                continue
            ravenous = other.creature.power_amount("ravenous")
            if ravenous <= 0:
                continue
            other.creature.add_power("strength", ravenous)
            other.vars["ravenous_stun"] = 1
            self.log.append(f"{other.creature.name}'s Ravenous grants {ravenous} Strength")

    def _add_card_to_draw_random(self, card_instance: CardInstance) -> None:
        idx = self.rng.randrange(len(self.draw_pile) + 1)
        self.draw_pile.insert(idx, card_instance)

    def draw_cards(self, count: int, *, ignore_no_draw: bool = False) -> None:
        if self.player.power_amount("no_draw") and not ignore_no_draw:
            self.log.append("No Draw prevents drawing cards")
            return
        for _ in range(count):
            if len(self.hand) >= MAX_HAND_SIZE:
                self.log.append("Hand is full")
                return
            if not self.draw_pile:
                if not self.discard_pile:
                    return
                self.draw_pile = self.discard_pile
                self.discard_pile = []
                self.rng.shuffle(self.draw_pile)
                self.log.append("Discard pile shuffled into draw pile")
            card_id = self.draw_pile.pop()
            self.hand.append(card_id)
            self.log.append(f"Draw {CARD_LIBRARY[card_id.def_id].name}")
            self._hellraiser_after_draw(len(self.hand) - 1)

    def all_combat_cards(self, *, include_current: bool = False) -> list[CardInstance]:
        cards = self.draw_pile + self.hand + self.discard_pile + self.exhaust_pile + self.removed_pile + self.play_pile
        if include_current and self.current_card_instance is not None:
            cards.append(self.current_card_instance)
        return cards

    def auto_play_from_draw(self, count: int, *, force_exhaust: bool = False) -> None:
        selected: list[CardInstance] = []
        for _ in range(max(0, count)):
            if not self.draw_pile:
                if not self.discard_pile:
                    break
                self.draw_pile = self.discard_pile
                self.discard_pile = []
                self.rng.shuffle(self.draw_pile)
                self.log.append("Discard pile shuffled into draw pile")
            selected.append(self.draw_pile.pop())
        self.play_pile.extend(selected)
        for card_instance in selected:
            self.auto_play_card_instance(card_instance, force_exhaust=force_exhaust)

    def auto_play_top_draw(self, *, force_exhaust: bool = False) -> None:
        self.auto_play_from_draw(1, force_exhaust=force_exhaust)

    def auto_play_card_instance(self, card_instance: CardInstance, *, force_exhaust: bool = False) -> None:
        card = CARD_LIBRARY[card_instance.def_id]
        if card_instance in self.play_pile:
            self.play_pile.remove(card_instance)
        if "unplayable" in card.keywords:
            self.move_auto_play_result_without_playing(card_instance, force_exhaust=force_exhaust)
            self.log.append(f"Auto-play skips {card.name}")
            return
        target_index = None
        if card.target == "enemy":
            alive = [idx for idx, enemy in enumerate(self.enemies) if enemy.alive]
            if not alive:
                self.move_auto_play_result_without_playing(card_instance, force_exhaust=force_exhaust)
                return
            target_index = self.rng.choice(alive)
        self.hand.append(card_instance)
        hand_index = len(self.hand) - 1
        old_energy = self.energy
        self.energy = max(self.energy, self.effective_cost(card, card_instance))
        self.play_card(hand_index, target_index)
        self.energy = old_energy
        if force_exhaust and card_instance in self.discard_pile:
            self.discard_pile.remove(card_instance)
            self.exhaust_card(card_instance, caused_by_ethereal=False)

    def move_auto_play_result_without_playing(self, card_instance: CardInstance, *, force_exhaust: bool) -> None:
        card = CARD_LIBRARY[card_instance.def_id]
        if force_exhaust or "exhaust" in card.keywords:
            self.exhaust_card(card_instance, caused_by_ethereal=False)
        elif card.exhausts_when_played:
            self.removed_pile.append(card_instance)
            self.log.append(f"{card.name} leaves combat")
        else:
            self.discard_pile.append(card_instance)

    def _hellraiser_after_draw(self, hand_index: int) -> None:
        if not self.player.power_amount("hellraiser") or hand_index >= len(self.hand):
            return
        card_instance = self.hand[hand_index]
        card = CARD_LIBRARY[card_instance.def_id]
        if "strike" not in card.keywords:
            return
        target_index = None
        if card.target == "enemy":
            alive = [idx for idx, enemy in enumerate(self.enemies) if enemy.alive]
            if not alive:
                return
            target_index = self.rng.choice(alive)
        old_energy = self.energy
        self.energy = max(self.energy, self.effective_cost(card, card_instance))
        self.play_card(hand_index, target_index)
        self.energy = old_energy

    def _stampede_autoplay(self) -> None:
        for _ in range(self.player.power_amount("stampede")):
            attacks = [
                idx for idx, card_instance in enumerate(self.hand)
                if CARD_LIBRARY[card_instance.def_id].card_type == "attack"
                and "unplayable" not in CARD_LIBRARY[card_instance.def_id].keywords
            ]
            if not attacks:
                return
            hand_index = self.rng.choice(attacks)
            card = CARD_LIBRARY[self.hand[hand_index].def_id]
            target_index = None
            if card.target == "enemy":
                alive = [idx for idx, enemy in enumerate(self.enemies) if enemy.alive]
                if not alive:
                    return
                target_index = self.rng.choice(alive)
            old_energy = self.energy
            self.energy = max(self.energy, self.effective_cost(card, self.hand[hand_index]))
            self.play_card(hand_index, target_index)
            self.energy = old_energy

    def _howl_from_beyond_autoplay(self) -> None:
        howls = [
            card_instance for card_instance in list(self.exhaust_pile)
            if card_instance.def_id in {"howl_from_beyond", "howl_from_beyond_plus"}
        ]
        for card_instance in howls:
            if card_instance not in self.exhaust_pile or not self.alive_enemies():
                continue
            self.exhaust_pile.remove(card_instance)
            self.hand.append(card_instance)
            hand_index = len(self.hand) - 1
            card = CARD_LIBRARY[card_instance.def_id]
            old_energy = self.energy
            self.energy = max(self.energy, self.effective_cost(card, card_instance))
            self.play_card(hand_index, None)
            self.energy = old_energy

    def estimate_card_damage_var(self, card_instance: CardInstance | str) -> int:
        if isinstance(card_instance, CardInstance):
            card = CARD_LIBRARY[card_instance.def_id]
            misc = card_instance.misc
        else:
            card = CARD_LIBRARY[card_instance]
            misc = 0

        raw: int | None = None
        for effect in card.effects:
            effect_type = effect.get("type")
            if effect_type in {
                "deal_damage",
                "deal_damage_all",
                "random_enemy_damage",
                "whirlwind",
                "fiend_fire",
                "tear_asunder",
                "damage_if_lost_hp",
                "molten_fist",
                "dismantle",
                "fight_me",
                "mangle",
                "setup_strike",
                "feed",
            }:
                raw = int(effect.get("amount", 0))
                break
            if effect_type == "body_slam":
                raw = self.player.block
                break
            if effect_type == "perfected_strike":
                strike_count = sum(
                    1 for instance in self.all_combat_cards(include_current=True)
                    if "strike" in CARD_LIBRARY[instance.def_id].keywords
                )
                raw = int(effect.get("base", 0)) + int(effect.get("per_strike", 0)) * strike_count
                break
            if effect_type == "ashen_strike":
                raw = int(effect.get("base", 0)) + int(effect.get("per_exhaust", 0)) * len(self.exhaust_pile)
                break
            if effect_type == "bully":
                raw = int(effect.get("base", 0))
                break
            if effect_type in {"rampage", "thrash"}:
                raw = int(effect.get("amount", 0)) + misc
                break

        if raw is None:
            return 0
        amount = raw + self.player.power_amount("strength")
        if self.player.power_amount("weak") > 0:
            amount = int(amount * 0.75)
        return max(0, amount)

    def estimate_card_damage(self, card_instance: CardInstance | str, target: Creature | None = None) -> int:
        if isinstance(card_instance, CardInstance):
            card = CARD_LIBRARY[card_instance.def_id]
            misc = card_instance.misc
        else:
            card = CARD_LIBRARY[card_instance]
            misc = 0

        def preview_damage(base_damage: int) -> int:
            if target is not None:
                return self.calculate_damage(self.player, target, base_damage)
            amount = base_damage + self.player.power_amount("strength")
            if self.player.power_amount("weak") > 0:
                amount = int(amount * 0.75)
            return max(0, amount)

        total = 0
        for effect in card.effects:
            effect_type = effect.get("type")
            if effect_type == "deal_damage":
                amount = preview_damage(int(effect.get("amount", 0)))
                total += amount * int(effect.get("hits", 1))
            elif effect_type == "deal_damage_all":
                amount = preview_damage(int(effect.get("amount", 0)))
                total += amount
            elif effect_type == "body_slam":
                amount = preview_damage(self.player.block)
                total += amount
            elif effect_type == "perfected_strike":
                strike_count = sum(
                    1 for instance in self.all_combat_cards(include_current=True)
                    if "strike" in CARD_LIBRARY[instance.def_id].keywords
                )
                amount = preview_damage(int(effect.get("base", 0)) + int(effect.get("per_strike", 0)) * strike_count)
                total += amount
            elif effect_type == "rampage":
                amount = preview_damage(int(effect.get("amount", 0)) + misc)
                total += amount
            elif effect_type == "ashen_strike":
                amount = preview_damage(int(effect.get("base", 0)) + int(effect.get("per_exhaust", 0)) * len(self.exhaust_pile))
                total += amount
            elif effect_type == "bully":
                vulnerable = target.power_amount("vulnerable") if target is not None else 0
                amount = int(effect.get("base", 0)) + int(effect.get("per_vulnerable", 0)) * vulnerable
                amount = preview_damage(amount)
                total += amount
            elif effect_type == "random_enemy_damage":
                amount = preview_damage(int(effect.get("amount", 0)))
                total += amount * int(effect.get("hits", 1))
            elif effect_type in {"whirlwind", "fiend_fire", "molten_fist", "dismantle", "fight_me", "mangle"}:
                amount = preview_damage(int(effect.get("amount", 0)))
                total += amount * int(effect.get("hits", 1))
            elif effect_type == "damage_if_lost_hp":
                hits = int(effect.get("hits_if_lost", 1)) if self.hp_lost_this_turn else 1
                amount = preview_damage(int(effect.get("amount", 0)))
                total += amount * hits
            elif effect_type == "tear_asunder":
                hits = 1 + self.damage_events_received
                amount = preview_damage(int(effect.get("amount", 0)))
                total += amount * hits
        return max(0, total)

    def _reward(self, done: bool) -> int:
        if not done:
            return 0
        if self.player.hp <= 0:
            return -100
        if all(not enemy.alive for enemy in self.enemies):
            return 100
        return -10
