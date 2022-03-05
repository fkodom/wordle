from wordle.game import LetterEvaluation, Wordle, WordleStepInfo, _evaluate_guess


def test_letter_evaluation():
    eval = LetterEvaluation()
    assert eval.empty

    eval.text = "a"
    assert not eval.empty

    assert hasattr(eval, "in_word")
    assert isinstance(eval.in_word, bool)
    assert hasattr(eval, "in_correct_position")
    assert isinstance(eval.in_correct_position, bool)


def test_wordle_step_info():
    info = WordleStepInfo(step=1, letters=(LetterEvaluation(),) * 5)
    assert hasattr(info, "success")
    assert isinstance(info.success, bool)
    assert hasattr(info, "done")
    assert isinstance(info.done, bool)
    assert hasattr(info, "guess")
    assert isinstance(info.guess, str)
    assert info.guess == "_" * 5


def test_evaluate_guess():
    guess, truth = "hello", "world"
    success, letters = _evaluate_guess(guess, truth)
    assert success is False
    targets = (
        LetterEvaluation("h"),
        LetterEvaluation("e"),
        LetterEvaluation("l"),
        LetterEvaluation("l", in_word=True, in_correct_position=True),
        LetterEvaluation("o", in_word=True),
    )
    for letter, target in zip(letters, targets):
        assert letter.text == target.text
        assert letter.in_word is target.in_word
        assert letter.in_correct_position is target.in_correct_position

    success, letters = _evaluate_guess("hello", "hello")
    assert success is True
    for letter in letters:
        assert letter.in_word is True
        assert letter.in_correct_position is True


def test_game_step():
    game = Wordle()
    game._word = "hello"
    info = game.step(guess="world")
    assert isinstance(info, WordleStepInfo)
    assert info.success is False
    assert game.done is False

    game = Wordle()
    game._word = "hello"
    info = game.step(guess="hello")
    assert isinstance(info, WordleStepInfo)
    assert info.success is True
    assert game.done is True


def test_game_done():
    game = Wordle()
    game._word = "hello"
    assert game.done is False

    game._step = game.total_steps
    assert game.done is True

    game._step = 1
    game.step(guess="hello")
    assert game.done is True
