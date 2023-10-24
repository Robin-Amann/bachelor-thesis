import utils.file as utils
import tasks.transcript_alignment.preprocessing as pre
import tasks.transcript_alignment.wer_align as alignment
from progress.bar import ChargingBar


print(12345678)
print(f'{45678: 08,}')


# combine hesitations
# hesitations = list( utils.read_vocabulary('code\\sample_data\\vocabulary\\vocabulary_manual\\hesitations_by_eye.txt').keys() )
# vocabulary = list( utils.read_vocabulary('code\\sample_data\\vocabulary\\vocabulary_manual\\vocabulary.txt').keys() )
# whisper_hesitations = list( utils.read_vocabulary('code\\sample_data\\vocabulary\\vocabulary_whisper\\hesitations_by_eye.txt').keys() )
# whisper_vocabulary = list( utils.read_vocabulary('code\\sample_data\\vocabulary\\vocabulary_whisper\\vocabulary.txt').keys() )
# # for h in hesitations :
# #     if h not in whisper_hesitations and h in whisper_vocabulary :
# #         print(h)
# # for h in whisper_hesitations :
# #     if h not in hesitations and h in vocabulary :
# #         print(h)
# hes = set(hesitations + whisper_hesitations)
# print(hes)
# utils.write_file('code\\sample_data\\vocabulary\\hesitations.txt', '\n'.join(hes))

# # delete files
# import utils.file as utils
# import os
# files = utils.get_directory_files(segmented_transcript_dir, 'txt')
# for file in files :
#     f = str(file)
#     content = utils.read_file(f)
#     if not any(c.isalpha() for c in content) :
#         print(file, content)
#         os.remove(f)       # transcript
#         os.remove(segmented_speech_dir + f[len(segmented_transcript_dir) : - 4] + '.wav')   # audio
#         os.remove(whisper_dir + f[len(segmented_transcript_dir) : - 4] + '.txt')    # whisper transcript
#         os.remove(transcript_alignment_dir + f[len(segmented_transcript_dir) : - 4] + '.txt')    # whisper transcript