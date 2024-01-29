import utils.file as utils
import utils.constants as c
import utils.wer_alignment as alignment
from progress.bar import ChargingBar
import utils.transcript as word_utils
import utils.console as console

# retranscribe_dirs = [c.retranscibed_dir / 'whisper_large', c.retranscibed_dir / 'wav2vec2', c.retranscibed_dir / 'wav2vec2_LM', c.retranscibed_dir / 'wav2vec2_custom_LM', c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations']

# for d in retranscribe_dirs :
#     files = utils.get_dir_files(d)
#     print(len(files))


files = utils.get_dir_files(c.retranscibed_dir / 'wav2vec2' )

for file in files :
    x = utils.read_dict(file)
    utils.write_dict(file, x)