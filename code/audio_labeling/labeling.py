from enum import Enum
import utils.file as utils
import audio_transcript_alignment.audio_transcript_alignment as audio_transcript_alignment


LABELS = Enum('Label', ['SILENCE', 'SPEECH', 'HESITATION'])
THRESHOLD = 0.25 #minimum legth of audio to be considered a gap in seconds
HESITATIONS = ["UM", 'UH']

def label(words, audio_len, sample_rate) :
    minimum_gap = THRESHOLD * sample_rate
    segments = []
    # insert words
    for w in words :
        if w['transcript'] in HESITATIONS :
            segments.append({'label' : LABELS.HESITATION, 'start' : w['start'], 'end' : w['end']})
        else :
            segments.append({'label' : LABELS.SPEECH, 'start' : w['start'], 'end' : w['end']})
    
    # cluster words
    if segments[0]['start'] < minimum_gap :
        segments[0]['start'] = 0
    if audio_len - segments[-1]['end'] < minimum_gap :
        segments[-1]['end'] = audio_len - 1
    i = 0
    
    while i < len(segments) - 1 :
        if segments[i+1]['start'] - segments[i]['end'] < minimum_gap and segments[i]['label'] == segments[i+1]['label']:
            segments[i]['end'] = segments[i+1]['end']
            segments.pop(i+1)
        else :
            i += 1
    # add silence
    if segments[0]['start'] > 0 :
        segments.insert(0, {'label' : LABELS.SILENCE, 'start' : 0, 'end' : segments[0]['start'] - 1})
    if segments[-1]['end'] < audio_len - 1 :
        segments.append({'label' : LABELS.SILENCE, 'start' : segments[-1]['end'] + 1, 'end' : audio_len - 1})
    i = 0    
    while i < len(segments) - 1:
        if segments[i+1]['start'] - segments[i]['end'] > 1 :
            segments.insert(i+1, {'label' : LABELS.SILENCE, 'start' : segments[i]['end'] + 1, 'end' : segments[i+1]['start'] - 1})
        else :
            i += 1
    return segments
# {label, start, end}


def write_segments_to_file(audio_file, segments) :
    segments = [seg['label'] + '|' + seg['start'] + '|'+ seg['end'] for seg in segments]
    segments = '\n'.join(segments)
    utils.write_file(audio_file[:-4] + ".txt", )


def read_segments_from_file(file_path) :
    segments = utils.read_file(file_path)
    segments = segments.split('\n')
    segments = [tuple(l.split('|')) for l in segments]
    segments = [ { 'label' : label, 'start' : start, 'end' : end} for label, start, end in segments ]
    return segments


def label_file(audio_file, sample_rate, words) :
    audio = utils.read_audio(audio_file, sample_rate)
    audio_len = audio[0].size(0)
    segments = label(words, audio_len, sample_rate)
    write_segments_to_file(audio_file, segments)


def align_directory(audio_directory, words_directory, sample_rate) :
    files = utils.get_directory_files(words_directory, "txt")
    for file in files :
        print("align", str(file))
        f = str(file)[len(words_directory) : ]
        audio_file = audio_directory + f
        words_file = words_directory + f
        words = audio_transcript_alignment.read_words_from_file(words_file)
        label_file(audio_file, sample_rate, words)