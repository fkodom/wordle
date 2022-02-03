# wordle

Fastest [Wordle](https://www.powerlanguage.co.uk/wordle/) solver in the West.

* 99.73% success rate
* 3.634 average turns to win
* <5 ms per guess

![quick draw](https://media.giphy.com/media/aqDXCH2M1ycEw/giphy.gif)


## Install

Install directly from this repository:
```bash
pip install git+https://github.com/fkodom/wordle.git
```

## Solve

Launch the assistive solver:
```bash
solve-wordle
```

## Play

Visit the **[Public Web App](https://share.streamlit.io/fkodom/wordle/main/app.py)**, or play a command line game:
```bash
play-wordle
```

## Benchmarks
Full details in [benchmarks.jsonl](data/benchmarks.jsonl).

* Accuracy (99.73%) and turns-to-win (3.634) are averages over recommended starting words.
* RALPH has the highest win percentage (99.91%)
* SLATE has the fewest turns to win (3.586)
* SHALT is a good all-around choice (99.74%, 3.629)

<img src="data/benchmarks.jpg" height="600px" />

## How It Works

Exactly solving for word probabilities requires an exhaustive search through all possible word combinations. (There are way too many to be fast or practical.) Instead, we approximate them using a cheaper method.

First, a few definitions:

> $p_i(c)$ $\to$ probability of character $c$ at position $i$ in the word
> 
> $p(c)$ $\to$ probability of character $c$ at any position
> 
> $p(w)$ $\to$ probability of a word ($c_1$, $c_2$, $c_3$, $c_4$, $c_5$)
> 
> $n_c(w)$ $\to$ counts of character $c$ in word $w$
> 
> $n_c$ $\to$ counts of character $c$ in the remaining word bank


Very roughly speaking, the word probability scales with each of $p_i(c)$ and $p(c)$:

$$p(w) \sim \prod_i p_i(c_i) \, p(c_i)$$

Then, $p_i(c)$ and $p(c)$ can be approximated from the remaining possible words, just by counting the frequencies of different letters. Then, to avoid over-counting from words with repeated letters, we divide by the number of identical permutations. 

$$p(c) \sim \frac{n_{c}}{n_{all} \cdot n_c(w)!}$$


## TODO

* Generate better benchmarks for the solver, with visualizations for the README.
* Unit tests
* GHA workflow for automated tests across Python versions
* Publish as PyPI package
