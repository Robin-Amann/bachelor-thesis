import transcript_alignment.preprocessing as pre
import transcript_alignment.postprocessing as post
import transcript_alignment.wer_align as wer
import utils.file as loader


machine_transcript_messy = loader.read_file("code\\sample_data\\whisper_fe_03_00001.txt")
hand_transcript_messy = loader.read_file("code\\sample_data\\manual_fe_03_00001.txt")

# cleanup
hand_trimmed, hand_clean = pre.process(
    transcript=hand_transcript_messy, 
    start="A:",
    patterns=["A:", "B:", "\t", "\n", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)"], 
)
machine_trimmed, machine_clean = pre.process(
    transcript=machine_transcript_messy,
    additional_clean_chars="<>-",
)

# wer alignment
operations = wer.get_operations(hand_clean.split(" "), machine_clean.split(" "))
hand_snips, machine_snips = wer.align(hand_trimmed.split(" "), machine_trimmed.split(" "), operations)
post.write_to_file_wer("code\\sample_data\\aligned_manual_whisper_fe_03_00001.txt", hand_snips, machine_snips, 30)







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
