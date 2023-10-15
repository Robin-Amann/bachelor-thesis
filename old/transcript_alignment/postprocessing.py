def write_to_file(path, hand_snips, machine_snips) :
    with open(path, 'w') as file :
        for i in range(len(machine_snips)) :
            file.write("Machine: " + machine_snips[i] + "\n")
            file.write("Hand:    " + hand_snips[i] + "\n\n")

def process(snips, trimmed) :
    trimmed = trimmed.split()
    trimmed_snips = []
    base = 0
    for s in snips :
        trimmed_snips.append( " ".join(trimmed[base : base + len(s.split())]) )
        base += len(s.split())
    return trimmed_snips