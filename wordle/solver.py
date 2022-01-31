from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import regex

from wordle.data import load_word_frequencies
from wordle.game import LetterEvaluation, WordleStepInfo


class Solver:
    def __init__(self, word_bank_size: Optional[int] = 7500):
        self.word_bank_size = word_bank_size
        self.frequencies = load_word_frequencies(max_words=word_bank_size)
        self.history: List[WordleStepInfo] = []

    def update(self, step_info: WordleStepInfo) -> str:
        self.history.append(step_info)
        self.frequencies = _filter_frequencies_from_step_info(
            self.frequencies, step_info
        )
        out = _get_most_common_word(self.frequencies)
        return out


def _filter_frequencies_from_step_info(
    frequencies: Dict[str, int], info: WordleStepInfo
) -> Dict[str, int]:
    letters = info.letters
    exclude = [x.text for x in letters if not x.in_word]
    include = [x.text for x in letters if x.in_word]
    regex_terms = [x.text if x.in_correct_position else f"[^{x.text}]" for x in letters]
    regex_phrase = regex.compile("".join(regex_terms))

    return {
        w: f
        for w, f in frequencies.items()
        if all(x in w for x in include)
        and not any(x in w for x in exclude)
        and regex_phrase.match(w)
    }


def _get_most_common_word(frequencies: Dict[str, int]) -> str:
    return max(frequencies.keys(), key=lambda w: frequencies[w])


@dataclass
class WordRecommendations:
    recommended: str
    alternatives: Sequence[str]

    def __str__(self) -> str:
        return (
            f"Recommended: {self.recommended}\n"
            f"Alternatives: [" + ", ".join(self.alternatives) + "]"
        )


class AssistiveSolver(Solver):
    def __init__(self, word_bank_size: Optional[int] = 7500):
        super().__init__(word_bank_size)
        self.step = 1
        self.done = False

    def recommend(self, max_alternatives: int = 5) -> WordRecommendations:
        if len(self.frequencies) == self.word_bank_size:
            return WordRecommendations(
                recommended="table", alternatives=["rates", "least"],
            )

        # TODO: This can be inefficient when the number of remaining words is large.
        # Consider filtering the words by frequency first, and sort only the remaining
        # words (if necessary).
        top_remaining = sorted(
            list(self.frequencies.keys()), key=(lambda word: -self.frequencies[word])
        )[: max_alternatives + 1]
        return WordRecommendations(
            recommended=top_remaining[0], alternatives=top_remaining[1:]
        )

    def _get_input(self, prompt: str) -> str:
        return input(prompt).lower().strip().replace(" ", "").replace(",", "")

    def _get_step_info(self) -> WordleStepInfo:
        guess = self._get_input("Enter your guess: ")
        in_correct_position = self._get_input("Which letters were correct (green)? ")
        success = all(letter in in_correct_position for letter in guess)
        if not success:
            in_word = self._get_input(
                "Which letters were in the word, but in the wrong spot (yellow)? "
            )
        else:
            in_word = ""

        self.done = success
        letters = [
            LetterEvaluation(
                text=letter,
                in_word=(letter in in_word or letter in in_correct_position),
                in_correct_position=(letter in in_correct_position),
            )
            for letter in guess
        ]

        return WordleStepInfo(
            step=self.step, success=success, done=self.done, letters=letters
        )

    def solve(self):
        print("Wordle Solver!")
        while not self.done:
            print(f"\nStep {self.step}")
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
