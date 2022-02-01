from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import List, Tuple

from tqdm import tqdm

from wordle.data import load_word_frequencies
from wordle.game import Wordle
from wordle.solver import Solver


def solve_game(word: str, first_guess: str) -> Tuple[bool, int]:
    game = Wordle(word_bank_size=1500, silent=True)
    game._word = word
    solver = Solver()
    info = game.step(first_guess)

    while not game.done:
        guess = solver.update(info)
        info = game.step(guess)

    return (game._success, game._step)


def test_solver_with_first_guess(
    first_guess: str, max_words: int = 1500,
) -> Tuple[float, float]:
    words = load_word_frequencies(max_words=max_words)
    solve_fn = partial(solve_game, first_guess=first_guess)

    pool = ProcessPoolExecutor(max_workers=4)
    results = list(pool.map(solve_fn, words))

    wins = sum(r[0] for r in results)
    win_percentage = wins / len(results)
    avg_turns_to_win = sum(r[1] for r in results if r[0]) / wins

    return win_percentage, avg_turns_to_win


def test_first_guesses(max_words: int = 128) -> List[Tuple[str, float, float]]:
    words = list(load_word_frequencies(max_words=max_words).keys())
    results = [test_solver_with_first_guess(word) for word in tqdm(words)]
    return [(word, *result) for word, result in zip(words, results)]


if __name__ == "__main__":
    print(test_solver_with_first_guess("table"))
    # results = test_first_guesses(512)
    # for result in results:
    #     print(result)
