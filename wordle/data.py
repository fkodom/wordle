from functools import lru_cache
import gzip
import pickle
import os
from typing import Dict, Optional

WORD_FREQUENCIES_PATH = os.path.join(
    os.path.dirname(__file__), os.path.pardir, "data", "word-frequencies.pkl.gz"
)


@lru_cache()
def _load_raw_word_frequencies() -> Dict[str, int]:
    with gzip.open(WORD_FREQUENCIES_PATH, "rb") as f:
        return pickle.load(f)


def load_word_frequencies(
    max_words: Optional[int] = None, min_freq: Optional[float] = None
) -> Dict[str, int]:
    frequencies = _load_raw_word_frequencies()
    if min_freq is not None:
        frequencies = {w: f for w, f in frequencies.items() if f >= min_freq}
    if max_words is not None:
        selected_words = sorted(
            list(frequencies.keys()), key=(lambda word: -frequencies[word])
        )[:max_words]
        frequencies = {w: frequencies[w] for w in selected_words}

    return frequencies
