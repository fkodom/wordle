from __future__ import annotations
from copy import deepcopy

import argparse
from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import perm, prod
from typing import Dict, List, Optional, Sequence, Tuple, Union

from wordle.data import load_all_words, load_words
from wordle.game import LetterEvaluation, WordleStepInfo, _evaluate_guess


@dataclass
class WordRecommendations:
    recommended: Optional[str]
    alternatives: Sequence[str] = ()

    def __str__(self) -> str:
        return (
            f"Recommended: {self.recommended}\n"
            f"Alternatives: [" + ", ".join(self.alternatives) + "]"
        )


@lru_cache(maxsize=2048)
def _cached_counter(word: str) -> Dict[str, int]:
    return Counter(word)


@lru_cache(maxsize=2048)
def _rank_by_chain_prob(words: Tuple[str, ...]) -> Tuple[str, ...]:
    word_set = set(words)
    probs = {w: _word_prob(w, words) for w in word_set}
    return tuple(w for w in sorted(word_set, key=lambda w: -probs[w]))


def _character_prob(char: str, options: Union[str, Tuple[str, ...]]) -> float:
    counts = _cached_counter(options)
    return counts[char] / len(options)


def _word_prob(word: str, options: Tuple[str, ...]) -> float:
    counts = _cached_counter(word)
    ordered_options = zip(*options)
    all_options = "".join(options)

    positional_probs = [_character_prob(c, o) for c, o in zip(word, ordered_options)]
    overall_probs = [_character_prob(c, all_options) for c in word]
    permutations = [perm(counts[c]) for c in word]

    return prod(
        pp * op / ps**2
        for pp, op, ps in zip(positional_probs, overall_probs, permutations)
    )


@lru_cache(maxsize=2048)
def _rank_by_average_split(words: Tuple[str, ...]) -> Tuple[str, ...]:
    avg_words = {w: _avg_words_after_guess(w, words) for w in words}
    return tuple(w for w in sorted(words, key=lambda w: avg_words[w]))


@lru_cache(maxsize=2048)
def _rank_by_maximum_split(words: Tuple[str, ...]) -> Tuple[str, ...]:
    avg_words = {w: _max_words_after_guess(w, words) for w in words}
    return tuple(w for w in sorted(words, key=lambda w: avg_words[w]))


@lru_cache(maxsize=65536)
def _eval_pattern(guess: str, truth: str) -> int:
    """Compact evaluation pattern as a base-3 integer in [0, 243)."""
    remaining: dict = {}
    for c in truth:
        remaining[c] = remaining.get(c, 0) + 1

    result = [0, 0, 0, 0, 0]
    for i in range(5):
        if guess[i] == truth[i]:
            result[i] = 2
            remaining[guess[i]] -= 1

    for i in range(5):
        if result[i] == 0 and remaining.get(guess[i], 0) > 0:
            result[i] = 1
            remaining[guess[i]] -= 1

    return result[0] * 81 + result[1] * 27 + result[2] * 9 + result[3] * 3 + result[4]


def _partition_buckets(guess: str, words: Tuple[str, ...]) -> Dict[int, int]:
    """Count words in each evaluation-pattern bucket for a given guess."""
    buckets: Dict[int, int] = {}
    for word in words:
        p = _eval_pattern(guess, word)
        buckets[p] = buckets.get(p, 0) + 1
    return buckets


def _avg_words_after_guess(guess: str, words: Tuple[str, ...]) -> float:
    buckets = _partition_buckets(guess, words)
    return sum(c * c for c in buckets.values()) / len(words)


def _max_words_after_guess(guess: str, words: Tuple[str, ...]) -> float:
    buckets = _partition_buckets(guess, words)
    return max(buckets.values())


@lru_cache(maxsize=2048)
def _rank_by_exhaustive_search(words: Tuple[str, ...]) -> Tuple[str, ...]:
    turns = {w: _avg_turns_to_win(w, words) for w in words}
    return tuple(w for w in sorted(words, key=lambda w: turns[w]))


def _num_turns_to_win(truth: str, guess: Optional[str], words: Tuple[str, ...]) -> int:
    solver = WordleSolver(mode="exhaustive")
    solver.words = words
    step = 1

    while guess != truth:
        assert guess is not None
        success, letters = _evaluate_guess(guess, truth)
        info = WordleStepInfo(step=step, success=success, done=success, letters=letters)
        solver.update(info)
        guess = solver.recommend().recommended
        step += 1

    return step


def _avg_turns_to_win(guess: str, words: Tuple[str, ...]) -> float:
    return max(_num_turns_to_win(w, guess, words) for w in words)


def _rank_by_turns_to_win(words: Tuple[str, ...]) -> Tuple[str, ...]:
    if len(words) > 128:
        return _rank_by_chain_prob(words)
    else:
        return _rank_by_average_split(words)


