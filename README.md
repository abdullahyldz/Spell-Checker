![image](https://user-images.githubusercontent.com/44057640/118408872-278c8b00-b690-11eb-807c-1142c653e894.png)

Estimating a unigram language model P(w) using a [corpus](http://norvig.com/big.txt) of concatenation of several public domain books from Project Gutenberg as well as lists
of most frequent words from Wiktionary and the British National Corpus </br>

Given a query word;
Application calculates a set of words whose edit distance to given word is 1. (candidates) To calculate the edit distance, Damerau - Levenshtein edit distance is used.

Another [corpus](http://norvig.com/ngrams/spell-errors.txt) that represents number of error occurrance in search queries is also used.

Those candidates are sorted according to the scores in their P(w)*P(x|w) calculations.

Spell Checker application is implemented with Flask, Python

To render the webpage, Jinja templates are used with pure HTML, CSS

### How to run

1. Command `python main.py` to start the server

2. Connect to `http://localhost:5000/`
