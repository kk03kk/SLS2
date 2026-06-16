from __future__ import annotations

from sts2_sim.data import CardDef


CARD_LIBRARY: dict[str, CardDef] = {
    # Ironclad single-player cards. Each base card is followed by its upgraded version.
    "aggression": CardDef(
        id="aggression",
        name="Aggression",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "aggression",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="aggression_plus",
    ),
    "aggression_plus": CardDef(
        id="aggression_plus",
        name="Aggression+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "aggression",
                "amount": 1,
            },
        ),
        keywords=frozenset({"innate"}),
        exhausts_when_played=True,
    ),
    "anger": CardDef(
        id="anger",
        name="Anger",
        cost=0,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 6,
            },
            {
                "type": "add_card_to_discard",
                "card_id": "anger",
                "count": 1,
            },
        ),
        upgraded_id="anger_plus",
    ),
    "anger_plus": CardDef(
        id="anger_plus",
        name="Anger+",
        cost=0,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 8,
            },
            {
                "type": "add_card_to_discard",
                "card_id": "anger_plus",
                "count": 1,
            },
        ),
    ),
    "armaments": CardDef(
        id="armaments",
        name="Armaments",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 5,
            },
            {
                "type": "upgrade_from_hand",
            },
        ),
        upgraded_id="armaments_plus",
    ),
    "armaments_plus": CardDef(
        id="armaments_plus",
        name="Armaments+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 5,
            },
            {
                "type": "upgrade_from_hand",
                "all": True,
            },
        ),
    ),
    "ashen_strike": CardDef(
        id="ashen_strike",
        name="Ashen Strike",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "ashen_strike",
                "base": 6,
                "per_exhaust": 3,
            },
        ),
        keywords=frozenset({"strike"}),
        upgraded_id="ashen_strike_plus",
    ),
    "ashen_strike_plus": CardDef(
        id="ashen_strike_plus",
        name="Ashen Strike+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "ashen_strike",
                "base": 6,
                "per_exhaust": 4,
            },
        ),
        keywords=frozenset({"strike"}),
    ),
    "barricade": CardDef(
        id="barricade",
        name="Barricade",
        cost=3,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "barricade",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="barricade_plus",
    ),
    "barricade_plus": CardDef(
        id="barricade_plus",
        name="Barricade+",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "barricade",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "bash": CardDef(
        id="bash",
        name="Bash",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 8,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 2,
            },
        ),
        upgraded_id="bash_plus",
    ),
    "bash_plus": CardDef(
        id="bash_plus",
        name="Bash+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 10,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 3,
            },
        ),
    ),
    "battle_trance": CardDef(
        id="battle_trance",
        name="Battle Trance",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "draw_cards",
                "amount": 3,
            },
            {
                "type": "apply_power",
                "power": "no_draw",
                "amount": 1,
            },
        ),
        upgraded_id="battle_trance_plus",
    ),
    "battle_trance_plus": CardDef(
        id="battle_trance_plus",
        name="Battle Trance+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "draw_cards",
                "amount": 4,
            },
            {
                "type": "apply_power",
                "power": "no_draw",
                "amount": 1,
            },
        ),
    ),
    "blood_wall": CardDef(
        id="blood_wall",
        name="Blood Wall",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "hp_loss_then_block",
                "hp_loss": 2,
                "block": 16,
            },
        ),
        upgraded_id="blood_wall_plus",
    ),
    "blood_wall_plus": CardDef(
        id="blood_wall_plus",
        name="Blood Wall+",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "hp_loss_then_block",
                "hp_loss": 2,
                "block": 20,
            },
        ),
    ),
    "bloodletting": CardDef(
        id="bloodletting",
        name="Bloodletting",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "lose_hp",
                "amount": 3,
            },
            {
                "type": "gain_energy",
                "amount": 2,
            },
        ),
        upgraded_id="bloodletting_plus",
    ),
    "bloodletting_plus": CardDef(
        id="bloodletting_plus",
        name="Bloodletting+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "lose_hp",
                "amount": 3,
            },
            {
                "type": "gain_energy",
                "amount": 3,
            },
        ),
    ),
    "bludgeon": CardDef(
        id="bludgeon",
        name="Bludgeon",
        cost=3,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 32,
            },
        ),
        upgraded_id="bludgeon_plus",
    ),
    "bludgeon_plus": CardDef(
        id="bludgeon_plus",
        name="Bludgeon+",
        cost=3,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 42,
            },
        ),
    ),
    "body_slam": CardDef(
        id="body_slam",
        name="Body Slam",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "body_slam",
            },
        ),
        upgraded_id="body_slam_plus",
    ),
    "body_slam_plus": CardDef(
        id="body_slam_plus",
        name="Body Slam+",
        cost=0,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "body_slam",
            },
        ),
    ),
    "brand": CardDef(
        id="brand",
        name="Brand",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "lose_hp",
                "amount": 1,
            },
            {
                "type": "exhaust_from_hand",
                "mode": "chosen",
            },
            {
                "type": "apply_power",
                "power": "strength",
                "amount": 1,
            },
        ),
        upgraded_id="brand_plus",
    ),
    "brand_plus": CardDef(
        id="brand_plus",
        name="Brand+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "lose_hp",
                "amount": 1,
            },
            {
                "type": "exhaust_from_hand",
                "mode": "chosen",
            },
            {
                "type": "apply_power",
                "power": "strength",
                "amount": 2,
            },
        ),
    ),
    "break": CardDef(
        id="break",
        name="Break",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 20,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 5,
            },
        ),
        upgraded_id="break_plus",
    ),
    "break_plus": CardDef(
        id="break_plus",
        name="Break+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 30,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 7,
            },
        ),
    ),
    "breakthrough": CardDef(
        id="breakthrough",
        name="Breakthrough",
        cost=1,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "lose_hp",
                "amount": 1,
            },
            {
                "type": "deal_damage_all",
                "amount": 9,
            },
        ),
        upgraded_id="breakthrough_plus",
    ),
    "breakthrough_plus": CardDef(
        id="breakthrough_plus",
        name="Breakthrough+",
        cost=1,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "lose_hp",
                "amount": 1,
            },
            {
                "type": "deal_damage_all",
                "amount": 13,
            },
        ),
    ),
    "bully": CardDef(
        id="bully",
        name="Bully",
        cost=0,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "bully",
                "base": 4,
                "per_vulnerable": 2,
            },
        ),
        upgraded_id="bully_plus",
    ),
    "bully_plus": CardDef(
        id="bully_plus",
        name="Bully+",
        cost=0,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "bully",
                "base": 4,
                "per_vulnerable": 3,
            },
        ),
    ),
    "burning_pact": CardDef(
        id="burning_pact",
        name="Burning Pact",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "exhaust_from_hand",
                "mode": "chosen",
            },
            {
                "type": "draw_cards",
                "amount": 2,
            },
        ),
        upgraded_id="burning_pact_plus",
    ),
    "burning_pact_plus": CardDef(
        id="burning_pact_plus",
        name="Burning Pact+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "exhaust_from_hand",
                "mode": "chosen",
            },
            {
                "type": "draw_cards",
                "amount": 3,
            },
        ),
    ),
    "cascade": CardDef(
        id="cascade",
        name="Cascade",
        cost=-1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "auto_play_from_draw",
                "x_cost": True,
            },
        ),
        upgraded_id="cascade_plus",
    ),
    "cascade_plus": CardDef(
        id="cascade_plus",
        name="Cascade+",
        cost=-1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "auto_play_from_draw",
                "x_cost": True,
                "bonus": 1,
            },
        ),
    ),
    "cinder": CardDef(
        id="cinder",
        name="Cinder",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 18,
            },
            {
                "type": "exhaust_from_hand",
                "mode": "random",
            },
        ),
        upgraded_id="cinder_plus",
    ),
    "cinder_plus": CardDef(
        id="cinder_plus",
        name="Cinder+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 24,
            },
            {
                "type": "exhaust_from_hand",
                "mode": "random",
            },
        ),
    ),
    "colossus": CardDef(
        id="colossus",
        name="Colossus",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 5,
            },
            {
                "type": "apply_power",
                "power": "colossus",
                "amount": 1,
            },
        ),
        upgraded_id="colossus_plus",
    ),
    "colossus_plus": CardDef(
        id="colossus_plus",
        name="Colossus+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 8,
            },
            {
                "type": "apply_power",
                "power": "colossus",
                "amount": 1,
            },
        ),
    ),
    "conflagration": CardDef(
        id="conflagration",
        name="Conflagration",
        cost=1,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 2,
                "hits": 4,
            },
        ),
        upgraded_id="conflagration_plus",
    ),
    "conflagration_plus": CardDef(
        id="conflagration_plus",
        name="Conflagration+",
        cost=1,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 2,
                "hits": 5,
            },
        ),
    ),
    "corruption": CardDef(
        id="corruption",
        name="Corruption",
        cost=3,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "corruption",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="corruption_plus",
    ),
    "corruption_plus": CardDef(
        id="corruption_plus",
        name="Corruption+",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "corruption",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "crimson_mantle": CardDef(
        id="crimson_mantle",
        name="Crimson Mantle",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "crimson_mantle",
                "amount": 8,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="crimson_mantle_plus",
    ),
    "crimson_mantle_plus": CardDef(
        id="crimson_mantle_plus",
        name="Crimson Mantle+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "crimson_mantle",
                "amount": 10,
            },
        ),
        exhausts_when_played=True,
    ),
    "cruelty": CardDef(
        id="cruelty",
        name="Cruelty",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "cruelty",
                "amount": 25,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="cruelty_plus",
    ),
    "cruelty_plus": CardDef(
        id="cruelty_plus",
        name="Cruelty+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "cruelty",
                "amount": 50,
            },
        ),
        exhausts_when_played=True,
    ),
    "dark_embrace": CardDef(
        id="dark_embrace",
        name="Dark Embrace",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "dark_embrace",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="dark_embrace_plus",
    ),
    "dark_embrace_plus": CardDef(
        id="dark_embrace_plus",
        name="Dark Embrace+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "dark_embrace",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "defend_ironclad": CardDef(
        id="defend_ironclad",
        name="Defend",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 5,
            },
        ),
        keywords=frozenset({"defend"}),
        upgraded_id="defend_ironclad_plus",
    ),
    "defend_ironclad_plus": CardDef(
        id="defend_ironclad_plus",
        name="Defend+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 8,
            },
        ),
        keywords=frozenset({"defend"}),
    ),
    "demon_form": CardDef(
        id="demon_form",
        name="Demon Form",
        cost=3,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "demon_form",
                "amount": 2,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="demon_form_plus",
    ),
    "demon_form_plus": CardDef(
        id="demon_form_plus",
        name="Demon Form+",
        cost=3,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "demon_form",
                "amount": 3,
            },
        ),
        exhausts_when_played=True,
    ),
    "dismantle": CardDef(
        id="dismantle",
        name="Dismantle",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "dismantle",
                "amount": 8,
            },
        ),
        upgraded_id="dismantle_plus",
    ),
    "dismantle_plus": CardDef(
        id="dismantle_plus",
        name="Dismantle+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "dismantle",
                "amount": 10,
            },
        ),
    ),
    "dominate": CardDef(
        id="dominate",
        name="Dominate",
        cost=1,
        card_type="skill",
        target="enemy",
        effects=(
            {
                "type": "dominate",
                "vulnerable": 1,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="dominate_plus",
    ),
    "dominate_plus": CardDef(
        id="dominate_plus",
        name="Dominate+",
        cost=1,
        card_type="skill",
        target="enemy",
        effects=(
            {
                "type": "dominate",
                "vulnerable": 2,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "drum_of_battle": CardDef(
        id="drum_of_battle",
        name="Drum Of Battle",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "draw_cards",
                "amount": 2,
            },
        ),
        upgraded_id="drum_of_battle_plus",
    ),
    "drum_of_battle_plus": CardDef(
        id="drum_of_battle_plus",
        name="Drum Of Battle+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "draw_cards",
                "amount": 2,
            },
        ),
    ),
    "evil_eye": CardDef(
        id="evil_eye",
        name="Evil Eye",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "if_exhausted_this_turn_gain_block",
                "amount": 8,
            },
        ),
        upgraded_id="evil_eye_plus",
    ),
    "evil_eye_plus": CardDef(
        id="evil_eye_plus",
        name="Evil Eye+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "if_exhausted_this_turn_gain_block",
                "amount": 11,
            },
        ),
    ),
    "expect_a_fight": CardDef(
        id="expect_a_fight",
        name="Expect A Fight",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_energy_per_attack_in_hand",
            },
        ),
        upgraded_id="expect_a_fight_plus",
    ),
    "expect_a_fight_plus": CardDef(
        id="expect_a_fight_plus",
        name="Expect A Fight+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_energy_per_attack_in_hand",
            },
        ),
    ),
    "feed": CardDef(
        id="feed",
        name="Feed",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "feed",
                "amount": 10,
                "max_hp": 3,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="feed_plus",
    ),
    "feed_plus": CardDef(
        id="feed_plus",
        name="Feed+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "feed",
                "amount": 12,
                "max_hp": 4,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "feel_no_pain": CardDef(
        id="feel_no_pain",
        name="Feel No Pain",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "feel_no_pain",
                "amount": 3,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="feel_no_pain_plus",
    ),
    "feel_no_pain_plus": CardDef(
        id="feel_no_pain_plus",
        name="Feel No Pain+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "feel_no_pain",
                "amount": 4,
            },
        ),
        exhausts_when_played=True,
    ),
    "fiend_fire": CardDef(
        id="fiend_fire",
        name="Fiend Fire",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "fiend_fire",
                "amount": 7,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="fiend_fire_plus",
    ),
    "fiend_fire_plus": CardDef(
        id="fiend_fire_plus",
        name="Fiend Fire+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "fiend_fire",
                "amount": 10,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "fight_me": CardDef(
        id="fight_me",
        name="Fight Me",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "fight_me",
                "amount": 5,
                "hits": 2,
                "player_strength": 3,
                "enemy_strength": 1,
            },
        ),
        upgraded_id="fight_me_plus",
    ),
    "fight_me_plus": CardDef(
        id="fight_me_plus",
        name="Fight Me+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "fight_me",
                "amount": 6,
                "hits": 2,
                "player_strength": 4,
                "enemy_strength": 1,
            },
        ),
    ),
    "flame_barrier": CardDef(
        id="flame_barrier",
        name="Flame Barrier",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 12,
            },
            {
                "type": "apply_power",
                "power": "flame_barrier",
                "amount": 4,
            },
        ),
        upgraded_id="flame_barrier_plus",
    ),
    "flame_barrier_plus": CardDef(
        id="flame_barrier_plus",
        name="Flame Barrier+",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 16,
            },
            {
                "type": "apply_power",
                "power": "flame_barrier",
                "amount": 6,
            },
        ),
    ),
    "forgotten_ritual": CardDef(
        id="forgotten_ritual",
        name="Forgotten Ritual",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "if_exhausted_this_turn_gain_energy",
                "amount": 3,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="forgotten_ritual_plus",
    ),
    "forgotten_ritual_plus": CardDef(
        id="forgotten_ritual_plus",
        name="Forgotten Ritual+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "if_exhausted_this_turn_gain_energy",
                "amount": 4,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "havoc": CardDef(
        id="havoc",
        name="Havoc",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "auto_play_from_draw",
                "count": 1,
                "force_exhaust": True,
            },
        ),
        upgraded_id="havoc_plus",
    ),
    "havoc_plus": CardDef(
        id="havoc_plus",
        name="Havoc+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "auto_play_from_draw",
                "count": 1,
                "force_exhaust": True,
            },
        ),
    ),
    "headbutt": CardDef(
        id="headbutt",
        name="Headbutt",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 9,
            },
            {
                "type": "move_discard_to_draw_top",
            },
        ),
        upgraded_id="headbutt_plus",
    ),
    "headbutt_plus": CardDef(
        id="headbutt_plus",
        name="Headbutt+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 12,
            },
            {
                "type": "move_discard_to_draw_top",
            },
        ),
    ),
    "hellraiser": CardDef(
        id="hellraiser",
        name="Hellraiser",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "hellraiser",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="hellraiser_plus",
    ),
    "hellraiser_plus": CardDef(
        id="hellraiser_plus",
        name="Hellraiser+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "hellraiser",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "hemokinesis": CardDef(
        id="hemokinesis",
        name="Hemokinesis",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "lose_hp",
                "amount": 2,
            },
            {
                "type": "deal_damage",
                "amount": 15,
            },
        ),
        upgraded_id="hemokinesis_plus",
    ),
    "hemokinesis_plus": CardDef(
        id="hemokinesis_plus",
        name="Hemokinesis+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "lose_hp",
                "amount": 2,
            },
            {
                "type": "deal_damage",
                "amount": 20,
            },
        ),
    ),
    "howl_from_beyond": CardDef(
        id="howl_from_beyond",
        name="Howl From Beyond",
        cost=3,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 16,
            },
        ),
        upgraded_id="howl_from_beyond_plus",
    ),
    "howl_from_beyond_plus": CardDef(
        id="howl_from_beyond_plus",
        name="Howl From Beyond+",
        cost=3,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 21,
            },
        ),
    ),
    "impervious": CardDef(
        id="impervious",
        name="Impervious",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 30,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="impervious_plus",
    ),
    "impervious_plus": CardDef(
        id="impervious_plus",
        name="Impervious+",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 40,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "infernal_blade": CardDef(
        id="infernal_blade",
        name="Infernal Blade",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "add_random_attack_to_hand",
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="infernal_blade_plus",
    ),
    "infernal_blade_plus": CardDef(
        id="infernal_blade_plus",
        name="Infernal Blade+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "add_random_attack_to_hand",
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "inferno": CardDef(
        id="inferno",
        name="Inferno",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "inferno",
                "amount": 6,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="inferno_plus",
    ),
    "inferno_plus": CardDef(
        id="inferno_plus",
        name="Inferno+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "inferno",
                "amount": 9,
            },
        ),
        exhausts_when_played=True,
    ),
    "inflame": CardDef(
        id="inflame",
        name="Inflame",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "strength",
                "amount": 2,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="inflame_plus",
    ),
    "inflame_plus": CardDef(
        id="inflame_plus",
        name="Inflame+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "strength",
                "amount": 3,
            },
        ),
        exhausts_when_played=True,
    ),
    "iron_wave": CardDef(
        id="iron_wave",
        name="Iron Wave",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "gain_block",
                "amount": 5,
            },
            {
                "type": "deal_damage",
                "amount": 5,
            },
        ),
        upgraded_id="iron_wave_plus",
    ),
    "iron_wave_plus": CardDef(
        id="iron_wave_plus",
        name="Iron Wave+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "gain_block",
                "amount": 7,
            },
            {
                "type": "deal_damage",
                "amount": 7,
            },
        ),
    ),
    "juggernaut": CardDef(
        id="juggernaut",
        name="Juggernaut",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "juggernaut",
                "amount": 6,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="juggernaut_plus",
    ),
    "juggernaut_plus": CardDef(
        id="juggernaut_plus",
        name="Juggernaut+",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "juggernaut",
                "amount": 8,
            },
        ),
        exhausts_when_played=True,
    ),
    "juggling": CardDef(
        id="juggling",
        name="Juggling",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "juggling",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="juggling_plus",
    ),
    "juggling_plus": CardDef(
        id="juggling_plus",
        name="Juggling+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "juggling",
                "amount": 1,
            },
        ),
        keywords=frozenset({"innate"}),
        exhausts_when_played=True,
    ),
    "mangle": CardDef(
        id="mangle",
        name="Mangle",
        cost=3,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "mangle",
                "amount": 15,
                "strength_loss": 10,
            },
        ),
        upgraded_id="mangle_plus",
    ),
    "mangle_plus": CardDef(
        id="mangle_plus",
        name="Mangle+",
        cost=3,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "mangle",
                "amount": 20,
                "strength_loss": 15,
            },
        ),
    ),
    "molten_fist": CardDef(
        id="molten_fist",
        name="Molten Fist",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "molten_fist",
                "amount": 10,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="molten_fist_plus",
    ),
    "molten_fist_plus": CardDef(
        id="molten_fist_plus",
        name="Molten Fist+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "molten_fist",
                "amount": 14,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "not_yet": CardDef(
        id="not_yet",
        name="Not Yet",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "heal",
                "amount": 10,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="not_yet_plus",
    ),
    "not_yet_plus": CardDef(
        id="not_yet_plus",
        name="Not Yet+",
        cost=2,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "heal",
                "amount": 13,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "offering": CardDef(
        id="offering",
        name="Offering",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "lose_hp",
                "amount": 6,
            },
            {
                "type": "gain_energy",
                "amount": 2,
            },
            {
                "type": "draw_cards",
                "amount": 3,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="offering_plus",
    ),
    "offering_plus": CardDef(
        id="offering_plus",
        name="Offering+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "lose_hp",
                "amount": 6,
            },
            {
                "type": "gain_energy",
                "amount": 2,
            },
            {
                "type": "draw_cards",
                "amount": 5,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "one_two_punch": CardDef(
        id="one_two_punch",
        name="One Two Punch",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "one_two_punch",
                "amount": 1,
            },
        ),
        upgraded_id="one_two_punch_plus",
    ),
    "one_two_punch_plus": CardDef(
        id="one_two_punch_plus",
        name="One Two Punch+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "one_two_punch",
                "amount": 2,
            },
        ),
    ),
    "pacts_end": CardDef(
        id="pacts_end",
        name="Pact's End",
        cost=0,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "conditional_damage_all",
                "amount": 17,
                "minimum_exhaust": 3,
            },
        ),
        upgraded_id="pacts_end_plus",
    ),
    "pacts_end_plus": CardDef(
        id="pacts_end_plus",
        name="Pact's End+",
        cost=0,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "conditional_damage_all",
                "amount": 23,
                "minimum_exhaust": 3,
            },
        ),
    ),
    "perfected_strike": CardDef(
        id="perfected_strike",
        name="Perfected Strike",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "perfected_strike",
                "base": 6,
                "per_strike": 2,
            },
        ),
        keywords=frozenset({"strike"}),
        upgraded_id="perfected_strike_plus",
    ),
    "perfected_strike_plus": CardDef(
        id="perfected_strike_plus",
        name="Perfected Strike+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "perfected_strike",
                "base": 6,
                "per_strike": 3,
            },
        ),
        keywords=frozenset({"strike"}),
    ),
    "pillage": CardDef(
        id="pillage",
        name="Pillage",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "pillage",
                "amount": 6,
            },
        ),
        upgraded_id="pillage_plus",
    ),
    "pillage_plus": CardDef(
        id="pillage_plus",
        name="Pillage+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "pillage",
                "amount": 9,
            },
        ),
    ),
    "pommel_strike": CardDef(
        id="pommel_strike",
        name="Pommel Strike",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 9,
            },
            {
                "type": "draw_cards",
                "amount": 1,
            },
        ),
        keywords=frozenset({"strike"}),
        upgraded_id="pommel_strike_plus",
    ),
    "pommel_strike_plus": CardDef(
        id="pommel_strike_plus",
        name="Pommel Strike+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 10,
            },
            {
                "type": "draw_cards",
                "amount": 2,
            },
        ),
        keywords=frozenset({"strike"}),
    ),
    "primal_force": CardDef(
        id="primal_force",
        name="Primal Force",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "transform_attacks_to_strikes",
                "card_id": "giant_rock",
            },
        ),
        upgraded_id="primal_force_plus",
    ),
    "primal_force_plus": CardDef(
        id="primal_force_plus",
        name="Primal Force+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "transform_attacks_to_strikes",
                "card_id": "giant_rock_plus",
            },
        ),
    ),
    "pyre": CardDef(
        id="pyre",
        name="Pyre",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "pyre",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="pyre_plus",
    ),
    "pyre_plus": CardDef(
        id="pyre_plus",
        name="Pyre+",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "pyre",
                "amount": 2,
            },
        ),
        exhausts_when_played=True,
    ),
    "rage": CardDef(
        id="rage",
        name="Rage",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "rage",
                "amount": 3,
            },
        ),
        upgraded_id="rage_plus",
    ),
    "rage_plus": CardDef(
        id="rage_plus",
        name="Rage+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "rage",
                "amount": 5,
            },
        ),
    ),
    "rampage": CardDef(
        id="rampage",
        name="Rampage",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "rampage",
                "amount": 9,
                "increase": 5,
            },
        ),
        upgraded_id="rampage_plus",
    ),
    "rampage_plus": CardDef(
        id="rampage_plus",
        name="Rampage+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "rampage",
                "amount": 9,
                "increase": 9,
            },
        ),
    ),
    "rupture": CardDef(
        id="rupture",
        name="Rupture",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "rupture",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="rupture_plus",
    ),
    "rupture_plus": CardDef(
        id="rupture_plus",
        name="Rupture+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "rupture",
                "amount": 2,
            },
        ),
        exhausts_when_played=True,
    ),
    "second_wind": CardDef(
        id="second_wind",
        name="Second Wind",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "exhaust_non_attacks_gain_block",
                "block": 5,
            },
        ),
        upgraded_id="second_wind_plus",
    ),
    "second_wind_plus": CardDef(
        id="second_wind_plus",
        name="Second Wind+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "exhaust_non_attacks_gain_block",
                "block": 7,
            },
        ),
    ),
    "setup_strike": CardDef(
        id="setup_strike",
        name="Setup Strike",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "setup_strike",
                "amount": 7,
                "strength": 2,
            },
        ),
        keywords=frozenset({"strike"}),
        upgraded_id="setup_strike_plus",
    ),
    "setup_strike_plus": CardDef(
        id="setup_strike_plus",
        name="Setup Strike+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "setup_strike",
                "amount": 9,
                "strength": 3,
            },
        ),
        keywords=frozenset({"strike"}),
    ),
    "shrug_it_off": CardDef(
        id="shrug_it_off",
        name="Shrug It Off",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 8,
            },
            {
                "type": "draw_cards",
                "amount": 1,
            },
        ),
        upgraded_id="shrug_it_off_plus",
    ),
    "shrug_it_off_plus": CardDef(
        id="shrug_it_off_plus",
        name="Shrug It Off+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 11,
            },
            {
                "type": "draw_cards",
                "amount": 1,
            },
        ),
    ),
    "spite": CardDef(
        id="spite",
        name="Spite",
        cost=0,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "damage_if_lost_hp",
                "amount": 5,
                "hits_if_lost": 2,
            },
        ),
        upgraded_id="spite_plus",
    ),
    "spite_plus": CardDef(
        id="spite_plus",
        name="Spite+",
        cost=0,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "damage_if_lost_hp",
                "amount": 5,
                "hits_if_lost": 3,
            },
        ),
    ),
    "stampede": CardDef(
        id="stampede",
        name="Stampede",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "stampede",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="stampede_plus",
    ),
    "stampede_plus": CardDef(
        id="stampede_plus",
        name="Stampede+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "stampede",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "stoke": CardDef(
        id="stoke",
        name="Stoke",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "stoke",
            },
        ),
        upgraded_id="stoke_plus",
    ),
    "stoke_plus": CardDef(
        id="stoke_plus",
        name="Stoke+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "stoke",
                "upgraded": True,
            },
        ),
    ),
    "stomp": CardDef(
        id="stomp",
        name="Stomp",
        cost=3,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 12,
            },
        ),
        upgraded_id="stomp_plus",
    ),
    "stomp_plus": CardDef(
        id="stomp_plus",
        name="Stomp+",
        cost=3,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 15,
            },
        ),
    ),
    "stone_armor": CardDef(
        id="stone_armor",
        name="Stone Armor",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "plating",
                "amount": 4,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="stone_armor_plus",
    ),
    "stone_armor_plus": CardDef(
        id="stone_armor_plus",
        name="Stone Armor+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "plating",
                "amount": 6,
            },
        ),
        exhausts_when_played=True,
    ),
    "strike_ironclad": CardDef(
        id="strike_ironclad",
        name="Strike",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 6,
            },
        ),
        keywords=frozenset({"strike"}),
        upgraded_id="strike_ironclad_plus",
    ),
    "strike_ironclad_plus": CardDef(
        id="strike_ironclad_plus",
        name="Strike+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 9,
            },
        ),
        keywords=frozenset({"strike"}),
    ),
    "sword_boomerang": CardDef(
        id="sword_boomerang",
        name="Sword Boomerang",
        cost=1,
        card_type="attack",
        target="none",
        effects=(
            {
                "type": "random_enemy_damage",
                "amount": 3,
                "hits": 3,
            },
        ),
        upgraded_id="sword_boomerang_plus",
    ),
    "sword_boomerang_plus": CardDef(
        id="sword_boomerang_plus",
        name="Sword Boomerang+",
        cost=1,
        card_type="attack",
        target="none",
        effects=(
            {
                "type": "random_enemy_damage",
                "amount": 3,
                "hits": 4,
            },
        ),
    ),
    "taunt": CardDef(
        id="taunt",
        name="Taunt",
        cost=1,
        card_type="skill",
        target="enemy",
        effects=(
            {
                "type": "gain_block",
                "amount": 7,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 1,
            },
        ),
        upgraded_id="taunt_plus",
    ),
    "taunt_plus": CardDef(
        id="taunt_plus",
        name="Taunt+",
        cost=1,
        card_type="skill",
        target="enemy",
        effects=(
            {
                "type": "gain_block",
                "amount": 8,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 2,
            },
        ),
    ),
    "tear_asunder": CardDef(
        id="tear_asunder",
        name="Tear Asunder",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "tear_asunder",
                "amount": 5,
            },
        ),
        upgraded_id="tear_asunder_plus",
    ),
    "tear_asunder_plus": CardDef(
        id="tear_asunder_plus",
        name="Tear Asunder+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "tear_asunder",
                "amount": 7,
            },
        ),
    ),
    "thrash": CardDef(
        id="thrash",
        name="Thrash",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "thrash",
                "amount": 4,
            },
        ),
        upgraded_id="thrash_plus",
    ),
    "thrash_plus": CardDef(
        id="thrash_plus",
        name="Thrash+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "thrash",
                "amount": 6,
            },
        ),
    ),
    "thunderclap": CardDef(
        id="thunderclap",
        name="Thunderclap",
        cost=1,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 4,
            },
            {
                "type": "apply_power_all_enemies",
                "power": "vulnerable",
                "amount": 1,
            },
        ),
        upgraded_id="thunderclap_plus",
    ),
    "thunderclap_plus": CardDef(
        id="thunderclap_plus",
        name="Thunderclap+",
        cost=1,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "deal_damage_all",
                "amount": 7,
            },
            {
                "type": "apply_power_all_enemies",
                "power": "vulnerable",
                "amount": 1,
            },
        ),
    ),
    "tremble": CardDef(
        id="tremble",
        name="Tremble",
        cost=1,
        card_type="skill",
        target="enemy",
        effects=(
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 3,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="tremble_plus",
    ),
    "tremble_plus": CardDef(
        id="tremble_plus",
        name="Tremble+",
        cost=1,
        card_type="skill",
        target="enemy",
        effects=(
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 4,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "true_grit": CardDef(
        id="true_grit",
        name="True Grit",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 7,
            },
            {
                "type": "exhaust_from_hand",
                "mode": "random",
            },
        ),
        upgraded_id="true_grit_plus",
    ),
    "true_grit_plus": CardDef(
        id="true_grit_plus",
        name="True Grit+",
        cost=1,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "gain_block",
                "amount": 9,
            },
            {
                "type": "exhaust_from_hand",
                "mode": "chosen",
            },
        ),
    ),
    "twin_strike": CardDef(
        id="twin_strike",
        name="Twin Strike",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 5,
                "hits": 2,
            },
        ),
        keywords=frozenset({"strike"}),
        upgraded_id="twin_strike_plus",
    ),
    "twin_strike_plus": CardDef(
        id="twin_strike_plus",
        name="Twin Strike+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 7,
                "hits": 2,
            },
        ),
        keywords=frozenset({"strike"}),
    ),
    "unmovable": CardDef(
        id="unmovable",
        name="Unmovable",
        cost=2,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "unmovable",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="unmovable_plus",
    ),
    "unmovable_plus": CardDef(
        id="unmovable_plus",
        name="Unmovable+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "unmovable",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "unrelenting": CardDef(
        id="unrelenting",
        name="Unrelenting",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 14,
            },
            {
                "type": "apply_power",
                "power": "free_attack",
                "amount": 1,
                "recipient": "self",
            },
        ),
        upgraded_id="unrelenting_plus",
    ),
    "unrelenting_plus": CardDef(
        id="unrelenting_plus",
        name="Unrelenting+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 20,
            },
            {
                "type": "apply_power",
                "power": "free_attack",
                "amount": 1,
                "recipient": "self",
            },
        ),
    ),
    "uppercut": CardDef(
        id="uppercut",
        name="Uppercut",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 13,
            },
            {
                "type": "apply_power",
                "power": "weak",
                "amount": 1,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 1,
            },
        ),
        upgraded_id="uppercut_plus",
    ),
    "uppercut_plus": CardDef(
        id="uppercut_plus",
        name="Uppercut+",
        cost=2,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 13,
            },
            {
                "type": "apply_power",
                "power": "weak",
                "amount": 2,
            },
            {
                "type": "apply_power",
                "power": "vulnerable",
                "amount": 2,
            },
        ),
    ),
    "vicious": CardDef(
        id="vicious",
        name="Vicious",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "vicious",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="vicious_plus",
    ),
    "vicious_plus": CardDef(
        id="vicious_plus",
        name="Vicious+",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "vicious",
                "amount": 2,
            },
        ),
        exhausts_when_played=True,
    ),
    "whirlwind": CardDef(
        id="whirlwind",
        name="Whirlwind",
        cost=0,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "whirlwind",
                "amount": 5,
            },
        ),
        upgraded_id="whirlwind_plus",
    ),
    "whirlwind_plus": CardDef(
        id="whirlwind_plus",
        name="Whirlwind+",
        cost=0,
        card_type="attack",
        target="all_enemies",
        effects=(
            {
                "type": "whirlwind",
                "amount": 8,
            },
        ),
    ),

    # Special, status, curse, debug, and multiplayer-only cards used by combat effects.
    "giant_rock": CardDef(
        id="giant_rock",
        name="Giant Rock",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 16,
            },
        ),
        upgraded_id="giant_rock_plus",
    ),
    "giant_rock_plus": CardDef(
        id="giant_rock_plus",
        name="Giant Rock+",
        cost=1,
        card_type="attack",
        target="enemy",
        effects=(
            {
                "type": "deal_damage",
                "amount": 20,
            },
        ),
    ),
    "ascenders_bane": CardDef(
        id="ascenders_bane",
        name="Ascender's Bane",
        cost=-1,
        card_type="curse",
        target="none",
        keywords=frozenset({"eternal", "ethereal", "unplayable"}),
    ),
    "slimed": CardDef(
        id="slimed",
        name="Slimed",
        cost=1,
        card_type="status",
        target="none",
        effects=(
            {
                "type": "draw_cards",
                "amount": 1,
            },
        ),
        keywords=frozenset({"exhaust"}),
    ),
    "dazed": CardDef(
        id="dazed",
        name="Dazed",
        cost=-1,
        card_type="status",
        target="none",
        keywords=frozenset({"ethereal", "unplayable"}),
    ),
    "beckon": CardDef(
        id="beckon",
        name="Beckon",
        cost=1,
        card_type="status",
        target="none",
    ),
    "buffer_debug": CardDef(
        id="buffer_debug",
        name="Buffer Debug",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "buffer",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "intangible_debug": CardDef(
        id="intangible_debug",
        name="Intangible Debug",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "intangible",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
    "demonic_shield": CardDef(
        id="demonic_shield",
        name="Demonic Shield",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "hp_loss_then_block",
                "hp_loss": 1,
                "block": 12,
            },
        ),
        keywords=frozenset({"exhaust"}),
        upgraded_id="demonic_shield_plus",
    ),
    "demonic_shield_plus": CardDef(
        id="demonic_shield_plus",
        name="Demonic Shield+",
        cost=0,
        card_type="skill",
        target="self",
        effects=(
            {
                "type": "hp_loss_then_block",
                "hp_loss": 1,
                "block": 12,
            },
        ),
    ),
    "tank": CardDef(
        id="tank",
        name="Tank",
        cost=1,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "tank",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
        upgraded_id="tank_plus",
    ),
    "tank_plus": CardDef(
        id="tank_plus",
        name="Tank+",
        cost=0,
        card_type="power",
        target="self",
        effects=(
            {
                "type": "apply_power",
                "power": "tank",
                "amount": 1,
            },
        ),
        exhausts_when_played=True,
    ),
}



