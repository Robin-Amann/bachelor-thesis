import torch
import data.load_audio as audio

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
audio_file = ""
sample_rate = "16000"

# load audio
waveform = audio.load(audio_file, sample_rate)

# create transcript (whisper / audioclient) or load manual transcript
transcript = ""
manual_transcript = ""

# perform ctc alignment


# perform voice activation

# get untranscribed audio fragments

# perform prediction model to search for hesitations

# transcribe hesitations

