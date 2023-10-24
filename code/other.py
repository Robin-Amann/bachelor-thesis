import utils.statistics as statistics
import utils.file as utils


transcript_dir =           "D:\\Robin_dataset\\fisher english\\transcripts segmented\\training transcripts 1\\data\\trans\\000"
whisper_dir =              "D:\\Robin_dataset\\fisher english\\whisper segmented\\training transcripts 1\\data\\trans\\000"
transcript_alignment_dir = "D:\\Robin_dataset\\fisher english\\whisper manual segmented aligned\\training transcripts 1\\data\\trans\\000"

# statistics.hesitation_translation(transcript_dir, whisper_dir, transcript_alignment_dir)

# from manual to whisper
# word hesitation nothing commentary
#   whisper
# m [152087, 164,  12321, 0]
# a [1488,   2404, 3603,  0]
# n [5366,   189,  0,     0]
# u [416,    65,   1399,  0]
# a
# l


# vocabulary = utils.read_vocabulary('code\\sample_data\\vocabulary\\vocabulary_manual\\vocabulary.txt')
# for w, c in vocabulary.items() :
#     if "'" in w and c >= 10:
#         print(w, c)

statistics.vocabulary_set_statistic('code\\sample_data\\vocabulary\\vocabulary_manual_small')
# statistics.vocabulary_set_statistic('code\\sample_data\\vocabulary\\vocabulary_whisper')

# new_hes = utils.read_vocabulary('code\\sample_data\\vocabulary\\vocabulary_manual_small\\hesitations.txt')
# hes = utils.read_vocabulary('code\\sample_data\\vocabulary\\vocabulary_manual\\hesitations_by_eye.txt')

# new_hes = { k:v for k, v in new_hes.items() if k in hes.keys() }
# utils.write_vocabulary('code\\sample_data\\vocabulary\\vocabulary_manual_new\\hesitations_by_eye.txt', new_hes)