def ironclad_a10_starting_deck() -> list[str]:
    return (
        ["strike_ironclad"] * 5
        + ["defend_ironclad"] * 4
        + ["bash"]
        + ["ascenders_bane"]
    )


def ironclad_a0_starting_deck() -> list[str]:
    return ["strike_ironclad"] * 5 + ["defend_ironclad"] * 4 + ["bash"]


IRONCLAD_MULTIPLAYER_ONLY = frozenset({"demonic_shield", "tank"})
IRONCLAD_BASIC_CARDS = frozenset({"strike_ironclad", "defend_ironclad", "bash"})
IRONCLAD_ANCIENT_CARDS = frozenset({"break", "corruption"})
IRONCLAD_NOT_GENERATED_IN_COMBAT = frozenset({"feed", "not_yet"})


IRONCLAD_SINGLEPLAYER_POOL = tuple(
    card_id
    for card_id in (
        "aggression",
        "anger",
        "armaments",
        "ashen_strike",
        "barricade",
        "bash",
        "battle_trance",
        "blood_wall",
        "bloodletting",
        "bludgeon",
        "body_slam",
        "brand",
        "break",
        "breakthrough",
        "bully",
        "burning_pact",
        "cascade",
        "cinder",
        "colossus",
        "conflagration",
        "corruption",
        "crimson_mantle",
        "cruelty",
        "dark_embrace",
        "defend_ironclad",
        "demon_form",
        "dismantle",
        "dominate",
        "drum_of_battle",
        "evil_eye",
        "expect_a_fight",
        "feed",
        "feel_no_pain",
        "fiend_fire",
        "fight_me",
        "flame_barrier",
        "forgotten_ritual",
        "havoc",
        "headbutt",
        "hellraiser",
        "hemokinesis",
        "howl_from_beyond",
        "impervious",
        "infernal_blade",
        "inferno",
        "inflame",
        "iron_wave",
        "juggernaut",
        "juggling",
        "mangle",
        "molten_fist",
        "not_yet",
        "offering",
        "one_two_punch",
        "pacts_end",
        "perfected_strike",
        "pillage",
        "pommel_strike",
        "primal_force",
        "pyre",
        "rage",
        "rampage",
        "rupture",
        "second_wind",
        "setup_strike",
        "shrug_it_off",
        "spite",
        "stampede",
        "stoke",
        "stomp",
        "stone_armor",
        "strike_ironclad",
        "sword_boomerang",
        "taunt",
        "tear_asunder",
        "thrash",
        "thunderclap",
        "tremble",
        "true_grit",
        "twin_strike",
        "unmovable",
        "unrelenting",
        "uppercut",
        "vicious",
        "whirlwind",
    )
    if card_id not in IRONCLAD_MULTIPLAYER_ONLY
)


