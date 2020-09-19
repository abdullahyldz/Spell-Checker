import re

from flask import Flask, render_template, request, redirect, url_for, flash
from train import SpellChecker

app = Flask(__name__)


@app.route('/')
def initialize():
    return render_template('spellChecker.html', string_variable=None, incorrected_variable=None)


@app.route('/', methods=["POST"])
def spellChecker():
    if request.method == 'POST':
        word = request.form['input-word']
        print('Requested: ', word)
        print(sc.regex2.match(word))
        if sc.regex2.match(word):
            corrected_word = sc.correctWord(word)
            print('Corrected: ', corrected_word)
            return render_template('spellChecker.html', corrected_variable=corrected_word, incorrected_variable=word)
        else:
            return render_template('spellChecker.html', string_variable=None, incorrected_variable=None)
    else:
        return render_template('spellChecker.html', string_variable=None, incorrected_variable=None)


if __name__ == "__main__":
    sc = SpellChecker()
    exampleWord = 'academic'
    print("Probability of '%s' : %f" % (exampleWord, sc.getWordFreq(exampleWord)))
    exampleWord2 = 'the'
    print("Probability of '%s' : %f" % (exampleWord2, sc.getWordFreq(exampleWord2)))
    print(sc.correctWord('yhe'))
    print(sc.correctWord('tha'))
    print(sc.correctWord('tge'))
    print(sc.correctWord('ge'))
    app.run(debug=True)
