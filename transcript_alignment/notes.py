# Model :
#
# machine-transcript:   you don't want to be recorded oh i don't care all right so uh this is for the university of pennsylvania uh and we've got thirty minutes to talk talk yeah we've got to talk thirty minutes <noise> all right well <noise> i know i'm here i'm here uh i say i i say i know i'm traveling with a pro here okay now
# machine:                        ----------
# machine_compare_index - 
# Hand-transcript:      you don't want to be recorded oh i don't care hhh  all right so ah this is for the university of pensylvannia hhh oh i i still don't mind oh and we've got thirty minutes to talk we've thirty minutes to talk oh ok yeah we've got to talk thirty minutes alright well hhh &=cough er do you have that time i i know i'm i'm prattling with a pro here huh i say i know i'm prattling with a pro here hhh o:kay hhh now
# hand_window           -------------------------------- 
# hand                     ----------  
# hand_compare_index    -


# By hand (10 char equal except single swaps / skips): 
# Machine:  you don't want to be recorded oh i don't care |     | all right so uh this is for the university of pennsylvania | uh                             | and we've got thirty minutes to talk | talk                               | yeah we've got to talk thirty minutes | <noise> all right well <noise>                      | i know i'm | here i'm                 | here uh i say i  | i say i | know i'm traveling with a pro here |     | okay  |     | now
# Hand:     you don't want to be recorded oh i don't care | hhh | all right so ah this is for the university of pensylvannia | hhh oh i i still don't mind oh | and we've got thirty minutes to talk | we've thirty minutes to talk oh ok | yeah we've got to talk thirty minutes | alright well hhh &=cough er do you have that time i | i know i'm | i'm prattling with a pro | here huh i say i |         | know i'm prattling with a pro here | hhh | o:kay | hhh | now

# by character:
# Machine:  ["you don't want to be recorded oh i don't care ", 'hhh  ', 'all right so ', 'ah this is for the university of pen', 'sylvannia ', "hhh oh i i still don't mind ", "oh and we've got thirty minutes to talk ", "we've thirty minute", 's to talk ', "oh ok yeah we've got to talk ", 'thirty minutes ', '',           'alright well ', 'hhh &=cough er do you have that time ', "i i know i'm ", "i'm prattling with a pr", 'o here h', 'u',       "h i say i know i'm ", 'prat', 'tling with a pro here ', 'hhh o:kay hhh now']
# Hand:     ["you don't want to be recorded oh i don't care ", '',      'all right so ', 'uh this is for the university of pen', 'nsylvania ', '',                             "uh and we've got thirty minutes to talk ", "talk yeah we've go",  't to talk ', '',                              'thirty minutes ', '<noise> al', 'l right well ', '<noise',                                "> i know i'm ", "here i'm",                ' here uh', ' i say ', "i i say i know i'm ", 'trav', 'eling with a pro here ', 'okay now']

# by word:
# Machine:  ["you don't want to be recorded oh i don't care ", '    ', 'all right so uh this is for the university of pennsylvania ', '                            ', "uh and we've got thirty minutes to talk ", 'talk                               ', "yeah we've got to talk thirty minutes ", '<noise> all right well <noise>                      ', "i know i'm ", "here i'm here uh                  ", 'i say i ', 'i say i ', "know i'm ", 'traveling ', 'with a pro here ', 'okay now']
# Hand:     ["you don't want to be recorded oh i don't care ", 'hhh ', 'all right so ah this is for the university of pensylvannia ', "hhh oh i i still don't mind ", "oh and we've got thirty minutes to talk ", "we've thirty minutes to talk oh ok ", "yeah we've got to talk thirty minutes ", ' hhh &=cough er do you have that time i ', "i know i'm ", "i'm prattling with a pro here huh ", 'i say i ', '        ', "know i'm ", 'prattling ', 'with a pro here ', 'hhh o:kay hhh now']
#
# Machine:  you don't want to be recorded oh i don't care  |      | all right so uh this is for the university of pennsylvania  |                              | uh and we've got thirty minutes to talk  | talk                                | yeah we've got to talk thirty minutes  | <noise> all right well <noise>                       | i know i'm  | here i'm here uh                   | i say i  | i say i  | know i'm  | traveling  | with a pro here  | okay now          |
# Hand:     you don't want to be recorded oh i don't care  | hhh  | all right so ah this is for the university of pensylvannia  | hhh oh i i still don't mind  | oh and we've got thirty minutes to talk  | we've thirty minutes to talk oh ok  | yeah we've got to talk thirty minutes  | alright well hhh &=cough er do you have that time i  | i know i'm  | i'm prattling with a pro here huh  | i say i  |          | know i'm  | prattling  | with a pro here  | hhh o:kay hhh now |



# def align_by_character() : 
#     global machine_transcript, hand_transcript, hand_snips, machine_snips, same_snips, compare_size, window_size
#     # compare

#     machine_compare_index = 0
#     compare_size = 8
#     print("Start")
#     while machine_compare_index <= len(machine_transcript) - compare_size :

#         hit = False
#         hand_compare_index = 0
#         # hand window always has index 0
                                               
#         window_size = 4 * compare_size
#         if window_size > len(hand_transcript) :             
#             window_size = len(hand_transcript)
#             if window_size < compare_size :                 
#                 machine_snips.append(machine_transcript)
#                 machine_transcript = ""                     
#                 hand_snips.append(hand_transcript)
#                 hand_transcript = ""               
#                 same_snips.append(False)
#                 return

#             print("window changed. new size: ", window_size)

#         while hand_compare_index <= window_size - compare_size :
#             if compare(machine_transcript[machine_compare_index : machine_compare_index + compare_size], hand_transcript[hand_compare_index : hand_compare_index + compare_size]) :
#                 # incease compare size till comparison fails
#                 extended_size = compare_size
#                 while machine_compare_index + (extended_size + 1) <= len(machine_transcript) and hand_compare_index + (extended_size + 1) <= len(hand_transcript) : 

#                     if compare(machine_transcript[machine_compare_index : machine_compare_index + extended_size + 1], hand_transcript[hand_compare_index : hand_compare_index + extended_size + 1]) :
#                         extended_size += 1
#                     else :
#                         break
#                 addSnips(machine_compare_index, hand_compare_index, extended_size)
#                 machine_compare_index = 0
#                 hand_compare_index = 0
#                 hit = True


#                 break
#             else :   
#                 hand_compare_index += 1
        
#         if not hit :
#             machine_compare_index += 1

#     print(machine_snips)
#     print(hand_snips)
#     print(same_snips)