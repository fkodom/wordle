import argparse
import random
import time
from dataclasses import dataclass
from typing import Counter, List, Optional, Tuple

from colorama import Fore

from wordle.data import load_words

WORD_LENGTH = 5
# STEPS_PER_GAME = 6
MARKDOWN_LETTER_TEMPLATE = """
<p style='color:{color};background-color:gray;font-size:24px;text-align:center'><b>{letter}</b></p>
"""


@dataclass
class LetterEvaluation:
    text: str = "_"
    in_word: bool = False
    in_correct_position: bool = False

    def __hash__(self) -> int:
        return hash(f"{self.text}{self.in_word}{self.in_correct_position}")

    @property
    def empty(self) -> bool:
        return self.text == "_"


EMPTY_LETTER = LetterEvaluation()


@dataclass
class WordleStepInfo:
    step: int
    letters: Tuple[LetterEvaluation, ...]
    success: bool = False
    done: bool = False

    def __hash__(self) -> int:
        return hash(self.letters)

    @property
    def guess(self) -> str:
        return "".join([letter.text for letter in self.letters])


EMPTY_STEP_INFO = WordleStepInfo(step=0, letters=(EMPTY_LETTER,) * 5)


def _evaluate_guess(
    guess: str, truth: str
) -> Tuple[bool, Tuple[LetterEvaluation, ...]]:
    truth_counts = Counter(truth)
    success = guess == truth
    letters: List[LetterEvaluation] = []

    for x, y in zip(guess, truth):
        if x == y:
            letters.append(
                LetterEvaluation(text=x, in_word=True, in_correct_position=True)
            )
            truth_counts[x] -= 1
        else:
            letters.append(LetterEvaluation(text=x))

    for x, letter in zip(guess, letters):
        if not letter.in_word and truth_counts[x] > 0:
            letter.in_word = True
            truth_counts[x] -= 1

    return success, tuple(letters)


class Wordle:
    def __init__(
        self, seed: Optional[int] = None, total_steps: int = 6, silent: bool = False
    ):
        word_bank = load_words()
        if seed is None:
            seed = int(time.time())
        random.seed(seed)
        self._word = random.choice(word_bank)
        self.total_steps = total_steps
        self.silent = silent

        self._step = 1
        self._success = False
        self.history: List[WordleStepInfo] = []

    def _print_step_info(self, info: WordleStepInfo):
        for letter in info.letters:
            if letter.in_correct_position:
                color = Fore.GREEN
            elif letter.in_word:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            print(f"{color}{letter.text}{Fore.RESET}", end=" ")

        print("\n")
        if self._success:
            print(f"{Fore.GREEN}YOU WIN!{Fore.RESET}")
        elif self.done:
            print(f"{Fore.RED}You lost :(")
            print(f"The word was: {Fore.GREEN}{self._word.upper()}{Fore.RESET}")

    @property
    def done(self):
        return self._success or self._step >= self.total_steps

    def step(self, guess: str) -> WordleStepInfo:
        self._success, letters = _evaluate_guess(guess=guess, truth=self._word)
        info = WordleStepInfo(
            step=self._step, success=self._success, done=self.done, letters=letters
        )

        self.history.append(info)
        if not self.done:
            self._step += 1

        if not self.silent:
            self._print_step_info(info)

        return info

    def play(self):
        print("Wordle!\n")

        while not self.done:
            print(f"Step {self._step} of {self.total_steps}")
            guess = input("Enter a guess: ").lower().strip()
            _ = self.step(guess)


class MultiWordle:
    def __init__(
        self,
        num_words: int,
        total_steps: int,
        seed: Optional[int] = None,
        silent: bool = False,
    ):
        if seed is None:
            seed = int(time.time())
        self.wordles = [
            Wordle(total_steps=total_steps, seed=(seed + i), silent=True)
            for i in range(num_words)
        ]
        self.num_words = num_words
        self.total_steps = total_steps
        self.silent = silent

        self._step = 1
        self._success = False

    @property
    def done(self) -> bool:
        all_done = all(wordle.done for wordle in self.wordles)
        return all_done or self._step >= self.total_steps

    def step(self, guess: str) -> List[WordleStepInfo]:
        out: List[WordleStepInfo] = []
        for i, wordle in enumerate(self.wordles, 1):
            if wordle.done:
                continue

            info = wordle.step(guess)
            if not self.silent:
                print(f"Word {i} of {self.num_words}: ", end="")
                wordle._print_step_info(info)

            out.append(info)

        self._success = all(wordle._success for wordle in self.wordles)
        if not self.done:
            self._step += 1

        return out

    def play(self):
        print(f"{self.__class__.__name__}!\n")
        print(f"Num words: {self.num_words}\n")

        while not self.done:
            print(f"Step {self._step} of {self.total_steps}")
            guess = input("Enter a guess: ").lower().strip()
            _ = self.step(guess)


class Dordle(MultiWordle):
    def __init__(
        self, total_steps: int = 7, seed: Optional[int] = None, silent: bool = False
    ):
        super().__init__(num_words=2, total_steps=total_steps, seed=seed, silent=silent)


class Quordle(MultiWordle):
    def __init__(
        self, total_steps: int = 9, seed: Optional[int] = None, silent: bool = False
    ):
        super().__init__(num_words=4, total_steps=total_steps, seed=seed, silent=silent)


class Octordle(MultiWordle):
    def __init__(
        self, total_steps: int = 13, seed: Optional[int] = None, silent: bool = False
    ):
        super().__init__(num_words=8, total_steps=total_steps, seed=seed, silent=silent)


class StreamlitWordle(Wordle):
    def _render_step_info_streamlit(self, info: WordleStepInfo):
        import streamlit as st

        columns = st.columns(5)
        letters = info.letters

        for column, letter in zip(columns, letters):
            if letter.text == "_":
                color = "Gray"
            elif letter.in_correct_position:
                color = "Green"
            elif letter.in_word:
                color = "Yellow"
            else:
                color = "Red"
            with column:
                st.markdown(
                    MARKDOWN_LETTER_TEMPLATE.format(
                        color=color, letter=letter.text.upper()
                    ),
                    unsafe_allow_html=True,
                )

    def _render_empty_step_streamlit(self):
        self._render_step_info_streamlit()

    def render_streamlit(self):
        for step in self.history:
            self._render_step_info_streamlit(step)

        remaining_steps = self.total_steps - len(self.history)
        for _ in range(remaining_steps):
            self._render_step_info_streamlit(info=EMPTY_STEP_INFO)


def main_wordle():
    Wordle().play()


def main_multi_wordle():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-words", type=int, required=True)
    parser.add_argument("--total-steps", type=int, required=True)
    args = parser.parse_args()

    MultiWordle(num_words=args.num_words, total_steps=args.total_steps).play()


def main_quordle():
    Quordle().play()


def main_dordle():
    Dordle().play()


def main_octordle():
    Octordle().play()
