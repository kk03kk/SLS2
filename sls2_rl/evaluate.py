from __future__ import annotations

import argparse

from .baseline import run_rule_episode
from .combat_env import CombatConfig, SlS2CombatEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained combat policy or rule baseline.")
    parser.add_argument("--model", default="")
    parser.add_argument("--algo", choices=["ppo", "maskableppo"], default="maskableppo")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--pool", choices=["weak", "strong", "elite", "boss"], default="weak")
    parser.add_argument("--enemy", default="")
    parser.add_argument("--extra-min", type=int, default=0)
    parser.add_argument("--extra-max", type=int, default=0)
    parser.add_argument("--render", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env = SlS2CombatEnv(CombatConfig(encounter_pool=args.pool, enemy_id=args.enemy or None, random_extra_cards=(args.extra_min, args.extra_max)))
    wins = 0
    rewards = []
    if not args.model:
        for _ in range(args.episodes):
            result = run_rule_episode(env, args.render)
            wins += int(result["win"])
            rewards.append(result["reward"])
    else:
        if args.algo == "maskableppo":
            from sb3_contrib import MaskablePPO

            model = MaskablePPO.load(args.model, env=env)
        else:
            from stable_baselines3 import PPO

            model = PPO.load(args.model, env=env)
        for _ in range(args.episodes):
            obs, info = env.reset()
            done = False
            total_reward = 0.0
            while not done:
                kwargs = {}
                if args.algo == "maskableppo":
                    kwargs["action_masks"] = info["action_mask"]
                action, _ = model.predict(obs, deterministic=True, **kwargs)
                obs, reward, terminated, truncated, info = env.step(int(action))
                total_reward += reward
                done = terminated or truncated
                if args.render:
                    env.render()
            wins += int(info["enemy_hp"] <= 0)
            rewards.append(total_reward)
    print(f"episodes={args.episodes} win_rate={wins / args.episodes:.3f} avg_reward={sum(rewards) / len(rewards):.3f}")


if __name__ == "__main__":
    main()

