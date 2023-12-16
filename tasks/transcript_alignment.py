import utils.file as utils
from progress.bar import ChargingBar
import tasks.transcript_cleanup as pre
import utils.wer_alignment as wer_utils


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
    machine_transcript_messy = ' '.join([w['word'] for w in utils.read_dict(automatic_source)])
    hand_transcript_messy = ' '.join([w['word'] for w in utils.read_dict(manual_source)])
    hand_trimmed, hand_clean = pre.process(transcript=hand_transcript_messy)
    machine_trimmed, machine_clean = pre.process(transcript=machine_transcript_messy)
    operations = wer_utils.get_operations(hand_clean.split(), machine_clean.split())    # list of {n, i, d, r}
    if write_only_operations :
        utils.write_file(operations_desination, ' '.join(operations))
    else :
        hand_snips, machine_snips = wer_utils.align(hand_trimmed.split(), machine_trimmed.split(), operations)
        write_to_file_wer(operations_desination, hand_snips, machine_snips, 30)


def align_dir(manual_dir, automatic_dir, destination_dir, write_only_operations=False) :
    files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir]) #, filter_condition= lambda f : not f.stem[2:6] in constants.ignore_files )

    for manual_file, automatic_file in ChargingBar("Align Transcripts").iter(files) :
        operations_file = utils.repath(manual_file, manual_dir, destination_dir)
        align_file(manual_file, automatic_file, operations_file, write_only_operations)


