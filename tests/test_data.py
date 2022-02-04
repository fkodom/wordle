from wordle.data import _download_words, load_words


def test_load_words():
    words = load_words()
    assert len(words) == 2315
    assert all(len(w) == 5 for w in words)


def test_download_words():
    _download_words()
    test_load_words()
