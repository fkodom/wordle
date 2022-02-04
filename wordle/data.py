import os
from functools import lru_cache
from typing import Tuple

import gdown

WORDS_URL = (
    "https://drive.google.com/uc?id=1upgBKczLa9CU1q1V-_Hsi3ImPfPGqevb"
    # https://drive.google.com/file/d/1upgBKczLa9CU1q1V-_Hsi3ImPfPGqevb/view?usp=sharing
)
WORDS_PATH = os.path.join(
    os.path.dirname(__file__), os.path.pardir, "data", "words.txt"
)


def _download_words():
    os.makedirs(os.path.dirname(WORDS_PATH), exist_ok=True)
    gdown.download(WORDS_URL, WORDS_PATH)


@lru_cache()
def load_words() -> Tuple[str, ...]:
    if not os.path.exists(WORDS_PATH):
        _download_words()

    with open(WORDS_PATH, "r") as f:
        return tuple(line.lower().strip() for line in f.readlines())
