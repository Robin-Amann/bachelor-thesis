import torch
import torchaudio
import pathlib
import os

def get_directory_files(directory, filetype) :
    files = [f for f in pathlib.Path(directory).glob("**\*." + filetype)]    
    return files


def read_audio(file_path, sample_rate) :
    if not os.path.isfile(file_path) :
        return []
    waveform, _ = torchaudio.load(file_path)  
    if torchaudio.info(file_path).sample_rate != sample_rate :    
        waveform = torchaudio.functional.resample(
            orig_freq=torchaudio.info(file_path).sample_rate, 
            new_freq=sample_rate, 
            waveform=waveform)
    return waveform

    
def write_audio(file_path, waveform, sample_rate) :
    if waveform.dim() == 1 :
        waveform = waveform[None, :]
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    torchaudio.save(file_path, waveform, sample_rate)


def read_file(path) :
    content = ""
    with open(path, "r", encoding="utf8") as file :
        content = file.read()
    return content


def write_file(path, content, mode='w') :
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding='utf8') as file :
        file.write(content)


def read_vocabulary(path) :
    file_content = read_file(path).split('\n')
    vocabulary = [ tuple(w.split('|')) for w in file_content if w and not w.isspace()]
    vocabulary = [ (w, int(c)) for w, c in vocabulary]
    return dict(vocabulary)


def write_vocabulary(path, vocabulary) :
    sorted_vocabulary = sorted(vocabulary.items(), key=lambda item: item[1])[::-1]
    file_content = '\n'.join([ w + '|' + str(c) for w, c in sorted_vocabulary])
    write_file(path, file_content)


from enum import Enum
LABELS = Enum('Label', ['SILENCE', 'SPEECH', 'HESITATION'])

def read_audio_labels_from_file(file_path) :
    segments = read_file(file_path)
    segments = segments.split('\n')
    segments = [tuple(l.split('|')) for l in segments]
    segments = [ { 'label' : LABELS[label], 'start' : int(start), 'end' : int(end)} for label, start, end in segments ]
    return segments


def write_audio_labels_to_file(audio_file, segments) :
    segments = [seg['label'].name + '|' + str(seg['start']) + '|'+ str(seg['end']) for seg in segments]
    segments = '\n'.join(segments)
    write_file(audio_file[:-4] + ".txt", segments)


def write_words_to_file(words, destination_file) :
    words = [word['transcript'] + '|' + str(word['start']) + '|'+ str(word['end']) + '|' + str(word['score']) for word in words]
    words = '\n'.join(words)
    write_file(destination_file, words)

def read_words_from_file(file_path) :
    words = read_file(file_path)
    words = words.split('\n')
    words = [tuple(l.split('|')) for l in words]
    words = [ { 'transcript' : transcript, 'start' : int(start), 'end' : int(end), 'score' : float(score) } for transcript, start, end, score in words ]
    return words