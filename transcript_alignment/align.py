
def addSnips(hand_transcript, machine_transcript, hand_snips, machine_snips, same_snips, machine_index, hand_index, compare_size) :
    if machine_index != 0 or hand_index != 0 :
        machine_snips.append(machine_transcript[ : machine_index])
        machine_transcript = machine_transcript[machine_index : ]     
        hand_snips.append(hand_transcript[ : hand_index])
        hand_transcript = hand_transcript[hand_index : ]           
        same_snips.append(False)
    machine_snips.append(machine_transcript[ : compare_size])
    machine_transcript = machine_transcript[compare_size : ]    
    hand_snips.append(hand_transcript[ : compare_size])
    hand_transcript = hand_transcript[compare_size : ]           
    same_snips.append(True)
    return hand_transcript, machine_transcript


# strings are not the same if two consecutive chars are unequal 
def compare(one, two) :
    if one == two :
        return True

    if one[-1] != two[-1] :
        return False
    
    for x in range(0, len(one) - 1) :
        if one[x] != two[x] and one[x+1] != two[x] and one[x] != two[x+1] and one[x+1] != two[x+1] :
            return False
        
    return True

    
def add_tails(hand_transcript, machine_transcript, hand_snips, machine_snips, same_snips) :
    if len(machine_transcript) > 0 or len(hand_transcript) > 0 :                 
        machine_snips.append(machine_transcript)
        machine_transcript = ""                     
        hand_snips.append(hand_transcript)
        hand_transcript = ""               
        same_snips.append(False)
    return hand_transcript, machine_transcript


def align_index_and_size(transcript, index, size) :
    # not start of a word
    while index < len(transcript) and ( (index > 0 and transcript[index - 1] != ' ') or transcript[index] == ' ' ):
        index += 1
    # shift caused out of bounds
    if index > len(transcript) - size :
        return  True, index, size
    
    # widen compare size to whole words
    #       last character is not already ' '            next character exists
    while transcript[index + size - 1] != ' ' and index + size + 1 <= len(transcript)  :   
        size += 1
    
    return  False, index, size


def align_transcript(base_compare_size, hand_transcript, machine_transcript) :

    hand_snips = []
    machine_snips = [] 
    same_snips = []

    # compare
    machine_index = 0

    while machine_index <= len(machine_transcript) - base_compare_size :
        
        # configure variables
        compare_size = base_compare_size
        hit = False
        hand_index = 0                       # hand window always has index 0

        # move machine to next word and expand compare size to full word
        out_of_bounds, machine_index, compare_size = align_index_and_size(machine_transcript, machine_index, compare_size)   
        if out_of_bounds :
            hand_transcript, machine_transcript = add_tails(hand_transcript, machine_transcript, hand_snips, machine_snips, same_snips)
            return hand_snips, machine_snips, same_snips

        # configure window size
        window_size = 8 * compare_size + machine_index
        if window_size > len(hand_transcript) :             
            window_size = len(hand_transcript)
            if window_size < compare_size :                
                hand_transcript, machine_transcript = add_tails(hand_transcript, machine_transcript, hand_snips, machine_snips, same_snips)
                return hand_snips, machine_snips, same_snips

        # while hand is within window
        while hand_index + compare_size <= window_size:

            # move hand to next word
            out_of_bounds, hand_index, t = align_index_and_size(hand_transcript, hand_index, compare_size)
            if out_of_bounds :
                break
            
            if compare(machine_transcript[machine_index : machine_index + compare_size], hand_transcript[hand_index : hand_index + compare_size]) :
                # incease compare size till comparison fails
                hit = True
                while True :    
                    # expand compar size (machine index won't change)
                    out_of_bounds, machine_index, temp_compare_size = align_index_and_size(machine_transcript, machine_index, compare_size + 1)
                    if out_of_bounds or hand_index > len(hand_transcript) - temp_compare_size :  # out of bounce for both transcripts
                        break

                    if compare(machine_transcript[machine_index : machine_index + temp_compare_size], hand_transcript[hand_index : hand_index + temp_compare_size]) :
                        compare_size = temp_compare_size
                    else :
                        break
                
                # add similar transcripts
                hand_transcript, machine_transcript = addSnips(hand_transcript, machine_transcript, hand_snips, machine_snips, same_snips, machine_index, hand_index, compare_size)
                machine_index = 0
                hand_index = 0

                break
            else :   
                hand_index += 1
        
        if not hit :
            machine_index += 1
    
    hand_transcript, machine_transcript = add_tails(hand_transcript, machine_transcript, hand_snips, machine_snips, same_snips)

    return hand_snips, machine_snips, same_snips


def align(base_compare_size, hand_snips, machine_snips, same_snips) :
    
    for i in reversed( range( len(hand_snips) ) ) :
        if same_snips[i] or len(hand_snips[i]) == 0 or len(machine_snips[i]) == 0 :
            continue
        else :
            hand_snips_temp, machine_snips_temp, same_snips_temp = align_transcript(base_compare_size, hand_snips[i], machine_snips[i])                
            hand_snips[i:i+1] = hand_snips_temp
            machine_snips[i:i+1] = machine_snips_temp
            same_snips[i:i+1] = same_snips_temp
    
    return hand_snips, machine_snips, same_snips