from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sts2_sim.engine import END_TURN, Action, CombatEnv


ActionKey = str
StateKey = str
QTable = dict[StateKey, dict[ActionKey, float]]


def _bucket(value: int, size: int) -> int:
    return max(0, value) // size


def state_key(env: CombatEnv) -> StateKey:
    hand_counts: dict[str, int] = {}
    for card_instance in env.hand:
        hand_counts[card_instance.def_id] = hand_counts.get(card_instance.def_id, 0) + 1
    hand_part = ",".join(f"{card_id}:{count}" for card_id, count in sorted(hand_counts.items()))

    enemies = []
    for enemy in env.enemies:
        if not enemy.alive:
            enemies.append("dead")
            continue
        move = env.current_enemy_move(enemy)
        creature = enemy.creature
        enemies.append(
            ":".join(
                [
                    enemy.definition.id,
                    str(_bucket(creature.hp, 3)),
                    str(_bucket(creature.block, 3)),
                    str(creature.power_amount("vulnerable")),
                    str(creature.power_amount("weak")),
                    move.id,
                ]
            )
        )

    player = env.player
    return "|".join(
        [
            f"t{min(env.turn, 10)}",
            f"b{_bucket(player.block, 3)}",
            f"e{env.energy}",
            f"str{player.power_amount('strength')}",
            f"vul{player.power_amount('vulnerable')}",
            f"weak{player.power_amount('weak')}",
            f"h[{hand_part}]",
            f"d{_bucket(len(env.draw_pile), 5)}",
            f"p{_bucket(len(env.discard_pile), 5)}",
            "en[" + ";".join(enemies) + "]",
        ]
    )


def action_key(env: CombatEnv, action: Action) -> ActionKey:
    if action == END_TURN:
        return "END"
    hand_index = action[0]
    target_index = action[1]
    choice_index = action[2] if len(action) > 2 else None
    card_id = env.hand[hand_index].def_id
    card = env.card_def(card_id)
    choice_part = f":choice{choice_index}" if choice_index is not None else ""
    if card.target == "enemy":
        return f"PLAY:{card_id}:enemy{choice_part}"
    return f"PLAY:{card_id}:none{choice_part}"


def legal_action_keys(env: CombatEnv) -> list[ActionKey]:
    keys = {action_key(env, action) for action in env.legal_actions()}
    return sorted(keys)


def action_from_key(env: CombatEnv, key: ActionKey) -> Action:
    if key == "END":
        return END_TURN

    try:
        _, card_id, target_mode = key.split(":", 2)
    except ValueError:
        return END_TURN
    choice_index = None
    if ":choice" in target_mode:
        target_mode, choice_text = target_mode.split(":choice", 1)
        try:
            choice_index = int(choice_text)
        except ValueError:
            choice_index = None

    matching_actions = [
        action for action in env.legal_actions()
        if action != END_TURN and env.hand[action[0]].def_id == card_id
        and (choice_index is None or (len(action) > 2 and action[2] == choice_index))
    ]
    if not matching_actions:
        return END_TURN

    if target_mode == "enemy":
        enemy_actions = [action for action in matching_actions if action[1] is not None]
        if enemy_actions:
            return min(enemy_actions, key=lambda action: env.enemies[action[1]].creature.hp)
    return matching_actions[0]


def greedy_action_key(q_table: QTable, env: CombatEnv, rng: random.Random | None = None) -> ActionKey:
    rng = rng or random
    state = state_key(env)
    legal = legal_action_keys(env)
    values = q_table.get(state, {})
    best_value = max(values.get(key, 0.0) for key in legal)
    best = [key for key in legal if values.get(key, 0.0) == best_value]
    return rng.choice(best)


class QAgent:
    def __init__(self, q_table: QTable, seed: int | None = None) -> None:
        self.q_table = q_table
        self.rng = random.Random(seed)

    def choose_action(self, env: CombatEnv) -> tuple[int, int | None]:
        return action_from_key(env, greedy_action_key(self.q_table, env, self.rng))


@dataclass(frozen=True)
class TrainStats:
    episodes: int
    eval_runs: int
    win_rate: float
    avg_hp_lost: float
    avg_turns: float
    states: int
    actions: int


