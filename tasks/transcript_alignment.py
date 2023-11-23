import numpy as np
import utils.file as utils
import utils.constants as constants
from progress.bar import ChargingBar
import tasks.transcript_cleanup as pre
import os

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

def full_align(start, end, insertion_obj='') :
    op = get_operations(start, end)
    return align(start, end, op, insertion_obj)

def print_words(start, end) :
    alignments = [zip(start, end), zip(end, start)]
    for alignment in alignments :
        for word, ref in alignment :
            if len(word) < len(ref) :
                print(word + (len(ref) - len(word)) * " " + " ", end="")
            else :
                print(word + " ", end="")
        print("")

def print_words_new(transcripts) :
    for transcript in transcripts :
        for index, word in enumerate(transcript) :
            l = max( [ len(t[index]) for t in transcripts] )
            print(word.ljust(l), end=' ')
        print()

def print_3_words(trans_a, trans_b, trans_c) :
    transcripts = [trans_a, trans_b, trans_c]
    transcripts = [clean.split() for _, clean in [pre.process(x) for x in transcripts]]
    transcripts = [full_align(transcripts[0], t) for t in transcripts[1:]] # at, t
    (trans_ba, trans_b), (trans_ca, trans_c) = transcripts
     
    i = 0
    while i < len(trans_ba) and i < len(trans_ca) :
        if trans_ba[i] == '' and trans_ca[i] != '' :
            trans_ca.insert(i, '')
            trans_c.insert(i, '')
        elif trans_ca[i] == '' and trans_ba[i] != '' :
            trans_ba.insert(i, '')
            trans_b.insert(i, '')
        i += 1

    while i < len(trans_ca) :
        trans_ba.append('')
        trans_b.append('')
        i += 1
    while i < len(trans_ba) :
        trans_ca.append('')
        trans_c.append('')
    i += 1

    notsure = [False] + [ True if b!=c else False for b, c in zip(trans_b, trans_c) ] + [False]
    notsure = list(zip(notsure[1:], notsure[:-1]))
    l1 = [ i for i, (x, y) in enumerate(notsure) if x and not y]
    l2 = [ i for i, (x, y) in enumerate(notsure) if y and not x]
    blocks = list(zip(l1, l2))

    for s, e in blocks :
        trans_b[s : e], trans_c[s : e] = full_align([x for x in trans_b[s : e] if x ], [x for x in trans_c[s : e] if x ])
    
    transcripts = [trans_ba, trans_b , trans_c]
    if not len(trans_ba) == len(trans_b) == len(trans_c) :
        print(len(trans_ba), trans_ba)
        print(len(trans_b), trans_b)
        print(len(trans_c), trans_c)
    for transcript in transcripts :
        for index, word in enumerate(transcript) :
            l = max( [ len(t[index]) for t in transcripts] )
            # print(word.ljust(l), end=' ')
        # print()


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
    files = [ f for f in utils.get_directory_files(manual_dir, 'txt') if (not 'Speech' in f.stem) and (not f.stem[2:6] in constants.ignore_files)]
    files = [ (f, utils.repath(f, manual_dir, automatic_dir)) for f in files]

    for manual_file, automatic_file in ChargingBar("Align Transcripts").iter(files) :
        operations_file = utils.repath(manual_file, manual_dir, destination_dir)
        align_file(manual_file, automatic_file, operations_file, write_only_operations)


def wer(operations) :
    if len(operations) == 0 :
        return 1
    return (operations.count('i') + operations.count('d') + operations.count('r')) / len(operations)


def dir_wer(manual_dir, automatic_dir) :
    files = [ f for f in utils.get_directory_files(manual_dir, 'txt') if (not 'Speech' in f.stem) and (not f.stem[2:6] in constants.ignore_files) and not f.stem in constants.controversial_files ]
    files = [ (f, utils.repath(f, manual_dir, automatic_dir)) for f in files ] 
    w = 0
    l = 0
    for manual_file, automatic_file in ChargingBar("Align Transcripts").iter(files) :
        if os.path.isfile(manual_file) and os.path.isfile(automatic_file) :
            automatic = utils.read_file(automatic_file)
            manual = ' '.join([w['word'] for w in utils.read_label_timings_from_file(manual_file)])
            _, manual = pre.process(manual)
            _, automatic = pre.process(automatic)
            operations = get_operations(manual.split(), automatic.split())
            wer_value = wer(operations)
            l += len(operations)
            w += wer_value * len(operations)
    return w / l
