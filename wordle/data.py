import os
from functools import lru_cache
from typing import List

WORDS_PATH = os.path.join(
    os.path.dirname(__file__), os.path.pardir, "data", "words.txt"
)


@lru_cache()
def load_words() -> List[str]:
    with open(WORDS_PATH, "r") as f:
        return [line.lower().strip() for line in f.readlines()]
