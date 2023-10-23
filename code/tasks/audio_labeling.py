import utils.file as utils
import tasks.audio_transcript_alignment.audio_transcript_alignment as audio_transcript_alignment
import tasks.vocabulary_extraction as vocabulary
from progress.bar import ChargingBar

THRESHOLD = 0.25 #minimum legth of audio to be considered a gap in seconds
HESITATIONS = []

def label(words, audio_len, sample_rate) :
    minimum_gap = THRESHOLD * sample_rate
    segments = []
    # insert words
    for w in words :
        if w['transcript'] in HESITATIONS or w['transcript'][0] == '-' or w['transcript'][-1] == '-' :
            segments.append({'label' : utils.LABELS.HESITATION, 'start' : w['start'], 'end' : w['end']})
        else :
            segments.append({'label' : utils.LABELS.SPEECH, 'start' : w['start'], 'end' : w['end']})
    
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
        segments.insert(0, {'label' : utils.LABELS.SILENCE, 'start' : 0, 'end' : segments[0]['start'] - 1})
    if segments[-1]['end'] < audio_len - 1 :
        segments.append({'label' : utils.LABELS.SILENCE, 'start' : segments[-1]['end'] + 1, 'end' : audio_len - 1})
    i = 0    
    while i < len(segments) - 1:
        if segments[i+1]['start'] - segments[i]['end'] > 1 :
            segments.insert(i+1, {'label' : utils.LABELS.SILENCE, 'start' : segments[i]['end'] + 1, 'end' : segments[i+1]['start'] - 1})
        else :
            i += 1
    return segments
# {label, start, end}


def label_file(audio_file, sample_rate, words) :
    audio = utils.read_audio(audio_file, sample_rate)
    audio_len = audio[0].size(0)
    segments = label(words, audio_len, sample_rate)
    utils.write_audio_labels_to_file(audio_file, segments)


def label_directory(audio_directory, words_directory, sample_rate) :
    HESITATIONS = list( vocabulary.read_vocabulary('code\\sample_data\\vocabulary\\hesitations_by_eye.txt').keys() )
    files = utils.get_directory_files(words_directory, "txt")
    with ChargingBar("Audio Labeling", max=len(files)) as bar:
        for file in files :
            f = str(file)[len(words_directory) : -4]
            audio_file = audio_directory + f + '.wav'
            words_file = words_directory + f + '.txt'
            words = audio_transcript_alignment.read_words_from_file(words_file)
            label_file(audio_file, sample_rate, words)
            bar.next()