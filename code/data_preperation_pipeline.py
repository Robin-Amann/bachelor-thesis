import tasks.vocabulary_extraction as vocabulary_extraction
import tasks.audio_segmentation as segmentation
import tasks.audio_transcription as transcriptor
import tasks.transcript_normalization as normalizer
import tasks.transcript_alignment.transcript_alignment as transcript_alignment
import tasks.audio_transcript_alignment.audio_transcript_alignment as audio_transcript_alignment
import tasks.audio_labeling as labeling

# constants
sample_rate = 16000

# directories   
# speech_dir and transcript_dir need to mirror each other in stucture and filenames (except file extentions obiously)
transcript_dir =                 "D:\\Robin_dataset\\fisher english\\transcripts\\training transcripts 1\\data\\trans\\000"
speech_dir =                     "D:\\Robin_dataset\\fisher english\\speech\\training speech 1\\d1\\audio\\000"

segmented_speech_dir =           "D:\\Robin_dataset\\fisher english\\speech segmented\\training speech 1\\d1\\audio\\000"
segmented_transcript_dir =       "D:\\Robin_dataset\\fisher english\\transcripts segmented\\training transcripts 1\\data\\trans\\000"
whisper_dir =                    "D:\\Robin_dataset\\fisher english\\whisper segmented\\training transcripts 1\\data\\trans\\000"
transcript_alignment_dir =       "D:\\Robin_dataset\\fisher english\\whisper manual segmented aligned\\training transcripts 1\\data\\trans\\000"
audio_transcript_alignment_dir = "D:\\Robin_dataset\\fisher english\\audio manual segmented aligned\\training transcripts 1\\data\\trans\\000"


# vocabulary_extraction.get_vocabulary_set(
#     source_directory=transcript_dir,
#     destination_directory="code\\sample_data\\vocabulary\\vocabulary_manual_small", 
#     patterns=["# Transcribed at the LDC", "# fe_[0-9]{2}_[0-9]{5}.sph", "A:", "B:", "\t", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)", '\.', ',', '!', '\?']
# )
# vocabulary_extraction.get_vocabulary_set(
#     source_directory="D:\\Robin_dataset\\fisher english\\transcripts", 
#     destination_directory="code\\sample_data\\vocabulary\\vocabulary_manual", 
#     patterns=["# Transcribed at the LDC", "# fe_[0-9]{2}_[0-9]{5}.sph", "A:", "B:", "\t", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)", '\.', ',', '!', '\?']
#     )
# vocabulary_extraction.get_vocabulary_set(
#     source_directory=whisper_dir, 
#     destination_directory="code\\sample_data\\vocabulary\\vocabulary_whisper", 
#     patterns=['\.', ',', '!', '\?']
#     )       # 좋아요<|ko|> was in whisper vocabulary


segmentation.segment_directory(speech_dir, transcript_dir, segmented_speech_dir, segmented_transcript_dir, sample_rate)
transcriptor.transcribe_dir(segmented_speech_dir, whisper_dir, 'whisper')
normalizer.normalize_directory(segmented_transcript_dir)
normalizer.normalize_directory(whisper_dir)
transcript_alignment.align_directory(segmented_transcript_dir, whisper_dir, transcript_alignment_dir, True)
audio_transcript_alignment.align_directory(segmented_speech_dir, segmented_transcript_dir, audio_transcript_alignment_dir, sample_rate)
labeling.label_directory(segmented_speech_dir, audio_transcript_alignment_dir, sample_rate)


