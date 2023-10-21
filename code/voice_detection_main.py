import torch
import torchaudio
import voice_detection.voice_detection_silero_vad as voice_activation



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sample_rate = 16000

# example
audio_file = "code\\sample_data\\segmented\\fe_03_00001_0.wav"
print("audiofile sample rate:", torchaudio.info(audio_file).sample_rate)

speech_timestamps = voice_activation.voice_activation_detection(audio_file, sample_rate) # list of {start, end}

for w in speech_timestamps :
    print(w)