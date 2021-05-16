import re

from flask import Flask, render_template, request, redirect, url_for, flash
from train import SpellChecker

app = Flask(__name__)


@app.route('/')
def initialize():
    return render_template('spellChecker.html', string_variable=None, incorrected_variable=None)


@app.route('/', methods=["POST"])
def spellChecker():
    regex1 = re.compile('[^a-zA-Z\s]')
    validCharTest = re.compile('[a-zA-Z]*')
    if request.method == 'POST':
        word = request.form['input-word']
        print('Requested: ', word)
        print(validCharTest.match(word))
        if word.isalpha():
            corrected_word = sc.getBestCandidate(word)
            print('Corrected: ', corrected_word)
            return render_template('spellChecker.html', corrected_variable=corrected_word, incorrected_variable=word)
        else:
            print('Invalid characters in ')
            return render_template('spellChecker.html', string_variable=None, incorrected_variable=None)
    else:
        print('Invalid request')
        return render_template('spellChecker.html', string_variable=None, incorrected_variable=None)


if __name__ == "__main__":
    sc = SpellChecker()
    exampleWord = 'academic'
    print("Probability of '%s' : %f" % (exampleWord, sc.getWordFreq(exampleWord)))
    exampleWord2 = 'the'
    print("Probability of '%s' : %f" % (exampleWord2, sc.getWordFreq(exampleWord2)))
    print(sc.getBestCandidate('yhe'))
    print(sc.getBestCandidate('tha'))
    print(sc.getBestCandidate('tge'))
    print(sc.getBestCandidate('ge'))
    app.run(debug=True)
