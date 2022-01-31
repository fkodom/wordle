# wordle
A minimal Python library for playing and solving [Wordle](https://www.powerlanguage.co.uk/wordle/) problems.

[[Demo streamlit app](https://share.streamlit.io/fkodom/wordle/main/app.py)]


## About

I scraped common English words from the [BookCorpus](https://huggingface.co/datasets/bookcorpus) dataset to build a word bank for game play. The app chooses one of the 2500 most common 5-letter words for each game. That's equivalent to almost 7 years of one-per-day Wordle games. :)

I also implemented a basic Wordle solver, based on `regex` and the same corpus of common English words. It has a success rate of about 99% on average, assuming you use a common word as your first guess. (Measured on the 2500 game words, which also happen to be part of the solver's corpus. So maybe there's some bias in this measurement, but it still generally works well.)

> The first guess is not automated by the solver. (Potentially something to work on!) I tested the 500 most common words, to see which made for good initial guessesl **TABLE** had the highest success rate (99.9%), and **RATES** had the fewest average turns to win (3.50).


## Install

### CLI

Install this library:
```bash
pip install git+https://github.com/fkodom/wordle.git
```

Start a game using the included CLI tool:
```bash
play-wordle
```

The following dialogue should appear:
```
Wordle!

Step 1 of 6
Enter a guess: _
```


### Streamlit App

Clone this repo, and `cd` into its root directory:
```bash
git clone https://github.com/fkodom/wordle.git
cd wordle
```

Install the library from source, including the `[app]` extra package:
```bash
pip install -e .[app]
```

Launch the app with `streamlit`:
```bash
streamlit run app.py
```


## TODO

* Generate better benchmarks for the solver, possibly with visualizations to add to the README.
* Provide a CLI interface for the Wordle solver, so people can use it for daily puzzles. :)
* Add unit tests
* GHA workflow for automated tests across Python versions
* Publish as PyPI package
