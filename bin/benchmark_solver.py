from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import List, Tuple

from tqdm import tqdm

from wordle.data import load_word_frequencies
from wordle.game import Wordle
from wordle.solver import Solver


def solve_game(word: str, first_guess: str) -> Tuple[bool, int]:
    game = Wordle(silent=True)
    game._word = word
    solver = Solver()
    info = game.step(first_guess)

    while not game._done:
        guess = solver.update(info)
        info = game.step(guess)

    return (game._success, game._step)


def test_solver_with_first_guess(
    first_guess: str, max_words: int = 1500,
) -> Tuple[float, float]:
    words = load_word_frequencies(max_words=max_words)
    solve_fn = partial(solve_game, first_guess=first_guess)

    pool = ProcessPoolExecutor()
    results = list(pool.map(solve_fn, words))

    wins = sum(r[0] for r in results)
    win_percentage = wins / len(results)
    avg_turns_to_win = sum(r[1] for r in results if r[0]) / wins

    return win_percentage, avg_turns_to_win


def test_first_guesses(max_words: int = 128) -> List[Tuple[str, float, float]]:
    words = list(load_word_frequencies(max_words=max_words).keys())[96:]
    results = [test_solver_with_first_guess(word) for word in tqdm(words)]
    return [(word, *result) for word, result in zip(words, results)]


if __name__ == "__main__":
    results = test_first_guesses(128)
    for result in results:
        print(result)
