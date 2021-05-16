from editdistance import D_L_Backtrack, D_L_editDistance
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string
import re
import pandas as pd


corpusFile = 'data/corpus.txt'
testCorrectFile = 'data/test-words-correct.txt'
testMisspelledFile = 'data/test-words-misspelled.txt'
spellErrorsFile = 'data/spell-errors.txt'


text = "Hello everyone. Welcome to GeeksforGeeks."
print(word_tokenize(text))

def char_position(letter):
    return ord(letter) - 97

letters = 'abcdefghijklmnopqrstuvwxyz@*'  # '@' is beginning of strings and '*' is any non-alphanumeric character that can be mistyped.

def char_position(letter):
    return ord(letter) - 97

 
class SpellChecker:
    def preprocessInputQuery(self, query):
        newQuery = "".join([char if char not in self.removalCharacters else ' ' for char in query])
        return newQuery

    def __init__(self):
        self.corpusFile = 'data/corpus.txt'
        self.spellErrorsFile = 'data/spell-errors.txt'
        self.letters = 'abcdefghijklmnopqrstuvwxyz@*'
        self.removalCharacters = string.punctuation + '\n\t'

        self.stopwordList = stopwords.words('english')
        corpus = self.readCorpus(self.corpusFile)
        tokens = self.getTokens(corpus, self.stopwordList)
        self.setOfTokens = set(tokens)
        self.wordFreqTable = self.getFrequencyTable(tokens)

        spellErrorSamples = self.readSpellErrors(spellErrorsFile)
        confusion_matrix = self.createConfusionMatricesFromCorrections(spellErrorSamples)

        self.deletionFrame = pd.DataFrame(confusion_matrix['deletion'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))
        self.insertionFrame= pd.DataFrame(confusion_matrix['insertion'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))
        self.substitutionFrame=pd.DataFrame(confusion_matrix['substitution'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))
        self.transpositionFrame=pd.DataFrame(confusion_matrix['transposition'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))

    def readCorpus(self, filename):
        raw_corpus = open(filename).read().lower()
        corpus = "".join([char if char not in self.removalCharacters else ' ' for char in raw_corpus ])
        return corpus

    def getTokens(self, corpus, stopwordList):
        tokens = [token for token in word_tokenize(corpus) if token not in stopwordList]
        return tokens

    def getFrequencyTable(self, tokens):
        counter = Counter(tokens)
        frequencyItems = []
        for token, count in counter.items():
            frequencyItems.append([token, count, count / len(tokens)])
        wordFreqTable = pd.DataFrame(sorted(frequencyItems, key=lambda tup: tup[2], reverse=True), columns=['word', 'count', 'percentage'])
        return wordFreqTable


    def createConfusionMatricesFromCorrections(self, spell_error_samples):
        
        confusion_matrix_substitution = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix_transposition = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix_insertion = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix_deletion = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix = {'deletion': confusion_matrix_deletion,
                            'insertion': confusion_matrix_insertion,
                            'substitution': confusion_matrix_substitution,
                            'transposition': confusion_matrix_transposition}
        # For each spell error sample
        # backtrack is applied to both error and its correct version
        # get a correction such as ('deleted', 'c', 'a') meaning c is deleted after 'a'
        # then for each correction, confusion matrix [correction_type] is updated
        for (key,spellErrors) in spell_error_samples.items():
            for spellError in spellErrors:
                operations = D_L_Backtrack(spellError[0], key)
                for operation in operations:
                        x = char_position(operation[1]) if 0<=char_position(operation[1])<=25 else 27  # 0<=pos<=25 is for letters else it is * (wildcard)
                        y = char_position(operation[2]) if operation[2] != '@' and 0<=char_position(operation[2])<=25 else 26 if operation[2] == '@' else 27
                        confusion_matrix[operation[0]][x][y]+=spellError[1]

        return confusion_matrix

    def readSpellErrors(self, filename):
        spell_errors = []
        with open(filename) as fp:
            line = fp.readline()
            while(line):
                spell_errors.append(line[:-1])
                line = fp.readline()
        spell_error_samples = {}
        for spl_error in spell_errors:
            spl = spl_error.split(':') # first split it into key and possible misspellings
            spell_error_samples[spl[0].lower()] = [] # key is lowered and put in
            splErrors = spl[1].split(',') # splErrors are [loking, luing*2]
            for err in splErrors:
                spell_error_samples[spl[0].lower()].append(err.replace(' ', '').lower())
        for se in spell_error_samples.items():
            spell_error_samples[se[0]] = []
            for err in se[1]:
                if('*' in err):
                    sp = err.split('*') # If it has a * in it, I split it and take the number
                    spell_error_samples[se[0]].append((sp[0], int(sp[1])))
                else:
                    spell_error_samples[se[0]].append((err, 1)) # else 1 is placed in.
        return spell_error_samples
    

    def getCandidates(self, testWord):
        # First filter by length
        candidatesWithLengthDifference1 = [word for word in self.setOfTokens if (abs(len(word) - len(testWord)) <= 1)]
        # Secondly, filter by edit distance using D_L_editDistance method
        candidatesWithEditDistance1 = [candidate for candidate in candidatesWithLengthDifference1 if (D_L_editDistance(candidate, testWord) <= 1)]
        return candidatesWithEditDistance1

    def getWordFreq(self, word):
        if(word not in self.setOfTokens):
            return 0
        located = self.wordFreqTable.loc[self.wordFreqTable['word'] == word]
        return float(located['percentage'])

    def getProbabilityFromConfusionMatrix(self, operation):
        if(operation[0] == 'insertion'):
            series = self.insertionFrame.loc[operation[1]]
            return round(series[operation[2]]/sum(series), 7)
        elif(operation[0] == 'deletion'):
            series = self.deletionFrame.loc[operation[1]]
            return round(series[operation[2]]/sum(series), 7)

        elif(operation[0] == 'substitution'):
            series = self.substitutionFrame.loc[operation[1]]
            return round(series[operation[2]]/sum(series), 7)

        elif(operation[0] == 'transposition'):
            series = self.transpositionFrame.loc[operation[1]]
            return round(series[operation[2]]/sum(series), 7)


    def getBestCandidate(self, misspelledWord):
        bestCandidateScore = 0
        bestCandidate = misspelledWord
        candidates = self.getCandidates(misspelledWord)
        for candidate in candidates:
            candidateFrequency = self.getWordFreq(candidate)
            operation = D_L_Backtrack(candidate, misspelledWord) # What is the operation to get to candidate from misspelledWord
            # operation[0] is enough for words with edit distance 1
            probabilityFromConfusionMatrix = self.getProbabilityFromConfusionMatrix(operation[0]) # P(x|w)
            if(probabilityFromConfusionMatrix * candidateFrequency >= bestCandidateScore):
                bestCandidateScore = probabilityFromConfusionMatrix * candidateFrequency # P(x|w) * p(x)
                bestCandidate = candidate
        return bestCandidate

    
    def getSmoothedProbabilityFromConfusionMatrix(self, operation):
        if(operation[0] == 'insertion'):
            series = self.insertionFrame.loc[operation[1]]
            return (series[operation[2]]+1)/(sum(series)+len(letters))
        elif(operation[0] == 'deletion'):
            series = self.deletionFrame.loc[operation[1]]
            return (series[operation[2]]+1)/(sum(series)+len(letters))

        elif(operation[0] == 'substitution'):
            series = self.substitutionFrame.loc[operation[1]]
            return (series[operation[2]]+1)/(sum(series)+len(letters))

        elif(operation[0] == 'transposition'):
            series = self.transpositionFrame.loc[operation[1]]
            return (series[operation[2]]+1)/(sum(series)+len(letters))

    