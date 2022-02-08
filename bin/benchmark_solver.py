import os
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Dict, Iterator, Optional, Tuple

from tqdm import tqdm

from wordle.data import load_words
from wordle.game import Wordle
from wordle.solver import Solver

BENCHMARKS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "benchmarks.jsonl"
)


def solve_game(
    word: str, first_guess: str, mode: str = "turns-to-win"
) -> Tuple[bool, int]:
    game = Wordle(silent=True)
    game._word = word
    solver = Solver(mode=mode)
    guess = first_guess

    while guess != game._word and not game.done:
        info = game.step(guess)
        guess = solver.update(info)

    return (guess == game._word, game._step)


def test_solver_with_first_guess(first_guess: str, mode: str = "turns-to-win") -> Dict:
    words = load_words()
    results = [solve_game(w, first_guess, mode=mode) for w in words]

    return {
        "first_guess": first_guess,
        "win_percentage": sum(r[0] for r in results) / len(results),
        "average_turns": sum(r[1] for r in results) / len(results),
        "max_turns": max(r[1] for r in results),
    }


def test_first_guesses(
    mode: str = "hybrid",
    start_idx: int = 0,
    num_workers: Optional[int] = None,
) -> Iterator[Dict]:
    words = sorted(load_words())[start_idx:]
    map_fn = partial(test_solver_with_first_guess, mode=mode)
    if num_workers is None or num_workers > 1:
        pool = ProcessPoolExecutor(max_workers=num_workers)
        results = pool.map(map_fn, words)
    else:
        results = map(map_fn, words)

    return (r for r in tqdm(results, total=len(words)))


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="turns-to-win")
    parser.add_argument("--first-guess", type=str, default=None)
    parser.add_argument("--start-idx", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--num-workers", type=int, default=None)
    args = parser.parse_args()

    if args.first_guess is not None:
        result = test_solver_with_first_guess(args.first_guess, mode=args.mode)
        print(json.dumps(result, indent=2))
    else:
        results = test_first_guesses(
            mode=args.mode, start_idx=args.start_idx, num_workers=args.num_workers
        )
        os.makedirs(os.path.dirname(BENCHMARKS_PATH), exist_ok=True)
        mode = "w" if args.overwrite else "a"

        with open(BENCHMARKS_PATH, mode) as f:
            for i, result in enumerate(results):
                line = json.dumps(result)
                f.write(f"{line}\n")
