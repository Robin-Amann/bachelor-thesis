import torch
import utils.file as loader
import audio_transcript_alignment.ctc_extention as ctc
import transcript_alignment.preprocessing as pre

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def write_words_to_file(words, destination_file) :
    words = [word['transcript'] + '|' + str(word['start']) + '|'+ str(word['end']) + '|' + str(word['score']) for word in words]
    words = '\n'.join(words)
    loader.write_file(destination_file, words)

def read_words_from_file(file_path) :
    words = loader.read_file(file_path)
    words = words.split('\n')
    words = [tuple(l.split('|')) for l in words]
    words = [ { 'transcript' : transcript, 'start' : int(start), 'end' : int(end), 'score' : float(score) } for transcript, start, end, score in words ]
    return words

def align_file(audio_file, transcript_file, destination_file, sample_rate) :
    transcript = loader.read_file(transcript_file)
    trimmed, clean = pre.process(transcript)
    transcript = clean.upper().replace(' ', '|')
    waveform = loader.read_audio(audio_file, sample_rate)
    # words = ctc.full_alignment(waveform, transcript, device)    # list of {transcript, start, end, score}
    words = ctc.base_ctc(waveform, transcript, device)    # list of {transcript, start, end, score}
    for word, t in zip(words, trimmed.split()) :
        word['transcript'] = t
    write_words_to_file(words, destination_file)

def align_directory(audio_directory, transcript_directory, destination_directory, sample_rate) :
    files = loader.get_directory_files(transcript_directory, "txt")
    for file in files :
        print("align", str(file))
        f = str(file)[len(transcript_directory) : ]
        audio_file = audio_directory + f
        transcript_file = transcript_directory + f
        destination_file = destination_directory + f
        align_file(audio_file, transcript_file, destination_file, sample_rate)
