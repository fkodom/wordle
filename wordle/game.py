import random
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from colorama import Fore

from wordle.data import load_word_frequencies

WORD_LENGTH = 5
STEPS_PER_GAME = 6
MARKDOWN_LETTER_TEMPLATE = """
<p style='color:{color};background-color:gray;font-size:24px;text-align:center'><b>{letter}</b></p>
"""
# EMPTY_LETTER = {"letter": "_", "inWord": False, "inCorrectPosition": False}


@dataclass
class LetterEvaluation:
    text: str
    in_word: bool = False
    in_correct_position: bool = False


EMPTY_LETTER = LetterEvaluation(text="_")


@dataclass
class WordleStepInfo:
    step: int
    letters: Sequence[LetterEvaluation]
    success: bool = False
    done: bool = False


EMPTY_STEP_INFO = WordleStepInfo(step=0, letters=[EMPTY_LETTER] * 5)


def _evaluate_guess(guess: str, truth: str) -> Tuple[bool, List[LetterEvaluation]]:
    guess = guess.lower().strip()
    assert len(guess) == 5
    success = guess == truth
    letters = [
        LetterEvaluation(text=x, in_word=(x in truth), in_correct_position=(x == y))
        for x, y in zip(guess, truth)
    ]
    return success, letters


class Wordle:
    def __init__(
        self,
        word_bank_size: int = 1500,
        seed: Optional[int] = None,
        silent: bool = False,
    ):
        word_bank = load_word_frequencies(max_words=word_bank_size)
        if seed is None:
            seed = int(time.time())
        random.seed(seed)
        self._word = random.choice(list(word_bank.keys()))
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
        return self._success or self._step == STEPS_PER_GAME

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
            print(f"Step {self._step} of {STEPS_PER_GAME}")
            guess = input("Enter a guess: ").lower().strip()
            _ = self.step(guess)


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

        remaining_steps = STEPS_PER_GAME - len(self.history)
        for _ in range(remaining_steps):
            self._render_step_info_streamlit(info=EMPTY_STEP_INFO)


def main():
    Wordle().play()


if __name__ == "__main__":
    main()
