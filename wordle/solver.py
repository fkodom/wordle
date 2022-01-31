import regex
from typing import Dict, List, Optional

from wordle.data import load_word_frequencies


class Solver:
    def __init__(self, word_bank_size: Optional[int] = 7500):
        self.frequencies = load_word_frequencies(max_words=word_bank_size)
        self.history: List[Dict] = []

    def update(self, step_info: Dict) -> str:
        self.history.append(step_info)
        self.frequencies = _filter_frequencies_from_step_info(
            self.frequencies, step_info
        )
        out = _get_most_common_word(self.frequencies)
        return out


def _filter_frequencies_from_step_info(
    frequencies: Dict[str, int], info: Dict
) -> Dict[str, int]:
    letters = info["letters"]
    exclude = [x["letter"] for x in letters if not x["inWord"]]
    include = [x["letter"] for x in letters if x["inWord"]]
    regex_terms = [
        x["letter"] if x["inCorrectPosition"] else f"[^{x['letter']}]" for x in letters
    ]
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


def binary_distance(w1: str, w2: str) -> float:
    return sum(l1 == l2 for l1, l2 in zip(w1, w2)) / len(w1)
