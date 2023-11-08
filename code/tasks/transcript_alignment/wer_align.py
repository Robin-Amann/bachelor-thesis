import numpy as np

# operations needed to transform 'ref' to 'hyp'
# operations are: 
# nothing = {'operation' = "nothing"},
# insertion = {'operation' = "insertion", 'value' = },
# deletion = {'operation' = "deletion", 'from' },
# replacement = {'operation' = "replacement", 'from' = , 'to' = },
def backtrack(from_words, to_words, matrix) : 
    operations = []
    i = len(to_words)
    j = len(from_words)
    while i > 0 and j > 0 :
        if to_words[i-1] == from_words[j-1] :
            operations.append("n")
            j -= 1
            i -= 1
        else :
            if matrix[i-1, j] <= matrix[i-1, j-1] and matrix[i-1, j] <= matrix[i, j-1] :
                operations.append("i")
                i -= 1
            elif matrix[i, j-1] <= matrix[i-1, j-1] and matrix[i, j-1] <= matrix[i-1, j] :
                operations.append("d")
                j -= 1
            else :
                operations.append("r")
                j -= 1
                i -= 1
    while i > 0 :
        operations.append("i")
        i -= 1
    while j > 0 :
        operations.append("d")
        j -= 1
    return operations[::-1]


def levenshtein_matrix(from_words, to_words) :
    d = np.zeros((len(to_words) + 1, len(from_words) + 1))
    for i in range(len(to_words) + 1):
        d[i, 0] = i
    for j in range(len(from_words) + 1):
        d[0, j] = j
    for i in range(1, len(to_words) + 1):
        for j in range(1, len(from_words) + 1):
            if to_words[i - 1] == from_words[j - 1]:
                d[i, j] = d[i - 1, j - 1]
            else:
                substitution = d[i - 1, j - 1] + 1
                insertion = d[i, j - 1] + 1
                deletion = d[i - 1, j] + 1
                d[i, j] = min(substitution, insertion, deletion)
    return d


def get_operations(from_words, to_words):
    d = levenshtein_matrix(from_words, to_words)
    return backtrack(from_words, to_words, d)


def align(start, end, operations, insertion_obj='') :
    x = start[:]
    y = end[:]
    i = 0
    j = 0
    for op in operations :
        if op == "i" :
            x.insert(i, insertion_obj)
        elif op == "d" :
            y.insert(j, insertion_obj)
        i += 1
        j += 1 
    return x, y


def print_words(start, end) :
    alignments = [zip(start, end), zip(end, start)]
    for alignment in alignments :
        for word, ref in alignment :
            if len(word) < len(ref) :
                print(word + (len(ref) - len(word)) * " " + " ", end="")
            else :
                print(word + " ", end="")
        print("")