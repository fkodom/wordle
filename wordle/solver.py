from __future__ import annotations

import regex
import sys
from dataclasses import dataclass
from functools import lru_cache
from math import perm, prod
from typing import Counter, Dict, List, Sequence, Tuple

from wordle.data import load_words
from wordle.game import LetterEvaluation, WordleStepInfo


@dataclass
class WordRecommendations:
    recommended: str
    alternatives: Sequence[str]

    def __str__(self) -> str:
        return (
            f"Recommended: {self.recommended}\n"
            f"Alternatives: [" + ", ".join(self.alternatives) + "]"
        )


def _recommend_by_chain_prob(
    words: Sequence[str], max_alternatives: int = 5,
) -> WordRecommendations:
    ginis = {w: _word_prob(w, words) for w in words}
    ranked = sorted(words, key=lambda w: -ginis[w])
    return WordRecommendations(
        recommended=ranked[0], alternatives=ranked[1 : max_alternatives + 1]
    )


@lru_cache(maxsize=256)
def _character_prob(char: str, options: str) -> float:
    same = [char == o for o in options]
    return sum(same) / len(same)


def _word_prob(word: str, options: Sequence[str]) -> float:
    counts = Counter(word)
    ordered_options = zip(*options)
    all_options = "".join(options)

    positional_probs = [_character_prob(c, o) for c, o in zip(word, ordered_options)]
    overall_probs = [_character_prob(c, all_options) for c in word]
    permutations = [perm(counts[c]) for c in word]

    return prod(
        pp * op / ps ** 2
        for pp, op, ps in zip(positional_probs, overall_probs, permutations)
    )


class Solver:
    def __init__(self, mode: str = "chain"):
        self.mode = mode
        self.words = load_words()

    def recommend(self) -> WordRecommendations:
        if len(self.words) == len(load_words()):
            return WordRecommendations(
                recommended="clasp",
                alternatives=["scalp", "shalt", "spilt", "least", "slate", "ralph"],
            )

        if self.mode == "chain":
            return _recommend_by_chain_prob(self.words)
        else:
            raise ValueError(f"Solver mode '{self.mode}' is not supported.")

    def update(self, step_info: WordleStepInfo) -> str:
        self.words = _filter_words_from_step_info(self.words, step_info)
        return self.recommend().recommended


@lru_cache(maxsize=4096)
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


def _filter_words_from_step_info(
    words: Sequence[str], info: WordleStepInfo
) -> List[str]:
    limits = _get_character_limits_from_step_info(info)

    exclude_chars = [char for char, (_, upper) in limits.items() if upper == 0]
    exclude_phrase = "|".join(exclude_chars)
    regex_terms = [
        x.text if x.in_correct_position else f"[^({x.text}|{exclude_phrase})]"
        for x in info.letters
    ]
    regex_phrase = regex.compile("".join(regex_terms))
    words = [w for w in words if regex_phrase.match(w)]

    out = []
    for word in words:
        counts = Counter(word)
        if all(lower <= counts[k] <= upper for k, (lower, upper) in limits.items()):
            out.append(word)

    return out


class AssistiveSolver(Solver):
    def __init__(self):
        super().__init__()
        self.step = 1
        self.done = False

    def _get_input(self, prompt: str) -> str:
        return input(prompt).lower().strip().replace(" ", "").replace(",", "")

    def _get_step_info(self) -> WordleStepInfo:
        guess = self._get_input("Enter your guess: ")
        colors = self._get_input(
            "What color was each square?\n" "(b=black/gray, y=yellow, g=green): "
        )
        # in_correct_position = self._get_input("Which letters were correct (green)? ")
        success = all(color == "g" for color in colors)

        self.done = success
        letters = [
            LetterEvaluation(
                text=letter,
                in_word=(color in {"y", "g"}),
                in_correct_position=(color == "g"),
            )
            for letter, color in zip(guess, colors)
        ]

        return WordleStepInfo(
            step=self.step, success=success, done=self.done, letters=letters
        )

    def solve(self):
        print("Wordle Solver!")
        while not self.done:
            print(f"\nStep {self.step}")
            print("-" * 16)
            print(f"{len(self.words)} solutions remaining")
            recommendations = self.recommend()
            print(recommendations)
            print("-" * 16)
            info = self._get_step_info()
            self.update(info)
            self.step += 1

            if info.success:
                print("You win! :)")


def main():
    AssistiveSolver().solve()


if __name__ == "__main__":
    main()
