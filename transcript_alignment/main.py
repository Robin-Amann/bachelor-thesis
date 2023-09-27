import preprocessing as pre
import align as align
import postprocessing as post


if __name__ == "__main__":
    
    # read files
    machine_transcript_messy = pre.read_file("D:\\Bachelorarbeit-Code\\transcript_alignment\\transcripts\\audioclient.txt")
    hand_transcript_messy = pre.read_file("D:\\Bachelorarbeit-Code\\transcript_alignment\\transcripts\\callFriend.cha")
    
    # cleanup
    hand_trimmed, hand_clean = pre.process(
        transcript=hand_transcript_messy, 
        start="*M1:", 
        end="@End", 
        patterns=["\*M1:", "\*M2:", "\t", "\n", "[0-9]{4,6}_[0-9]{4,6}", "\([0-9]{0,2}.[0-9]{0,2}\)"], 
        trim_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ.:,;!?()[]", 
        clean_chars="abcdefghijklmnopqrstuvwxyz' ", 
        remove_space_before=".:,;!?')]", 
        remove_space_after="([" 
    )

    machine_trimmed, machine_clean = pre.process(
        transcript=machine_transcript_messy, 
        start="", 
        end="", 
        patterns=["asr:0: OUTPUT", "[0-9]+.[0-9]+-[0-9]+.[0-9]+:"], 
        trim_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ.:,;!?()[]", 
        clean_chars="abcdefghijklmnopqrstuvwxyz' <>-", 
        remove_space_before=".:,;!?')]>",
        remove_space_after="([<"
    )
    
    # alignment
    hand_snips = [hand_clean]
    machine_snips = [machine_clean]
    same_snips = [False]

    hand_snips, machine_snips, same_snips = align.align(6, hand_snips, machine_snips, same_snips)
    post.write_to_file("transcript_alignment\\alignment\\result1.txt", hand_snips, machine_snips)
    
    align.align(3, hand_snips, machine_snips, same_snips)    
    post.write_to_file("transcript_alignment\\alignment\\result2.txt", hand_snips, machine_snips)
    
    hand_trimmed_snips = post.process(hand_snips, hand_trimmed)
    machine_trimmed_snips = post.process(machine_snips, machine_trimmed)
    post.write_to_file("transcript_alignment\\alignment\\result.txt", hand_trimmed_snips, machine_trimmed_snips)