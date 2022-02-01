# wordle
A minimal Python library for playing and solving [Wordle](https://www.powerlanguage.co.uk/wordle/) problems.


## Overview

* **Play Wordle** in the command line
* **Solve Wordle** in the command line
* **[Public Web App](https://share.streamlit.io/fkodom/wordle/main/app.py)** for endless Wordle games


## Install

Install directly from this repository:
```bash
pip install git+https://github.com/fkodom/wordle.git
```

To play a command-line game, enter the command:
```bash
play-wordle
```

To use the assistive solver algorithm:
```bash
solve-wordle
```


## About

I scraped common English words from the [BookCorpus](https://huggingface.co/datasets/bookcorpus) dataset to build a word bank for game play. The app chooses one of the 1500 most common 5-letter words for each game. That's over 4 years of unique, one-per-day Wordle games. :)

I also implemented a basic Wordle solver, based on `regex` and the same corpus of common English words. Assuming you use a common English word as your first guess, it has a success rate of about 98% and takes roughly 3.6 turns to win on average. (Measured on the 1500 game words, which also happen to be part of the solver's corpus. So maybe there's some bias in this measurement, but it still generally works well.)

> The first guess is not automated by the solver (yet). I tested the 500 most common words, to see which made for good initial guessesl **TABLE** had the highest success rate (98.7%), and **RATES** had the fewest average turns to win (3.41).


## TODO

* Generate better benchmarks for the solver, possibly with visualizations to add to the README.
* Provide a CLI interface for the Wordle solver, so people can use it for daily puzzles. :)
* Add unit tests
* GHA workflow for automated tests across Python versions
* Publish as PyPI package
