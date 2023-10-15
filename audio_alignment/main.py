import torch
import torchaudio
import utils.file as loader
import ctc.extention as ctc
import voice_activation_detection.voice_detection_silero_vad as voice_activation
import transcription_model.whisper as whisper
import visualization.visualize as visual
import prediction_model.audio_utils as audio


## examples
audio_file = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript = "I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT"

# audio_file = ".\\audio_alignment\\data\\sample_data\\4s.wav"
# transcript = "ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"

# audio_file = ".\\audio_alignment\\data\\sample_data\\10s.wav"
# transcript = "THEY|MIGHT|CANCEL|MY|INSURANCE|WELL|I|THINK|THAT'S|THE|BEST|THING|POSSIBILITY|ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
manual_transcript_file = ".\\audio_alignment\\data\\sample_data\\transcript_manual.txt"
sample_rate = 16000
print("audiofile sample rate:", torchaudio.info(audio_file).sample_rate)

# load audio
waveform = loader.load_audio(audio_file, sample_rate)

# create transcript (whisper / audioclient) or load manual transcript
transcript = whisper.transcribe(audio_file)
# manual_transcript = loader.read_file(manual_transcript_file)


# # perform ctc alignment
words = ctc.full_alignment(waveform, transcript, device)    # list of {transcript, start, end, score}
# words = ctc.base_ctc(waveform, transcript, device)    # list of {transcript, start, end, score}

# # perform voice activation (sample rate before resampling)
speech_timestamps = voice_activation.voice_activation_detection(audio_file, torchaudio.info(audio_file).sample_rate) # list of {start, end}
ratio = sample_rate / torchaudio.info(audio_file).sample_rate
speech_timestamps = [{"start": int(ratio*s["start"]), "end" : int(ratio*s["end"])} for s in speech_timestamps]

visual.plot_words_and_speech(waveform[0], words, speech_timestamps, sample_rate)

# get untranscribed audio fragments
audio_fragments = audio.get_untranscribed_audio(waveform, words, speech_timestamps, sample_rate)    # list of {start, end, audio, speech = {start, end}}   speech is relative
for fragment in audio_fragments :
    print(fragment)
visual.plot_gaps(waveform[0], audio_fragments, sample_rate)

# perform prediction model to search for hesitations


# transcribe hesitations

