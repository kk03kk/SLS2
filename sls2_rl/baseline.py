from __future__ import annotations

from .combat_env import MAX_HAND, SlS2CombatEnv
from .data import CARDS


def choose_rule_action(env: SlS2CombatEnv) -> int:
    mask = env.action_masks()
    best_action = MAX_HAND
    best_score = -1.0
    incoming = env.enemy.move_for_turn(env.turn).damage * env.enemy.move_for_turn(env.turn).hits
    for i, card_id in enumerate(env.hand):
        if not mask[i]:
            continue
        card = CARDS[card_id]
        score = card.damage * 1.5 + card.block + card.strength * 4 + card.vulnerable * 2 + card.draw
        if incoming > env.player_block and card.block:
            score += 6
        if card.damage >= env.enemy_hp + env.enemy_block:
            score += 100
        if score > best_score:
            best_score = score
            best_action = i
    return best_action


def run_rule_episode(env: SlS2CombatEnv, render: bool = False) -> dict:
    obs, info = env.reset()
    total_reward = 0.0
    terminated = truncated = False
    while not (terminated or truncated):
        if render:
            env.render()
        action = choose_rule_action(env)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
    return {"win": info["enemy_hp"] <= 0, "reward": total_reward, **info}

