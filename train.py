import re
import pandas as pd
from editdistance import D_L_Backtrack, D_L_editDistance
from nltk.tokenize import word_tokenize

corpusFile = 'data/corpus.txt'
testCorrectFile = 'data/test-words-correct.txt'
testMisspelledFile = 'data/test-words-misspelled.txt'
spellErrorsFile = 'data/spell-errors.txt'


text = "Hello everyone. Welcome to GeeksforGeeks."
print(word_tokenize(text))

def char_position(letter):
    return ord(letter) - 97

letters = 'abcdefghijklmnopqrstuvwxyz@*'  # '@' is beginning of strings and '*' is any non-alphanumeric character that can be mistyped.


class SpellChecker:
    def __init__(self):
        self.regex1 = re.compile('[^a-zA-Z\s]')
        self.regex2 = re.compile('[a-zA-Z]')
        corpus = self.regex1.sub('', open(corpusFile).read().lower())       # Corpus is read from 'corpus.txt' file
        # First parameter is the replacement, second parameter is your input string
        self.tokens = word_tokenize(corpus[:20000])
        self.numberOfTokens = len(self.tokens)

        self.word_list_set = set(self.tokens)  # word_list_set is our dictionary
        print("Number of tokens: %d" % self.numberOfTokens)
        wordFreqDf = pd.DataFrame({'word': [], 'freq': [], 'percentage': []})
        wordFreq = []
        for word in self.word_list_set:
            count = self.tokens.count(word)
            wordFreq.append([word, count, count / self.numberOfTokens])  # word, its count and probability is added to DataFrame
        wordFreq = sorted(wordFreq, key=lambda tup: tup[2], reverse=True)
        print('Creating word frequencies')
        self.wordFreqDf = pd.DataFrame(wordFreq, columns=['word', 'count', 'percentage'])
        print('DONE: Creating word frequencies')
        print(self.wordFreqDf.head(20))
        self.readSpellErrors()
        print('Creating confusion matrices')
        confusion_matrix = self.createConfusionMatricesFromCorrections()
        print('DONE: Creating confusion matrices')
        self.deletionFrame = pd.DataFrame(confusion_matrix['deletion'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))
        self.insertionFrame= pd.DataFrame(confusion_matrix['insertion'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))
        self.substitutionFrame=pd.DataFrame(confusion_matrix['substitution'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))
        self.transpositionFrame=pd.DataFrame(confusion_matrix['transposition'], columns = list('abcdefghijklmnopqrstuvwxyz@*'), index = list(letters))

    def correctWord(self, testWord):
        print(testWord)
        bestCandidate = self.bestCandidate(testWord)
        bestCandidateSmoothed = self.bestCandidateSmoothed(testWord)

        print('best candidate: ', bestCandidate)
        print('best candidate smoothed: ', bestCandidateSmoothed)
        return bestCandidateSmoothed

    def readSpellErrors(self):
        spell_errors = []
        with open(spellErrorsFile) as fp:
            line = fp.readline()
            while(line):
                spell_errors.append(line[:-1])
                line = fp.readline()
        self.spell_error_samples = {}
        for spl_error in spell_errors:
            spl = spl_error.split(':') # first split it into key and possible misspellings
            self.spell_error_samples[spl[0].lower()] = [] # key is lowered and put in
            splErrors = spl[1].split(',') # splErrors are [loking, luing*2]
            for err in splErrors:
                self.spell_error_samples[spl[0].lower()].append(err.replace(' ', '').lower())
        for se in self.spell_error_samples.items():
            self.spell_error_samples[se[0]] = []
            for err in se[1]:
                if('*' in err):
                    sp = err.split('*') # If it has a * in it, I split it and take the number
                    self.spell_error_samples[se[0]].append((sp[0], int(sp[1])))
                else:
                    self.spell_error_samples[se[0]].append((err, 1)) # else 1 is placed in.

    def createConfusionMatricesFromCorrections(self):
        confusion_matrix_substitution = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix_transposition = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix_insertion = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix_deletion = [[0 for i in range(len(letters))] for j in range(len(letters))]
        confusion_matrix = {'deletion': confusion_matrix_deletion,
                           'insertion': confusion_matrix_insertion,
                           'substitution': confusion_matrix_substitution,
                           'transposition': confusion_matrix_transposition}
        # For each spell error sample
        # backtrack is applied to error and its correct version
        # and get a correction such as ('deleted', 'c', 'a')
        # then for each correction, confusion matrix [ correction_type] is updated
        for (key,spellErrors) in self.spell_error_samples.items():
            for spellError in spellErrors:
                operations = D_L_Backtrack(spellError[0], key)
                for operation in operations:
                        x = char_position(operation[1]) if 0<=char_position(operation[1])<=25 else 27  # 0<=pos<=25 is for letters else it is * (wildcard)
                        y = char_position(operation[2]) if operation[2] != '@' and 0<=char_position(operation[2])<=25 else 26 if operation[2] == '@' else 27
                        confusion_matrix[operation[0]][x][y]+=spellError[1]

        return confusion_matrix

    def getWordFreq(self, word):
        if(word not in self.word_list_set):
            return 0
        located = self.wordFreqDf.loc[self.wordFreqDf['word'] == word]
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

    def getCandidates(self, testWord):
        # First filter by length
        candidates_len1 = [word for word in self.word_list_set if (abs(len(word) - len(testWord)) <= 1)]
        # Secondly, filter by edit distance using D_L_editDistance method
        candidates_edit1 = [candidate for candidate in candidates_len1 if (D_L_editDistance(candidate, testWord) == 1)]
        return candidates_edit1

    def bestCandidate(self, misspelledWord):
        best = 0
        bestCandidate = misspelledWord
        candidates = self.getCandidates(misspelledWord)
        for candidate in candidates:
            probx = self.getWordFreq(candidate) # P(x)
            operation = D_L_Backtrack(candidate, misspelledWord) # What is the operation to get to candidate from misspelledWord
            # operation[0] is enough for words with edit distance 1
            probcovmat = self.getProbabilityFromConfusionMatrix(operation[0]) # P(x|w)
            if(probcovmat*probx>=best):
                best = probcovmat*probx # P(x|w) * p(x)
                bestCandidate = candidate
        return bestCandidate


    def bestCandidateSmoothed(self, misspelledWord):
        best = 0
        bestCandidate = misspelledWord
        candidates = self.getCandidates(misspelledWord)
        for candidate in candidates:
            probx = self.getWordFreq(candidate)
            operation = D_L_Backtrack(candidate, misspelledWord) # What is the operation to get to candidate from misspelledWord
            probcovmat = self.getProbabilityFromConfusionMatrix(operation[0])
            if(probcovmat*probx>=best):
                best = probcovmat*probx
                bestCandidate = candidate
        return bestCandidate


