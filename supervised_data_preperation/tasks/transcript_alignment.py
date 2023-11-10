import numpy as np
import utils.file as utils
from pathlib import Path
from progress.bar import ChargingBar
import tasks.transcript_cleanup as pre

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


def write_to_file_wer(path, hand_snips, machine_snips, words_per_line) :
    hand_lines = [hand_snips[words_per_line*i: words_per_line*(i+1)] for i in range(int(len(hand_snips) / words_per_line ) + 1)]
    machine_lines = [machine_snips[words_per_line*i: words_per_line*(i+1)] for i in range(int(len(machine_snips) / words_per_line ) + 1)]
    with open(path, 'w') as file :
        for hand, machine in zip(hand_lines, machine_lines) :
            lengths = [max(len(i), len(j)) for i, j in zip(hand, machine)]
            hand = [w + (l-len(w))*" " for w, l in zip(hand, lengths)]
            machine = [w + (l-len(w))*" " for w, l in zip(machine, lengths)]
            file.write("Machine: " + " ".join(machine) + "\n")
            file.write("Hand:    " + " ".join(hand) + "\n\n")


def align_file(manual_source, automatic_source, operations_desination, write_only_operations=False) :
    machine_transcript_messy = utils.read_file(automatic_source)
    hand_transcript_messy = ' '.join([w['word'] for w in utils.read_label_timings_from_file(manual_source)])
    hand_trimmed, hand_clean = pre.process(transcript=hand_transcript_messy)
    machine_trimmed, machine_clean = pre.process(transcript=machine_transcript_messy)

    operations = get_operations(hand_clean.split(), machine_clean.split())    # list of {n, i, d, r}
    if write_only_operations :
        utils.write_file(operations_desination, ' '.join(operations))
    else :
        hand_snips, machine_snips = align(hand_trimmed.split(), machine_trimmed.split(), operations)
        write_to_file_wer(operations_desination, hand_snips, machine_snips, 30)


def align_dir(manual_dir, automatic_dir, destination_dir, write_only_operations=False) :

    files = utils.get_dir_tuples([ (manual_dir, "txt", lambda s : not 'Speech' in s), (automatic_dir, "txt", lambda s : True) ], lambda s1, s2: s1 == s2)
    files = [(f1, f2[0][1]) for (s, f1), f2 in files]

    for manual_file, automatic_file in ChargingBar("Align Transcripts").iter(files) :
        operations_file = utils.repath(manual_file, manual_dir, destination_dir)
        align_file(manual_file, automatic_file, operations_file, write_only_operations)