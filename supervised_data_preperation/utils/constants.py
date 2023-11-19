from pathlib import Path

# General
sample_rate = 16000
manual_annotation_patterns = ['<+[^<>]*>+', '``/``', "''/''"]

AUDIO_SEGMENT_GAP = 1 # in sec
SPEECH_GAP = 0.25       # in sec (minimum legth of audio to be counted as silence)
ALLOWED_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "abcdefghijklmnopqrstuvwxyz" + "0123456789" + " '.,:;!?-" + "\"$%&*") # "ÄÖÜäöüáéíóúñ" 

ignore_files = ['2945', '2930', '2937', '2965', '2909', '2959', '2914', '2935', '4379', '2957', '2923', '2289', '2926', '2963']  # file numbers that are corrupt or missing

# # Home PC 
data_base = Path("D:\\Robin_dataset\\Switchboard\\Example")

timing_dir = data_base / "Timings"
disfluencies_dir = data_base / "Disfluencies"
audio_dir = data_base / "Speech"

model_dir = Path('supervised_data_preperation/data/models')
error_dir = Path('supervised_data_preperation/data/errors')
hesitations_file = Path('supervised_data_preperation/data/hesitations/hesitations.txt')


# # Cluster
# data_base = Path("/export/data3/bachelor_theses/ramann/data_new")

# timing_dir = data_base / "Switchboard-1 Release 2 Transcripts"
# disfluencies_dir = Path("/project/data_asr/LDC/LDC99T42/treebank_3/dysfl/mgd/swbd")
# audio_dir = Path("/project/data_asr/LDC/LDC97S62")

# model_dir = Path('data/models')
# error_dir = Path('data/errors')
# hesitations_file = Path('data/hesitations/hesitations.txt')

# General
manual_dir = data_base / "Manual"
manual_seg_dir = data_base / "Manual_Segmented"
automatic_seg_dir = data_base / "Automatic_Segmented"
transcript_align_dir = data_base / "Manual_Automatic_Alignment"
audio_automatic_align_dir = data_base / "Audio_Whisper_Alignment"