def ironclad_singleplayer_card_pool() -> list[str]:
    return list(IRONCLAD_SINGLEPLAYER_POOL)


def ironclad_singleplayer_generation_pool() -> list[str]:
    return [
        card_id
        for card_id in IRONCLAD_SINGLEPLAYER_POOL
        if card_id not in IRONCLAD_BASIC_CARDS
        and card_id not in IRONCLAD_ANCIENT_CARDS
        and card_id not in IRONCLAD_NOT_GENERATED_IN_COMBAT
    ]


IRONCLAD_CARD_RARITIES = {
    "aggression": "rare",
    "anger": "common",
    "armaments": "common",
    "ashen_strike": "uncommon",
    "barricade": "rare",
    "bash": "basic",
    "battle_trance": "uncommon",
    "blood_wall": "common",
    "bloodletting": "common",
    "bludgeon": "uncommon",
    "body_slam": "common",
    "brand": "rare",
    "break": "ancient",
    "breakthrough": "common",
    "bully": "uncommon",
    "burning_pact": "uncommon",
    "cascade": "rare",
    "cinder": "common",
    "colossus": "uncommon",
    "conflagration": "rare",
    "corruption": "ancient",
    "crimson_mantle": "rare",
    "cruelty": "rare",
    "dark_embrace": "rare",
    "defend_ironclad": "basic",
    "demon_form": "rare",
    "dismantle": "uncommon",
    "dominate": "uncommon",
    "drum_of_battle": "uncommon",
    "evil_eye": "uncommon",
    "expect_a_fight": "uncommon",
    "feed": "rare",
    "feel_no_pain": "uncommon",
    "fiend_fire": "rare",
    "fight_me": "uncommon",
    "flame_barrier": "uncommon",
    "forgotten_ritual": "uncommon",
    "havoc": "common",
    "headbutt": "common",
    "hellraiser": "rare",
    "hemokinesis": "uncommon",
    "howl_from_beyond": "uncommon",
    "impervious": "rare",
    "infernal_blade": "uncommon",
    "inferno": "uncommon",
    "inflame": "uncommon",
    "iron_wave": "common",
    "juggernaut": "rare",
    "juggling": "uncommon",
    "mangle": "rare",
    "molten_fist": "common",
    "not_yet": "rare",
    "offering": "rare",
    "one_two_punch": "rare",
    "pacts_end": "rare",
    "perfected_strike": "common",
    "pillage": "uncommon",
    "pommel_strike": "common",
    "primal_force": "rare",
    "pyre": "rare",
    "rage": "uncommon",
    "rampage": "uncommon",
    "rupture": "uncommon",
    "second_wind": "uncommon",
    "setup_strike": "common",
    "shrug_it_off": "common",
    "spite": "uncommon",
    "stampede": "uncommon",
    "stoke": "rare",
    "stomp": "uncommon",
    "stone_armor": "uncommon",
    "strike_ironclad": "basic",
    "sword_boomerang": "common",
    "taunt": "uncommon",
    "tear_asunder": "rare",
    "thrash": "rare",
    "thunderclap": "common",
    "tremble": "common",
    "true_grit": "common",
    "twin_strike": "common",
    "unmovable": "rare",
    "unrelenting": "uncommon",
    "uppercut": "uncommon",
    "vicious": "uncommon",
    "whirlwind": "uncommon",
}


for _card_id, _rarity in IRONCLAD_CARD_RARITIES.items():
    if _card_id in CARD_LIBRARY:
        object.__setattr__(CARD_LIBRARY[_card_id], "rarity", _rarity)
        upgraded_id = CARD_LIBRARY[_card_id].upgraded_id
        if upgraded_id is not None and upgraded_id in CARD_LIBRARY:
            object.__setattr__(CARD_LIBRARY[upgraded_id], "rarity", _rarity)


def ironclad_singleplayer_reward_pool() -> list[str]:
    return [
        card_id
        for card_id in IRONCLAD_SINGLEPLAYER_POOL
        if IRONCLAD_CARD_RARITIES.get(card_id) in {"common", "uncommon", "rare"}
    ]
