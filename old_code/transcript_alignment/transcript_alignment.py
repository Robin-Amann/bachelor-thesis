import tasks.transcript_alignment.preprocessing as pre
import tasks.transcript_alignment.postprocessing as post
import tasks.transcript_alignment.wer_align as wer
import utils.file as utils
from progress.bar import ChargingBar
import utils.constants as constants
from pathlib import Path

# operations are from hand to machine

def align_transcript(manual_source, automatic_source, operations_desination, write_only_operations=False) :
    machine_transcript_messy = utils.read_file(automatic_source)
    hand_transcript_messy = utils.read_file(manual_source)

    # cleanup
    # hand_trimmed, hand_clean = pre.process(transcript=hand_transcript_messy, patterns=["A:", "B:", "\t", "\n", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)"])
    # machine_trimmed, machine_clean = pre.process(transcript=machine_transcript_messy, additional_clean_chars="<>-")

    hand_trimmed, hand_clean = pre.process(transcript=hand_transcript_messy, patterns=constants.manual_trim_patterns)
    machine_trimmed, machine_clean = pre.process(transcript=machine_transcript_messy)

    # wer alignment
    operations = wer.get_operations(hand_clean.split(), machine_clean.split())    # list of {n, i, d, r}
    
    if write_only_operations :
        utils.write_file(operations_desination, ' '.join(operations))
    else :
        hand_snips, machine_snips = wer.align(hand_trimmed.split(), machine_trimmed.split(), operations)
        post.write_to_file_wer(operations_desination, hand_snips, machine_snips, 30)

def align_directory(manual_directory, automatic_directory, destination_directory, write_only_operations=False) :
    files = utils.get_directory_files(manual_directory, "txt")
    # file = source + parent + (stem + suffix = name)
    for file in ChargingBar("Align Transcripts").iter(files) :
        f = str(file)[len(manual_directory) : ]
        manual_transcript = manual_directory + f
        automatic_transcript = automatic_directory + f
        operations_desination = destination_directory + f
        align_transcript(manual_transcript, automatic_transcript, operations_desination, write_only_operations)


def sb_align_transcript(manual_source, automatic_source, operations_desination, write_only_operations=False) :
    machine_transcript_messy = utils.read_file(automatic_source)
    hand_transcript_messy = ' '.join([w['word'] for w in utils.read_label_timings_from_file(manual_source)])
    hand_trimmed, hand_clean = pre.process(transcript=hand_transcript_messy)
    machine_trimmed, machine_clean = pre.process(transcript=machine_transcript_messy)

    operations = wer.get_operations(hand_clean.split(), machine_clean.split())    # list of {n, i, d, r}
    if write_only_operations :
        utils.write_file(operations_desination, ' '.join(operations))
    else :
        hand_snips, machine_snips = wer.align(hand_trimmed.split(), machine_trimmed.split(), operations)
        post.write_to_file_wer(operations_desination, hand_snips, machine_snips, 30)


def sb_align_directory(manual_dir, automatic_dir, destination_dir, write_only_operations=False) :
    manual_files = [ (f.stem, f) for f in utils.get_directory_files(manual_dir, "txt") if not 'Speech' in f.stem ]
    automatic_files = [ (f.stem, f) for f in utils.get_directory_files(automatic_dir, "txt") ]
    stub = len(Path(manual_dir).parts)
    for stem, manual_file in ChargingBar("Align Transcripts").iter(manual_files) :
        automatic_file = next(f for s, f in automatic_files if s == stem)
        operations_file = Path(destination_dir) / Path('/'.join(list(manual_file.parts[stub : ])))
        sb_align_transcript(manual_file, automatic_file, operations_file, write_only_operations)