def _rank_by_win_percentage(words: Tuple[str, ...]) -> Tuple[str, ...]:
    if len(words) > 128:
        return _rank_by_chain_prob(words)
    elif len(words) > 32:
        return _rank_by_average_split(words)
    else:
        return _rank_by_exhaustive_search(words)


class WordleSolver:
    def __init__(self, mode: str = "turns-to-win"):
        self.mode = mode
        self.words = load_words()
        primary_set = set(self.words)
        self.fallback_words = tuple(w for w in load_all_words() if w not in primary_set)

    def recommend(self, max_alternatives: int = 5) -> WordRecommendations:
        if len(self.words) == len(load_words()):
            if self.mode == "win-percentage":
                return WordRecommendations(
                    recommended="ralph",
                    alternatives=["blast", "plush"],
                )
            else:
                return WordRecommendations(
                    recommended="slate",
                    alternatives=["blast", "tapir", "ralph"],
                )

        words = self.words if self.words else self.fallback_words

        if self.mode == "win-percentage":
            words = _rank_by_win_percentage(words)
        elif self.mode == "turns-to-win":
            words = _rank_by_turns_to_win(words)
        elif self.mode == "probability":
            words = _rank_by_chain_prob(words)
        elif self.mode == "avg-split":
            words = _rank_by_average_split(words)
        elif self.mode == "max-split":
            words = _rank_by_maximum_split(words)
        elif self.mode == "exhaustive":
            words = _rank_by_exhaustive_search(words)
        else:
            raise ValueError(f"Solver mode '{self.mode}' is not supported.")

        if self.words:
            self.words = words
        else:
            self.fallback_words = words

        if len(words) > 0:
            return WordRecommendations(
                recommended=words[0],
                alternatives=words[1 : max_alternatives + 1],
            )
        else:
            return WordRecommendations(recommended=None, alternatives=())

    def update(self, step_info: WordleStepInfo) -> Optional[str]:
        self.words = _filter_words_from_step_info(self.words, step_info)
        self.fallback_words = _filter_words_from_step_info(
            self.fallback_words, step_info
        )
        return self.recommend().recommended


class MultiWordleSolver:
    def __init__(self, num_words: int, mode: str = "probability"):
        self.num_words = num_words
        self.mode = mode
        self.solvers = [WordleSolver(mode=mode) for _ in range(num_words)]
        self._step = 1

    def recommend(self, max_alternatives: int = 5) -> WordRecommendations:
        if self._step == 1:
            return WordRecommendations(
                recommended="slate",
                alternatives=["blast", "tapir", "ralph"],
            )

        words: Tuple[str, ...] = sum(
            (solver.words for solver in self.solvers), start=tuple()
        )
        if self.mode == "probability":
            words = _rank_by_chain_prob(words)
        else:
            raise ValueError(f"Solver mode '{self.mode}' is not supported.")

        for solver in self.solvers:
            if len(solver.words) == 1:
                word = solver.words[0]
                words = (word,) + tuple(w for w in words if w != word)

        return WordRecommendations(
            recommended=words[0], alternatives=words[1 : max_alternatives + 1]
        )

    def update(self, step_info: Sequence[Optional[WordleStepInfo]]) -> Optional[str]:
        self._step += 1
        for solver, info in zip(self.solvers, step_info):
            if info is not None:
                solver.update(info)
        return self.recommend().recommended


class QuordleSolver(MultiWordleSolver):
    def __init__(self, mode: str = "probability"):
        super().__init__(num_words=4, mode=mode)


@lru_cache(maxsize=1024)
def _filter_words_from_step_info(
    words: Tuple[str, ...], info: WordleStepInfo
) -> Tuple[str, ...]:
    word_len = len(info.letters)

    # Group evaluations by character to compute count constraints
    char_in_word_count: Dict[str, int] = {}
    char_has_miss: Dict[str, bool] = {}
    for letter in info.letters:
        c = letter.text
        if c not in char_in_word_count:
            char_in_word_count[c] = 0
            char_has_miss[c] = False
        if letter.in_word:
            char_in_word_count[c] += 1
        else:
            char_has_miss[c] = True

    # Build count constraints and set of fully absent characters
    absent: set = set()
    count_checks: list = []
    for c, lo in char_in_word_count.items():
        if char_has_miss[c]:
            hi = lo
        else:
            hi = word_len
        if hi == 0:
            absent.add(c)
        else:
            count_checks.append((c, lo, hi))

    # Build positional constraints
    exact = [None] * word_len
    exclude_at = [absent.copy() for _ in range(word_len)]
    for i, letter in enumerate(info.letters):
        if letter.in_correct_position:
            exact[i] = letter.text
        else:
            exclude_at[i].add(letter.text)

    # Single-pass filter with early exit per word
    out = []
    for word in words:
        # Positional checks
        valid = True
        for i in range(word_len):
            c = word[i]
            if exact[i] is not None:
                if c != exact[i]:
                    valid = False
                    break
            elif c in exclude_at[i]:
                valid = False
                break
        if not valid:
            continue

        # Character count checks
        for c, lo, hi in count_checks:
            cnt = word.count(c)
            if cnt < lo or cnt > hi:
                valid = False
                break
        if valid:
            out.append(word)

    return tuple(out)


