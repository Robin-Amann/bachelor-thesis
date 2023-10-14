import torch
import utils.file as loader
import ctc.extention as ctc
import voice_activation_detection.voice_detection_silero_vad as voice_activation
import transcription_model.whisper as whisper
import os


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
audio_file = ".\\audio_alignment\\data\\sample_data\\4s.wav"
manual_transcript_file = ".\\audio_alignment\\data\\sample_data\\transcript_manual.txt"
sample_rate = 16000

# load audio
waveform = loader.load_audio(audio_file, sample_rate)
waveform = torch.Tensor( [ (waveform[0] + waveform[1]).tolist() ] )

# create transcript (whisper / audioclient) or load manual transcript
# transcript = whisper.transcribe(audio_file)
# manual_transcript = loader.read_file(manual_transcript_file)
transcript = "ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"

# # perform ctc alignment
words = ctc.full_alignment(waveform, transcript, device)
print(words)

# # perform voice activation
# speech_timestamps = voice_activation.voice_activation_detection(audio_file, sample_rate)

# get untranscribed audio fragments


# perform prediction model to search for hesitations


# transcribe hesitations

