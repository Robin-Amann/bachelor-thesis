
# General
sample_rate = 16000
manual_annotation_patterns = ['<+[^<>]*>+']

AUDIO_SEGMENT_GAP = 1 # in sec
SPEECH_GAP = 0.25       # in sec (minimum legth of audio to be counted as silence)

# Home PC 
data_base = "D:\\Robin_dataset\\Switchboard\\Example"

timing_dir = data_base + "\\Timings"
disfluencies_dir = data_base + "\\Disfluencies"
audio_dir = data_base + "\\Speech"

manual_dir = data_base + "\\Manual"
manual_seg_dir = data_base + "\\Manual_Segmented"
automatic_seg_dir = data_base + "\\Automatic_Segmented"
transcript_align_dir = data_base + "\\Manual_Automatic_Alignment"
audio_automatic_align_dir = data_base + "\\Audio_Whisper_Alignment"


# # Cluster
# data_base = "/export/data3/bachelor_theses/ramann/data/"

# timing_dir = ""
# disfluencies_dir = ""
# audio_dir = ""

# manual_dir = data_base + "Manual"
# manual_seg_dir = data_base + "Manual_Segmented"
# automatic_seg_dir = data_base + "Automatic_Segmented"
# transcript_align_dir = data_base + "Manual_Automatic_Alignment"
# audio_automatic_align_dir = data_base + "Audio_Whisper_Alignment"
