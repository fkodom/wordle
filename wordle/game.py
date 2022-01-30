import random
from typing import Dict, List

from colorama import Fore

from wordle.data import load_word_frequencies

WORD_LENGTH = 5
STEPS_PER_GAME = 6


class Wordle:
    def __init__(self, word_bank_size: int = 2500, silent: bool = False):
        word_bank = load_word_frequencies(max_words=word_bank_size)
        self.__word = random.choice(list(word_bank.keys()))
        self.silent = silent

        self._step: int = 1
        self._done: bool = False
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

    @staticmethod
    def _print_step_info(info: Dict):
        for letter in info["letters"]:
            if letter["inCorrectPosition"]:
                color = Fore.GREEN
            elif letter["inWord"]:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            print(f"{color}{letter['letter']}{Fore.RESET}", end=" ")

        print()
        if info["success"]:
            print(f"{Fore.GREEN}YOU WIN!{Fore.RESET}")
        else:
            print()

    def step(self, guess: str) -> Dict:
        info = self._evaluate_guess(guess=guess, truth=self.__word)
        info["step"] = self._step
        info["done"] = info["success"] or self._step == STEPS_PER_GAME

        self._step += 1
        self._done = info["done"]
        self.history.append(info)

        if not self.silent:
            self._print_step_info(info)

        return info

    def play(self):
        print("Wordle!\n")

        while not self._done:
            print(f"Step {self._step} of {STEPS_PER_GAME}")
            guess = input("Enter a guess: ").strip("\n\r")
            info = self.step(guess)
            self._print_step_info(info)


if __name__ == "__main__":
    Wordle().play()