def _get_input(prompt: str) -> str:
    return input(prompt).lower().strip().replace(" ", "").replace(",", "")


def _get_valid_word_input(prompt: str) -> str:
    word = _get_input(prompt)
    if word in set(load_all_words()):
        return word
    else:
        print("Not a valid 'Wordle' word! Try again.")
        return _get_valid_word_input(prompt)


def _get_wordle_step_info(step: int, guess: Optional[str] = None) -> WordleStepInfo:
    if guess is None:
        guess = _get_valid_word_input("Enter your guess: ")

    colors = _get_input(
        "What color was each square?\n(b=black/gray, y=yellow, g=green): "
    )
    success = all(color == "g" for color in colors)
    letters = tuple(
        LetterEvaluation(
            text=letter,
            in_word=(color in {"y", "g"}),
            in_correct_position=(color == "g"),
        )
        for letter, color in zip(guess, colors)
    )

    return WordleStepInfo(step=step, success=success, done=success, letters=letters)


class AssistiveWordleSolver(WordleSolver):
    def __init__(self, mode: str = "turns-to-win"):
        super().__init__(mode=mode)
        self.step = 1
        self.done = False

    def get_step_info(self, guess: Optional[str] = None) -> WordleStepInfo:
        info = _get_wordle_step_info(self.step, guess=guess)
        self.done = info.done
        return info

    def solve(self):
        print("Wordle Solver!")
        while not self.done:
            print(f"\nStep {self.step}")
            print("-" * 16)
            remaining = self.words if self.words else self.fallback_words
            print(f"{len(remaining)} solutions remaining")
            recommendations = self.recommend()
            print(recommendations)
            print("-" * 16)
            info = self.get_step_info()
            self.update(info)
            self.step += 1

            if info.success:
                print("You win! :)")


class AssistiveMultiWordleSolver(MultiWordleSolver):
    def __init__(self, num_words: int, mode: str = "probability"):
        super().__init__(num_words=num_words, mode=mode)
        self.step = 1
        self.dones = [False] * num_words

    @property
    def done(self):
        return all(done for done in self.dones)

    def get_step_info(
        self, guess: Optional[str] = None
    ) -> List[Optional[WordleStepInfo]]:
        guess = _get_valid_word_input("Enter your guess: ")
        step_info: List[Optional[WordleStepInfo]] = []
        for i, (solver, done) in enumerate(zip(self.solvers, self.dones), 1):
            if not done:
                print(f"Word {i} of {self.num_words}: ")
                info = _get_wordle_step_info(step=self.step, guess=guess)
                step_info.append(info)
                self.dones[i - 1] = info.done
                if info.done:
                    solver.words = tuple()
            else:
                step_info.append(None)

        return step_info

    def solve(self):
        print("MultiWordle Solver!")
        while not self.done:
            print(f"\nStep {self.step}")
            print("-" * 16)
            for i, (solver, done) in enumerate(zip(self.solvers, self.dones), 1):
                print(f"Solver {i} of {self.num_words}: ", end="")
                if done:
                    print("DONE")
                else:
                    print(f"{len(solver.words)} solutions remaining")
            recommendations = self.recommend()
            print(recommendations)
            print("-" * 16)
            step_info = self.get_step_info()
            self.update(step_info)
            self.step += 1

            successes = [getattr(info, "success", True) for info in step_info]
            if all(successes):
                print("You win! :)")


class AssistiveDordleSolver(AssistiveMultiWordleSolver):
    def __init__(self, mode: str = "probability"):
        super().__init__(num_words=2, mode=mode)


class AssistiveQuordleSolver(AssistiveMultiWordleSolver):
    def __init__(self, mode: str = "probability"):
        super().__init__(num_words=4, mode=mode)


class AssistiveOctordleSolver(AssistiveMultiWordleSolver):
    def __init__(self, mode: str = "probability"):
        super().__init__(num_words=8, mode=mode)


def main_wordle():
    parser = ArgumentParser()
    parser.add_argument("--mode", type=str, default="turns-to-win")
    args = parser.parse_args()

    AssistiveWordleSolver(mode=args.mode).solve()


def main_multi_wordle():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-words", type=int, required=True)
    args = parser.parse_args()

    AssistiveMultiWordleSolver(num_words=args.num_words).solve()


def main_dordle():
    AssistiveDordleSolver().solve()


def main_quordle():
    AssistiveQuordleSolver().solve()


def main_octordle():
    AssistiveOctordleSolver().solve()


if __name__ == "__main__":
    main_wordle()
