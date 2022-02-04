import json
import os
from functools import lru_cache
from typing import Dict, List

import matplotlib.pyplot as plt

from wordle.solver import Solver

BENCHMARKS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "benchmarks.jsonl"
)
FIGURE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "benchmarks.jpg")


@lru_cache()
def load_benchmarks() -> List[Dict]:
    with open(BENCHMARKS_PATH, "r") as f:
        return [json.loads(line.strip()) for line in f.readlines() if line.strip()]


def load_recommended_words() -> List[Dict]:
    benchmarks = load_benchmarks()
    recommended = Solver().recommend()
    words = [recommended.recommended, *recommended.alternatives]
    return [b for b in benchmarks if b["first_guess"] in words]


if __name__ == "__main__":
    plt.figure(figsize=(10, 10), dpi=250)

    benchmarks = load_benchmarks()
    words = [b["first_guess"] for b in benchmarks]
    win_percentages = [b["win_percentage"] for b in benchmarks]
    average_turns = [b["average_turns"] for b in benchmarks]
    plt.plot(win_percentages, average_turns, "b.", markersize=5)

    recommended = load_recommended_words()
    recommended_words = [b["first_guess"] for b in recommended]
    recommended_win_percentages = [b["win_percentage"] for b in recommended]
    recommended_average_turns = [b["average_turns"] for b in recommended]
    plt.plot(recommended_win_percentages, recommended_average_turns, "r.", markersize=5)
    breakpoint()

    plt.legend(["all words", "recommended"])
    plt.xlabel("Win Percentage")
    plt.ylabel("Avg. Turns to Win")

    for word, pct, turns in zip(words, win_percentages, average_turns):
        plt.annotate(
            word,
            (pct, turns),
            fontsize=4,
            textcoords="offset points",
            xytext=(0, -5),
            ha="center",
        )

    plt.tight_layout()
    plt.savefig(FIGURE_PATH)
