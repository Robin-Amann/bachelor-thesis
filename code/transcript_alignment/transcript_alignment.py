import transcript_alignment.preprocessing as pre
import transcript_alignment.postprocessing as post
import transcript_alignment.wer_align as wer
import utils.file as utils


# operations are from hand to machine

def align_transcript(manual_source, automatic_source, operations_desination, write_only_operations=False) :
    machine_transcript_messy = utils.read_file(automatic_source)
    hand_transcript_messy = utils.read_file(manual_source)

    # cleanup
    # hand_trimmed, hand_clean = pre.process(transcript=hand_transcript_messy, patterns=["A:", "B:", "\t", "\n", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)"])
    # machine_trimmed, machine_clean = pre.process(transcript=machine_transcript_messy, additional_clean_chars="<>-")

    hand_trimmed, hand_clean = pre.process(transcript=hand_transcript_messy, patterns=["\(\(", "\)\)"])
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
    for file in files :
        print("segment", str(file))
        f = str(file)[len(manual_directory) : ]
        manual_transcript = manual_directory + f
        automatic_transcript = automatic_directory + f
        operations_desination = destination_directory + f
        align_transcript(manual_transcript, automatic_transcript, operations_desination, write_only_operations)

# alignment
# hand_snips = [hand_clean]
# machine_snips = [machine_clean]
# same_snips = [False]

# hand_snips, machine_snips, same_snips = align.align(10, hand_snips, machine_snips, same_snips)
# post.write_to_file("transcript_alignment\\results\\result1.txt", hand_snips, machine_snips)

# hand_snips, machine_snips, same_snips = align.align(6, hand_snips, machine_snips, same_snips)    
# post.write_to_file("transcript_alignment\\results\\result2.txt", hand_snips, machine_snips)
# hand_trimmed_snips = post.process(hand_snips, hand_trimmed)
# machine_trimmed_snips = post.process(machine_snips, machine_trimmed)
# post.write_to_file("transcript_alignment\\results\\fe_03_00001_alignment.txt", hand_trimmed_snips, machine_trimmed_snips)