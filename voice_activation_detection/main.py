import torch
from pprint import pprint
import torchaudio
import matplotlib
import matplotlib.pyplot as plt

def plot_speech_samples(wav, speech_timestamps, sample_rate) :
    matplotlib.rcParams["figure.figsize"] = [12, 4.8]
    plt.plot(wav)
    for timestamp in speech_timestamps:
        x1, x0 = timestamp.values()
        plt.axvspan(x0, x1, alpha=0.1, color="red")     # add vertical rectangle
    plt.xlabel("time [second]")
    plt.xlim(0, wav.size(-1))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    sec = int(len(wav)/sample_rate)
    plt.xticks([sample_rate * i for i in range(sec+1)], list(range(sec+1)))
    plt.show()

# preparation
torch.set_num_threads(1)
AUDIO_PATH = "voice_activation_detection\\10s.wav"
SAMPLING_RATE = torchaudio.info(AUDIO_PATH).sample_rate     # 8000, 16000 are ok
print(SAMPLING_RATE)
USE_ONNX = False # change this to True if you want to test onnx model

# load model  
# UserWarning: You are about to download and run code from an untrusted repository. In a future release, this won't be allowed. 
# To add the repository to your trusted list, change the command to {calling_fn}(..., trust_repo=False) and a command prompt will appear asking for an explicit confirmation of trust, or load(..., trust_repo=True), 
# which will assume that the prompt is to be answered with 'yes'. You can also use load(..., trust_repo='check') which will only prompt for confirmation if the repo is not already trusted. This will eventually be the default behaviour
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True, onnx=USE_ONNX)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
wav = read_audio(AUDIO_PATH, sampling_rate=SAMPLING_RATE)   # tensor with timestampe

# get speech timestamps from full audio file
speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=SAMPLING_RATE)
print(type(speech_timestamps[0]))
pprint(speech_timestamps)

plot_speech_samples(wav, speech_timestamps, SAMPLING_RATE)

# merge all speech chunks to one audio
# save_audio('voice_activation_detection\\only_speech.wav', collect_chunks(speech_timestamps, wav), sampling_rate=SAMPLING_RATE) 

