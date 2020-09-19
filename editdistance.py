def editDistance(word1, word2):  # levenshtein edit distance (insertion, deletion, substitution)
    len1 = len(word1)
    len2 = len(word2)
    distanceMap = [[0] for i in range(len1 + 1)]
    distanceMap[0] = [i for i in range(len2 + 1)]
    for i in range(len1 + 1):
        distanceMap[i][0] = i

    for i in range(len1):
        for j in range(len2):
            adder = 0 if (word1[i] == word2[j]) else 1
            dist = min(distanceMap[i + 1][j] + 1, distanceMap[i][j + 1] + 1, distanceMap[i][j] + adder)
            distanceMap[i + 1].append(dist)

    return distanceMap[len1][len2]


def D_L_editDistance(word1,
                     word2):  # damerau levenshtein edit distance (insertion, deletion, substitution, transposition)
    len1 = len(word1)
    len2 = len(word2)
    distanceMap = [[0] for i in range(len1 + 1)]  # Create a (len1+1)x(len2+1) matrix
    distanceMap[0] = [i for i in range(len2 + 1)]  # Initialize first row from 0 to len2
    for i in range(len1 + 1):  # Initialize first column from 0 to len1
        distanceMap[i][0] = i

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            adder = 0 if (word1[i - 1] == word2[
                j - 1]) else 1  # If letters are same, then substitution costs 0 else costs 1
            dist = min(distanceMap[i][j - 1] + 1, distanceMap[i - 1][j] + 1, distanceMap[i - 1][
                j - 1] + adder)  # Edit distance so far is calculated from its left, top and top-left neigbor cells
            if (i > 1 and j > 1 and word1[i - 2:i] == word2[j - 2:j][
                                                      ::-1]):  # If previous 2 characters of words are swapped of each other, then transpose operation occurred
                dist = min(distanceMap[i - 2][j - 2] + 1,
                           dist)  # then dist is recalculated as minimum of just calculated distance and edit distance of where transposition started +1
            distanceMap[i].append(dist)
    return distanceMap[len1][len2]


def D_L_Backtrack(word1, word2):
    len1 = len(word1)
    len2 = len(word2)
    if (word1 == ''):
        return [('insertion', word2, '@')]
    elif (word2 == ''):
        return [('deletion', word1, '@')]
    distanceMap = [[0] for i in range(len1 + 1)]
    distanceMap[0] = [i for i in range(len2 + 1)]
    for i in range(len1 + 1):
        distanceMap[i][0] = i

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            adder = 0 if (word1[i - 1] == word2[j - 1]) else 1
            # print(i,j,adder)
            dist = min(distanceMap[i][j - 1] + 1, distanceMap[i - 1][j] + 1, distanceMap[i - 1][j - 1] + adder)
            if (i > 1 and j > 1 and word1[i - 2:i] == word2[j - 2:j][::-1]):
                dist = min(distanceMap[i - 2][j - 2] + 1, dist)
            distanceMap[i].append(dist)
    # up to this point, operations are same with method D_L_editDistance
    # then distanceMap matrix is backtrack for solution

    i = len1
    j = len2
    operations = []
    # the idea of this while loop is to start from the most bottom-right cell and go up and left
    # until one index reaches 1
    # go up means deletion, go left is insertion, go top-left is substitution, else it is transposition
    # operation selection hierarcy is like that.
    while (i >= 1 and j >= 1):
        if (distanceMap[i][j] == distanceMap[i][j - 1] + 1):
            operations.append(('insertion', word2[j - 1], word1[i - 1]))
            j = j - 1
        elif (distanceMap[i][j] == distanceMap[i - 1][j] + 1):
            operations.append(('deletion', word1[i - 1], word1[i - 2]))
            i = i - 1
        elif (distanceMap[i][j] == distanceMap[i - 1][j - 1] + (0 if word1[i - 1] == word2[j - 1] else 1)):
            if (not word1[i - 1] == word2[j - 1]):
                operations.append(('substitution', word2[j - 1], word1[i - 1]))
            i = i - 1
            j = j - 1
        else:
            operations.append(('transposition', word2[j - 1], word1[i - 1]))
            i = i - 2
            j = j - 2
    # after that i need to reach to most top-left cell.
    # '@' symbolizes the beginning of the words
    word1 = word1[:-1] + '@'  # word1=word1[:-1]+'@' changes last character to @
    word2 = word2[:-1] + '@'  # to detect characters are deleted or inserted at the beginning of the word
    while (i > 0):
        operations.append(('deletion', word1[i - 1], word1[i - 2]))
        i = i - 1
    while (j > 0):
        operations.append(('insertion', word2[j - 1], word1[i - 1]))
        j = j - 1
    return operations