from pathlib import Path
import utils.ignore_files as ignore

# General
sample_rate = 16000
# preprocessing
manual_annotation_patterns = ['<+[^<>]*>+', '``/``', "''/''"]

# number of ignore-files:         102
# number of controversial-files: 2484
# dataset (16.12.23):	                    number of files   total             name                    object								                                
# data_base				                                                        data_base
# ├ manual									                                                                    
# │ ├ long									2062              2230              manual_dir              word, annotation, pause_type, is_restart, start, end				
# │ └ segmented								2062 | 36837      2062 | 39321      manual_seg_dir          start, end | word, annotation, pause_type, is_restart, start, end	   (39321 = 36837 + 2484)
# └ automatic								                                                                    
#   ├ unaligned								36837                               automatic_dir           text																
#   ├ aligned								36837             43418             automatic_align_dir     word, start, end, score                                             
#   ├ version3								6187              6628              automatic_v3_dir        word, start, end													
#   └ retranscribed						                      100584            retranscibed_dir
#     ├ whisper								6187                                                        word, start, end													
#     ├ wav2vec2							36837                                                       word, start, end													
#     ├ wav2vec2_LM							36837                                                       word, start, end													
#     ├ wav2vec2_custom_LM 					6187                                                        word, start, end													
#     ├ wav2vec2_custom_LM_hesitations		6187                                                        word, start, end													
#     └ wav2vec2_custom_LM_hesitations_new	8349                                                        word, start, end
# files that are not in ignore_files or contoversial_files can be read with read_dict(path)


# Home PC 
data_base = Path("D:\\Robin_dataset\\Switchboard Computed")

timing_dir = Path("D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts\\word alignments")
disfluencies_dir = Path("D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd") 
audio_dir = Path("D:\\Robin_dataset\\Switchboard\\LDC97S62 Switchboard-1 Release 2") 


# # Cluster
# data_base = Path("/export/data3/bachelor_theses/ramann/data")

# timing_dir = data_base / "Switchboard-1 Release 2 Transcripts"
# disfluencies_dir = Path("/project/data_asr/LDC/LDC99T42/treebank_3/dysfl/mgd/swbd")
# audio_dir = Path("/project/data_asr/LDC/LDC97S62")


# # General
manual_dir = data_base / 'manual' / 'long'
manual_seg_dir = data_base / 'manual' / 'segmented'
automatic_dir = data_base / 'automatic' / 'unaligned' / 'correct'
automatic_align_dir = data_base / 'automatic' / 'aligned'                       
automatic_v3_dir = data_base / 'automatic' / 'aligned' / 'version3'
classification_dir = data_base / 'automatic' / 'classification'
retranscibed_dir = data_base / 'automatic' / 'retranscribed'


model_dir = Path('data/models')
error_dir = Path('data/supervised_data_preperation/errors')
hesitations_file = Path('data/data_preperation/hesitations/hesitations.txt')

ignore_files = ignore.ignore_files
controversial_files = ignore.controversial_files