import torch
import torchaudio
import utils.file as utils
import tasks.audio_transcript_alignment.ctc as ctc
from progress.bar import ChargingBar
import os
import utils.constants as constants
import utils.transcript as word_utils
from pathlib import Path

import tasks.audio_transcript_alignment.visualization as visual

# sw2749A018
audio_file = Path('D:/Robin_dataset/Switchboard/LDC97S62 Switchboard-1 Release 2/09/SWB1/sw02749A.wav')
sample_rate = 16000
transcript_file = Path('D:/Robin_dataset/Switchboard Computed/manual/segmented/27/2749/A/sw2749A018.txt')
start= int(414.627625 * sample_rate)
end= int(417.817625 * sample_rate)

SPEECH_FILE = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript = "|I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT|"
# transcript = "|I|HAD|THAT|CURIOSITY|AT|THIS|MOMENT|"

with torch.inference_mode():
    audio, _ = torchaudio.load(SPEECH_FILE)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_args = {'model_dir' : str(constants.model_dir / 'wav2vec2')}
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
model = bundle.get_model(dl_kwargs=model_args).to(device)
wav2vec2_model = (bundle, model)


# audio = utils.read_audio(audio_file, sample_rate)  # [ [...] ]
# audio = audio[:, start : end]

# import matplotlib.pyplot as plt

# fig, ax = plt.subplots(tight_layout=True, figsize=(20, 3))
# ax.plot(audio[0])
# ax.set_xticks([])
# secax = ax.secondary_xaxis('bottom', functions=(lambda x : x / sample_rate, lambda x : x * sample_rate))
# secax.set_xlabel('time [second]')

# ax.set_yticks([])
# ax.set_ylim(-1.0, 1.0)
# ax.set_xlim(0, audio.size(-1))
# plt.show()

# original_transcript = ' '.join([ w['word'] for w in utils.read_dict(transcript_file)])
# transcript = original_transcript.split()
# simple = [ word_utils.simplify(w) for w in transcript ]

# transcript = '|' + '|'.join(simple).upper() + '|'

labels, emission = ctc.get_emission(audio, device, wav2vec2_model)
words, trellis_width = ctc.ctc(emission, transcript, labels, whitespace_stay_default_value=-1)
trellis, tokens = ctc.get_trellis(emission, transcript, labels, whitespace_stay_default_value=-1)

# visual.plot_trellis(trellis)
# visual.plot_trellis_with_path(trellis, path)
visual.plot_alignments(trellis, words, audio[0], sample_rate)