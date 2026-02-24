import argparse
import datetime as dt
import json
import urllib.request
from typing import List

from wordle.game import Wordle, WordleStepInfo
from wordle.solver import WordleSolver

NYT_ENDPOINT = "https://www.nytimes.com/svc/wordle/v2/{date}.json"
TOTAL_STEPS = 6


def _fetch_wordle_payload(date: dt.date) -> dict:
    url = NYT_ENDPOINT.format(date=date.strftime("%Y-%m-%d"))
    with urllib.request.urlopen(url) as resp:  # nosec - known public endpoint
        return json.loads(resp.read().decode("utf-8"))


def _simulate_game(answer: str, mode: str) -> List[WordleStepInfo]:
    game = Wordle(silent=True, total_steps=TOTAL_STEPS)
    game._word = answer
    solver = WordleSolver(mode=mode)
    guess = solver.recommend().recommended

    while guess != game._word and not game.done:
        if guess is None:
            break
        info = game.step(guess)
        guess = solver.update(info)

    if not game.done and guess is not None:
        game.step(guess)

    return game.history


def _steps_to_ascii(history: List[WordleStepInfo]) -> List[str]:
    rows: List[str] = []
    for info in history:
        row = "".join(
            "🟩"
            if letter.in_correct_position
            else "🟨"
            if letter.in_word
            else "⬛"
            for letter in info.letters
        )
        rows.append(row)
    return rows


def _format_share_text(payload: dict, history: List[WordleStepInfo]) -> str:
    puzzle_number = payload.get("days_since_launch")
    success = history[-1].success if history else False
    attempts = len(history)
    attempts_str = str(attempts) if success else "X"
    rows = "\n".join(_steps_to_ascii(history))
    return f"Wordle {puzzle_number} {attempts_str}/{TOTAL_STEPS}\n\n{rows}"


def main_bot_wordle():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD (defaults to today)",
    )
    parser.add_argument("--mode", type=str, default="turns-to-win")
    args = parser.parse_args()

    date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    payload = _fetch_wordle_payload(date)
    answer = payload["solution"].lower()
    history = _simulate_game(answer, mode=args.mode)
    print(_format_share_text(payload, history))
