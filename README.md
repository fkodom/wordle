# wordle

Fastest [Wordle](https://www.powerlanguage.co.uk/wordle/) solver in the West.

* 99.83% success rate
* 3.597 average turns to win

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

> <img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;p_i(c)" title="\bg_white p_i(c)" /> --> probability of character $c$ at position $i$ in the word
> 
> <img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;p(c)" title="\bg_white p(c)" /> --> probability of character $c$ at any position
> 
> <img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;p(w)" title="\bg_white p(w)" /> --> probability of a word ($c_1$, $c_2$, $c_3$, $c_4$, $c_5$)
> 
> <img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;n_c(w)" title="\bg_white n_c(w)" /> --> counts of character $c$ in word $w$
> 
> <img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;n_c" title="\bg_white n_c" /> --> counts of character $c$ in the remaining word bank


Very roughly speaking, the word probability scales with each of $p_i(c)$ and $p(c)$:

<!-- $$p(w) \sim \prod_i p_i(c_i) \, p(c_i)$$ -->
<p style="text-align:center;"><img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;p(w)&space;\sim&space;\prod_i&space;p_i(c_i)&space;\,&space;p(c_i)" title="\bg_white p(w) \sim \prod_i p_i(c_i) \, p(c_i)" /></p>

Then, <img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;p_i(c)" title="\bg_white p_i(c)" /> and <img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;p(c)" title="\bg_white p(c)" /> can be approximated from the remaining possible words, just by counting the frequencies of different letters. Then, to avoid over-counting from words with repeated letters, we divide by the number of identical permutations. 

<!-- $$p(c) \sim \frac{n_{c}}{n_{all} \cdot n_c(w)!}$$ -->
<p style="text-align:center;"><img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;p(c)&space;\sim&space;\frac{n_{c}}{n_{all}&space;\cdot&space;n_c(w)!}&space;" title="\bg_white p(c) \sim \frac{n_{c}}{n_{all} \cdot n_c(w)!} " /></p>
