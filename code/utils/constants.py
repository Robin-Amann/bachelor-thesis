
sample_rate = 16000

fe_transcripts = "D:\\Robin_dataset\\fisher english\\transcripts"

transcript_dir = "D:\\Robin_dataset\\fisher english\\transcripts\\training transcripts 1\\data\\trans\\000"
speech_dir =     "D:\\Robin_dataset\\fisher english\\speech\\training speech 1\\d1\\audio\\000"

segmented_speech_dir =           "D:\\Robin_dataset\\fisher english\\speech segmented\\training speech 1\\d1\\audio\\000"
segmented_transcript_dir =       "D:\\Robin_dataset\\fisher english\\transcripts segmented\\training transcripts 1\\data\\trans\\000"
whisper_dir =                    "D:\\Robin_dataset\\fisher english\\whisper segmented\\training transcripts 1\\data\\trans\\000"
transcript_alignment_dir =       "D:\\Robin_dataset\\fisher english\\whisper manual segmented aligned\\training transcripts 1\\data\\trans\\000"
audio_transcript_alignment_dir = "D:\\Robin_dataset\\fisher english\\audio manual segmented aligned\\training transcripts 1\\data\\trans\\000"

hesitations = 'code\\data\\vocabulary\\hesitations_by_eye.txt'
english_most_common = 'code\\data\\vocabulary\\english_most_commen_5000.txt'

vocabulary_manual_dir = 'code\\data\\vocabulary\\vocabulary_manual'
vocabulary_manual_000_dir = 'code\\data\\vocabulary\\vocabulary_manual_small'
vocabulary_whisper_000_dir = 'code\\data\\vocabulary\\vocabulary_whisper'

error_dir = 'code\\data\\errors'

manual_trim_patterns = ["\(\(", "\)\)", '\[laughter\]', '\[noise\]', '\[sigh\]', '\[lipsmack\]', '\[cough\]', '\[laugh\]', '\[breath\]', '\[pause\]', '\[\[skip\]\]', '\[sigh\]-',  '\[laughter\]-', '\[sneeze\]']
