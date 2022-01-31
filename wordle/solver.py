from typing import Dict, List, Optional

import regex

from wordle.data import load_word_frequencies
from wordle.game import WordleStepInfo


class Solver:
    def __init__(self, word_bank_size: Optional[int] = 7500):
        self.frequencies = load_word_frequencies(max_words=word_bank_size)
        self.history: List[WordleStepInfo] = []

    def update(self, step_info: WordleStepInfo) -> str:
        self.history.append(step_info)
        self.frequencies = _filter_frequencies_from_step_info(
            self.frequencies, step_info
        )
        out = _get_most_common_word(self.frequencies)
        return out


def _filter_frequencies_from_step_info(
    frequencies: Dict[str, int], info: WordleStepInfo
) -> Dict[str, int]:
    letters = info.letters
    exclude = [x.text for x in letters if not x.in_word]
    include = [x.text for x in letters if x.in_word]
    regex_terms = [x.text if x.in_correct_position else f"[^{x.text}]" for x in letters]
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