def select_epsilon_greedy(
    q_table: QTable,
    env: CombatEnv,
    rng: random.Random,
    epsilon: float,
) -> ActionKey:
    legal = legal_action_keys(env)
    if rng.random() < epsilon:
        return rng.choice(legal)
    return greedy_action_key(q_table, env, rng)


def shaped_reward(env_before: dict[str, Any], env: CombatEnv, done: bool) -> float:
    before_player_hp = int(env_before["player_hp"])
    before_enemy_hp = int(env_before["enemy_hp"])
    after_player_hp = env.player.hp
    after_enemy_hp = sum(enemy.creature.hp for enemy in env.enemies if enemy.alive)

    damage_dealt = max(0, before_enemy_hp - after_enemy_hp)
    hp_lost = max(0, before_player_hp - after_player_hp)
    reward = damage_dealt * 0.05 - hp_lost * 2.0 - 0.02

    if done:
        if env.player.hp > 0 and all(not enemy.alive for enemy in env.enemies):
            reward += 20.0 + env.player.hp * 0.35
        else:
            reward -= 30.0
    return reward


def train_q_learning(
    deck: list[str],
    enemies: list,
    *,
    episodes: int = 5000,
    seed: int = 1,
    alpha: float = 0.25,
    gamma: float = 0.95,
    epsilon_start: float = 0.35,
    epsilon_end: float = 0.03,
    max_turns: int = 30,
) -> QTable:
    rng = random.Random(seed)
    q_table: QTable = {}

    for episode in range(episodes):
        progress = episode / max(1, episodes - 1)
        epsilon = epsilon_start + (epsilon_end - epsilon_start) * progress
        env = CombatEnv(deck, enemies, seed=seed + episode, max_turns=max_turns)
        done = False

        while not done:
            state = state_key(env)
            legal = legal_action_keys(env)
            q_table.setdefault(state, {key: 0.0 for key in legal})
            for key in legal:
                q_table[state].setdefault(key, 0.0)

            selected_key = select_epsilon_greedy(q_table, env, rng, epsilon)
            action = action_from_key(env, selected_key)
            before = {
                "player_hp": env.player.hp,
                "enemy_hp": sum(enemy.creature.hp for enemy in env.enemies if enemy.alive),
            }
            _, _, done, _ = env.step(action)
            reward = shaped_reward(before, env, done)

            next_state = state_key(env)
            next_legal = legal_action_keys(env) if not done else []
            next_best = 0.0
            if next_legal:
                q_table.setdefault(next_state, {key: 0.0 for key in next_legal})
                for key in next_legal:
                    q_table[next_state].setdefault(key, 0.0)
                next_best = max(q_table[next_state].get(key, 0.0) for key in next_legal)

            old_value = q_table[state][selected_key]
            target = reward + gamma * next_best
            q_table[state][selected_key] = old_value + alpha * (target - old_value)

    return q_table


def evaluate_q_agent(
    q_table: QTable,
    deck: list[str],
    enemies: list,
    *,
    runs: int = 200,
    seed: int = 100_000,
    max_turns: int = 30,
) -> TrainStats:
    wins = 0
    hp_lost: list[int] = []
    turns: list[int] = []
    for offset in range(runs):
        env = CombatEnv(deck, enemies, seed=seed + offset, max_turns=max_turns)
        agent = QAgent(q_table, seed=seed + offset)
        done = False
        while not done:
            _, _, done, info = env.step(agent.choose_action(env))
        result = info["result"]
        wins += int(result.won)
        hp_lost.append(result.hp_lost)
        turns.append(result.turns)

    action_count = sum(len(actions) for actions in q_table.values())
    return TrainStats(
        episodes=0,
        eval_runs=runs,
        win_rate=wins / runs,
        avg_hp_lost=sum(hp_lost) / max(1, len(hp_lost)),
        avg_turns=sum(turns) / max(1, len(turns)),
        states=len(q_table),
        actions=action_count,
    )


def save_q_table(path: str | Path, q_table: QTable, metadata: dict[str, Any]) -> None:
    payload = {
        "metadata": metadata,
        "q_table": q_table,
    }
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_q_table(path: str | Path) -> tuple[QTable, dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload["q_table"], payload.get("metadata", {})
