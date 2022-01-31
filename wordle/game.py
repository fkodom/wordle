import random
import time
from typing import Dict, List, Optional

from colorama import Fore

from wordle.data import load_word_frequencies

WORD_LENGTH = 5
STEPS_PER_GAME = 6
MARKDOWN_LETTER_TEMPLATE = """
<p style='color:{color};background-color:gray;font-size:24px;text-align:center'><b>{letter}</b></p>
"""
EMPTY_LETTER = {"letter": "_", "inWord": False, "inCorrectPosition": False}


class Wordle:
    def __init__(
        self,
        word_bank_size: int = 2500,
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
        self._done = False
        self._success = False
        self.history: List[Dict] = []

    @staticmethod
    def _evaluate_guess(guess: str, truth: str) -> Dict:
        guess = guess.lower().strip()
        assert len(guess) == 5
        return {
            "success": guess == truth,
            "letters": [
                {"letter": x, "inWord": x in truth, "inCorrectPosition": x == y}
                for x, y in zip(guess, truth)
            ],
        }

    def _print_step_info(self, info: Dict):
        for letter in info["letters"]:
            if letter["inCorrectPosition"]:
                color = Fore.GREEN
            elif letter["inWord"]:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            print(f"{color}{letter['letter']}{Fore.RESET}", end=" ")

        print("\n")
        if info["success"]:
            print(f"{Fore.GREEN}YOU WIN!{Fore.RESET}")
        elif info["done"]:
            print(f"{Fore.RED}You lost :(")
            print(f"The word was: {Fore.GREEN}{self._word}{Fore.RESET}")
        print()

    def step(self, guess: str) -> Dict:
        info = self._evaluate_guess(guess=guess, truth=self._word)
        info["step"] = self._step
        info["done"] = info["success"] or self._step == STEPS_PER_GAME

        self._step += 1
        self._done = info["done"]
        self._success = info["success"]
        self.history.append(info)

        if not self.silent:
            self._print_step_info(info)

        return info

    def play(self):
        print("Wordle!\n")

        while not self._done:
            print(f"Step {self._step} of {STEPS_PER_GAME}")
            guess = input("Enter a guess: ").strip("\n\r")
            _ = self.step(guess)

    def _render_step_info_streamlit(self, info: Dict):
        import streamlit as st

        columns = st.columns(5)
        letters = info.get("letters", [EMPTY_LETTER] * 5)

        for column, letter in zip(columns, letters):
            if letter["letter"] == "_":
                color = "Gray"
            elif letter["inCorrectPosition"]:
                color = "Green"
            elif letter["inWord"]:
                color = "Yellow"
            else:
                color = "Red"
            with column:
                st.markdown(
                    MARKDOWN_LETTER_TEMPLATE.format(
                        color=color, letter=letter["letter"].upper()
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
            self._render_step_info_streamlit(info={})


if __name__ == "__main__":
    Wordle().play()
