import preprocessing as pre
import align as align
import wer_align as wer
import postprocessing as post


if __name__ == "__main__":
    
    # read files
    machine_transcript_messy = pre.read_file("D:\\Robin_dataset\\fisher english\\whisper transcript\\000\\fe_03_00003.txt")
    hand_transcript_messy = pre.read_file("D:\\Robin_dataset\\fisher english\\training transcripts 1\\data\\trans\\000\\fe_03_00003.txt")
    
    # cleanup
    hand_trimmed, hand_clean = pre.process(
        transcript=hand_transcript_messy, 
        start="B: ", 
        end="", 
        patterns=["A:", "B:", "\t", "\n", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)"], 
    )

    machine_trimmed, machine_clean = pre.process(
        transcript=machine_transcript_messy,
        additional_clean_chars="<>-",
    )
    
    # alignment
    hand_snips = [hand_clean]
    machine_snips = [machine_clean]
    same_snips = [False]

    hand_snips, machine_snips, same_snips = align.align(10, hand_snips, machine_snips, same_snips)
    post.write_to_file("transcript_alignment\\results\\result1.txt", hand_snips, machine_snips)
    
    hand_snips, machine_snips, same_snips = align.align(6, hand_snips, machine_snips, same_snips)    
    post.write_to_file("transcript_alignment\\results\\result2.txt", hand_snips, machine_snips)
    hand_trimmed_snips = post.process(hand_snips, hand_trimmed)
    machine_trimmed_snips = post.process(machine_snips, machine_trimmed)
    post.write_to_file("transcript_alignment\\results\\result.txt", hand_trimmed_snips, machine_trimmed_snips)
    
    operations = wer.get_operations(hand_clean.split(" "), machine_clean.split(" "))
    hand_snips, machine_snips = wer.align(hand_trimmed.split(" "), machine_trimmed.split(" "), operations)
    post.write_to_file_wer("transcript_alignment\\results\\result_wer.txt", hand_snips, machine_snips, 30)