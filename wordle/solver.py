from __future__ import annotations

import argparse
import re
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import lru_cache
from math import perm, prod
from typing import Counter, Dict, List, Optional, Sequence, Tuple, Union

from wordle.data import load_words
from wordle.game import LetterEvaluation, Wordle, WordleStepInfo


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


def _num_words_after_guess(truth: str, guess: str, words: Tuple[str, ...]) -> int:
    wordle = Wordle(silent=True)
    wordle._word = truth
    step_info = wordle.step(guess)
    return len(_filter_words_from_step_info(words, step_info))


def _avg_words_after_guess(guess: str, words: Tuple[str, ...]) -> float:
    return sum(_num_words_after_guess(w, guess, words) for w in words) / len(words)


def _max_words_after_guess(guess: str, words: Tuple[str, ...]) -> float:
    return max(_num_words_after_guess(w, guess, words) for w in words)


@lru_cache(maxsize=2048)
def _rank_by_exhaustive_search(words: Tuple[str, ...]) -> Tuple[str, ...]:
    turns = {w: _avg_turns_to_win(w, words) for w in words}
    return tuple(w for w in sorted(words, key=lambda w: turns[w]))


def _num_turns_to_win(truth: str, guess: Optional[str], words: Tuple[str, ...]) -> int:
    wordle = Wordle(silent=True)
    wordle._word = truth
    solver = WordleSolver(mode="exhaustive")
    solver.words = words

    while guess != truth:
        assert guess is not None
        info = wordle.step(guess)
        solver.update(info)
        guess = solver.recommend().recommended

    return wordle._step


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
    elif len(words) > 16:
        return _rank_by_average_split(words)
    else:
        return _rank_by_exhaustive_search(words)


class WordleSolver:
    def __init__(self, mode: str = "turns-to-win"):
        self.mode = mode
        self.words = load_words()

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

        if self.mode == "win-percentage":
            self.words = _rank_by_win_percentage(self.words)
        elif self.mode == "turns-to-win":
            self.words = _rank_by_turns_to_win(self.words)
        elif self.mode == "probability":
            self.words = _rank_by_chain_prob(self.words)
        elif self.mode == "avg-split":
            self.words = _rank_by_average_split(self.words)
        elif self.mode == "max-split":
            self.words = _rank_by_maximum_split(self.words)
        elif self.mode == "exhaustive":
            self.words = _rank_by_exhaustive_search(self.words)
        else:
            raise ValueError(f"Solver mode '{self.mode}' is not supported.")

        if len(self.words) > 0:
            return WordRecommendations(
                recommended=self.words[0],
                alternatives=self.words[1 : max_alternatives + 1],
            )
        else:
            return WordRecommendations(recommended=None, alternatives=())

    def update(self, step_info: WordleStepInfo) -> Optional[str]:
        self.words = _filter_words_from_step_info(self.words, step_info)
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
        # if self.mode == "win-percentage":
        #     words = _rank_by_win_percentage(words)
        # elif self.mode == "turns-to-win":
        #     words = _rank_by_turns_to_win(self.words)
        if self.mode == "probability":
            words = _rank_by_chain_prob(words)
        # elif self.mode == "avg-split":
        #     words = _rank_by_average_split(self.words)
        # elif self.mode == "max-split":
        #     words = _rank_by_maximum_split(self.words)
        # elif self.mode == "exhaustive":
        #     words = _rank_by_exhaustive_search(self.words)
        else:
            raise ValueError(f"Solver mode '{self.mode}' is not supported.")

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


def _get_character_limits_from_step_info(
    info: WordleStepInfo,
) -> Dict[str, Tuple[int, int]]:
    unique_characters = set([x.text for x in info.letters])
    grouped = {c: [x for x in info.letters if x.text == c] for c in unique_characters}
    min_counts = {k: sum(x.in_word for x in v) for k, v in grouped.items()}
    max_counts = {
        k: (sys.maxsize if all(x.in_word for x in v) else min_counts[k])
        for k, v in grouped.items()
    }
    return {k: (min_counts[k], max_counts[k]) for k in unique_characters}


@lru_cache(maxsize=1024)
def _filter_words_from_step_info(
    words: Tuple[str, ...], info: WordleStepInfo
) -> Tuple[str, ...]:
    limits = _get_character_limits_from_step_info(info)

    exclude_phrase = "".join([c for c, (_, upper) in limits.items() if upper == 0])
    regex_terms = [
        x.text if x.in_correct_position else f"[^{x.text}{exclude_phrase}]"
        for x in info.letters
    ]
    regex_phrase = re.compile("".join(regex_terms))
    words = tuple(w for w in words if regex_phrase.match(w))

    out = []
    for word in words:
        counts = _cached_counter(word)
        if all(lower <= counts[k] <= upper for k, (lower, upper) in limits.items()):
            out.append(word)

    return tuple(out)


def _get_input(prompt: str) -> str:
    return input(prompt).lower().strip().replace(" ", "").replace(",", "")


def _get_valid_word_input(prompt: str) -> str:
    word = _get_input(prompt)
    if word in load_words():
        return word
    else:
        print("Not a valid 'Wordle' word! Try again.")
        return _get_valid_word_input(prompt)


def _get_wordle_step_info(step: int, guess: Optional[str] = None) -> WordleStepInfo:
    if guess is None:
        guess = _get_valid_word_input("Enter your guess: ")

    colors = _get_input(
        "What color was each square?\n" "(b=black/gray, y=yellow, g=green): "
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
            print(f"{len(self.words)} solutions remaining")
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
