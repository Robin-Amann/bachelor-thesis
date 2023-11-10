def write_to_file(path, hand_snips, machine_snips) :
    with open(path, 'w') as file :
        for i in range(len(machine_snips)) :
            file.write("Machine: " + machine_snips[i] + "\n")
            file.write("Hand:    " + hand_snips[i] + "\n\n")


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


def process(snips, trimmed) :
    trimmed = trimmed.split()
    trimmed_snips = []
    base = 0
    for s in snips :
        trimmed_snips.append( " ".join(trimmed[base : base + len(s.split())]) )
        base += len(s.split())
    return trimmed_snips