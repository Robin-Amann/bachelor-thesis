from enum import Enum

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