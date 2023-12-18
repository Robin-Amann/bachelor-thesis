import numpy as np
import utils.file as utils
from progress.bar import ChargingBar
import os

# calculate operations

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

import typing
# align lists
def align(start : list, end : list, operations : list = None, insertion_obj : typing.Any='') -> tuple[list, list]:
    '''
    if operations are not supplied, start and end are beeing simplified before calculating the operations.

    please refere to utils.transcript.simplify( ) for more information.
    '''
    if not operations :
        operations = get_operations([word_utils.simplify(word) for word in start], [word_utils.simplify(word) for word in end])
    x = start[:]
    y = end[:]
    i = 0
    for op in operations :
        if op == "i" :
            x.insert(i, insertion_obj)
        elif op == "d" :
            y.insert(i, insertion_obj)
        i += 1
    return x, y


import utils.transcript as word_utils
def align_words(start : list[dict], end : list[dict], insertion_obj : dict) :
    op = get_operations([word_utils.simplify(word['word']) for word in start], [word_utils.simplify(word['word']) for word in end])
    x, y = align(start, end, op, insertion_obj)
    return x, y, op


# calculate wer
def wer_and_ops(start : list[str], end : list[str]) :
    op = get_operations([word_utils.simplify(word) for word in start], [word_utils.simplify(word) for word in end])
    wer_value = calculate_wer(op)
    return wer_value, op


def calculate_wer(operations : list) :
    if len(operations) == 0 :
        return 1
    return (operations.count('i') + operations.count('d') + operations.count('r')) / len(operations)


# rest
def print_words(start : list[str], end : list[str]) :
    alignments = [zip(start, end), zip(end, start)]
    for alignment in alignments :
        for word, ref in alignment :
            if len(word) < len(ref) :
                print(word + (len(ref) - len(word)) * " " + " ", end="")
            else :
                print(word + " ", end="")
        print("")


# not in use
def dir_wer(manual_dir, automatic_dir, automatic_has_timing_info=True) :
    files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir] )
    wer = 0
    length = 0
    for manual_file, automatic_file in ChargingBar("Align Transcripts").iter(files) :
        if automatic_has_timing_info :
            automatic = [ w['word'] for w in utils.read_dict(automatic_file) ]
        else :
            automatic = utils.read_file(automatic_file).split()
        manual = [ w['word'] for w in utils.read_dict(manual_file) ]
        wer_value, ops = wer_and_ops(manual, automatic)
        length += len(ops)
        wer += wer_value * len(ops)
    return wer / length