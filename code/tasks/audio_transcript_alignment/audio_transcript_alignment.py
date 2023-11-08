import torch
import torchaudio
import utils.file as loader
import tasks.audio_transcript_alignment.ctc_extention as ctc
import tasks.transcript_alignment.preprocessing as pre
from progress.bar import ChargingBar
import utils.constants as constants

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def align_file(audio_file, transcript_file, destination_file, sample_rate, wav2vec2_model=None) :
    transcript = loader.read_file(transcript_file)
    trimmed, clean = pre.process(transcript, patterns=['\(\(', '\)\)'])  # \[[^\]]*\] --> [laughter] [mn] [lipsmack]
    transcript = clean.upper().replace(' ', '|')
    waveform = loader.read_audio(audio_file, sample_rate)
    # words = ctc.full_alignment(waveform, transcript, device)    # list of {transcript, start, end, score}
    words = ctc.base_ctc(waveform, transcript, device, wav2vec2_model)    # list of {transcript, start, end, score}
    if words == [] :
        print("Audio Transcript Error", transcript_file)
        loader.write_file(constants.error_dir + '\\audio_transcript_alignment.txt', "could not align " + audio_file + " " + transcript_file + '\n', mode='a')
    for word, t in zip(words, trimmed.split()) :
        word['transcript'] = t
    loader.write_words_to_file(words, destination_file)


def align_directory(audio_directory, transcript_directory, destination_directory, sample_rate) :
    files = loader.get_directory_files(transcript_directory, "txt")
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
    model = bundle.get_model().to(device)
    wav2vec2_model = (bundle, model)
    for file in ChargingBar("Align Transcript to Audio").iter(files) :
        if int(str(file.parent)[-5 : ]) < 38 :
            print("skip", str(file))
            continue
        f = str(file)[len(transcript_directory) : -4]
        audio_file = audio_directory + f + '.wav'
        transcript_file = transcript_directory + f + '.txt'
        destination_file = destination_directory + f + '.txt'
        align_file(audio_file, transcript_file, destination_file, sample_rate, wav2vec2_model)


def sb_align_directory(segments_dir, audio_dir, transcript_dir, destination_dir, sample_rate) :
    files = loader.get_directory_files(transcript_dir, "txt")
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
    model = bundle.get_model().to(device)
    wav2vec2_model = (bundle, model)
    for file in ChargingBar("Align Transcript to Audio").iter(files) :
        if int(str(file.parent)[-5 : ]) < 38 :
            print("skip", str(file))
            continue
        f = str(file)[len(transcript_dir) : -4]
        audio_file = audio_dir + f + '.wav'
        transcript_file = transcript_dir + f + '.txt'
        destination_file = destination_dir + f + '.txt'
        align_file(audio_file, transcript_file, destination_file, sample_rate, wav2vec2_model)


def realign_file(transcript_file, destination_file) :
    transcript = loader.read_file(transcript_file)
    trimmed, clean = pre.process(transcript, patterns=['\(\(', '\)\)'])
    words = loader.read_words_from_file(destination_file)
    for word, t in zip(words, trimmed.split()) :
        word['transcript'] = t
    loader.write_words_to_file(words, destination_file)


def realign_directory(transcript_directory, destination_directory) :
    files = loader.get_directory_files(destination_directory, "txt")
    for file in ChargingBar("Realign Transcript to Audio").iter(files) :
        f = str(file)[len(destination_directory) : -4]
        transcript_file = transcript_directory + f + '.txt'
        destination_file = destination_directory + f + '.txt'
        realign_file(transcript_file, destination_file)