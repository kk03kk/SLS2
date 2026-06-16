from __future__ import annotations

import argparse

import numpy as np

from sts2_sim.route_env import UnderdocksRoutePPOEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test the Underdocks route environment.")
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--random", action="store_true")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    for offset in range(args.episodes):
        env = UnderdocksRoutePPOEnv(seed=args.seed + offset)
        obs, _ = env.reset()
        done = False
        info = {}
        steps = 0
        while not done and steps < 1000:
            legal = np.flatnonzero(env.action_masks())
            action = int(rng.choice(legal)) if args.random else int(legal[0])
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            steps += 1
        result = info.get("result")
        print(
            f"seed={args.seed + offset} phase={env.phase} steps={steps} "
            f"won={result.won if result else None} final_hp={result.final_hp if result else None} "
            f"combats={result.combats_won if result else None}/7"
        )


if __name__ == "__main__":
    main()
