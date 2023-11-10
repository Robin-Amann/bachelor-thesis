import torch
import torchaudio
import utils.file as loader
import tasks.audio_transcript_alignment.ctc_extention as ctc
import tasks.transcript_alignment.preprocessing as pre
from progress.bar import ChargingBar
import utils.constants as constants
from pathlib import Path

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def align_file(audio_file, transcript_file, destination_file, sample_rate, wav2vec2_model=None) :
    transcript = loader.read_file(transcript_file)
    trimmed, clean = pre.process(transcript, patterns=['\(\(', '\)\)'])  # \[[^\]]*\] --> [laughter] [mn] [lipsmack]
    transcript = clean.upper().replace(' ', '|')
    waveform = loader.read_audio(audio_file, sample_rate)
    words = ctc.full_alignment(waveform, transcript, device)    # list of {transcript, start, end, score}
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


def sb_align_automatic(audio_file, transcript_file, sample_rate, wav2vec2_model) :
    audio = loader.read_audio(audio_file, sample_rate)  # [ [...] ]
    transcript = loader.read_file(transcript_file)
    trimmed, clean = pre.process(transcript)
    transcript = clean.upper().replace(' ', '|')
    words = ctc.full_alignment(audio, transcript, device)    # list of {transcript, start, end, score}
    # words = ctc.base_ctc(audio, transcript, device, wav2vec2_model)    # list of {transcript, start, end, score}
    if words :
        for word, t in zip(words, trimmed.split()) :
            word['transcript'] = t
    return words


def sb_align_automatic_directory(segments_dir, audio_dir, transcript_dir, destination_dir, sample_rate) :
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
    model = bundle.get_model().to(device)
    wav2vec2_model = (bundle, model)
    
    segment_files = [(f.stem, f) for f in loader.get_directory_files(segments_dir, 'txt') if 'Speech' in f.stem]
    audio_files = [(f.stem, f) for f in loader.get_directory_files(audio_dir, 'wav') if 'A' in f.stem or 'B' in f.stem]
    transcript_files = [(f.stem, f) for f in loader.get_directory_files(transcript_dir, 'txt')]

    stub = len(Path(segments_dir).parts)
    for stem, segment_file in ChargingBar("Align Transcript to Audio").iter(segment_files) :
        audio_file = next((f for s, f in audio_files if stem[2:7] in s), None) # Number and Speaker
        if audio_file == None :
            print(stem, "has no audio file")
            continue
        
        segments = loader.read_timestamps_from_file(str(segment_file))
        for index, segment in enumerate(segments) :
            transcript_file = next((f for s, f in transcript_files if (stem[2:7] + "{:03d}".format(index)) in s), None)
            words = sb_align_automatic(audio_file, transcript_file, sample_rate, wav2vec2_model)
            if words :
                destination_file = Path(destination_dir) / Path('/'.join(list(segment_file.parts[stub : -1]) + [stem[6]] ) ) / transcript_file.name
                loader.write_words_to_file(words, destination_file)
            else :
                print("could not align", stem + segment)



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