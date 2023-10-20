
JOIN_GAP = 0.5  # in sec

def extract_speaker(transcript, speaker_A = "A", speaker_B = "B", header_lines = 2) :
    lines = [l for l in transcript.split("\n") if l and not l.isspace()][header_lines:]
    text = []
    for l in lines :
        line = l.split(' ')
        start = float(line[0])
        end = float(line[1])
        speaker = line[2][0]
        utterance = ' '.join(line[3:])
        text.append({
            'start' : start, 
            'end' : end, 
            'speaker' : speaker, 
            'utterance' : utterance.strip()
            })
    speech_A = [t for t in text if t['speaker'] == speaker_A]
    i = 0
    while i < len(speech_A) - 1 :
        if speech_A[i+1]['start'] - speech_A[i]['end'] < JOIN_GAP :
            speech_A[i]['end'] = speech_A[i+1]['end']
            speech_A[i]['utterance'] = speech_A[i]['utterance'] + " " + speech_A[i+1]['utterance']
            speech_A.pop(i+1)
        else :
            i += 1
    speech_B = [t for t in text if t['speaker'] == speaker_B]
    i = 0
    while i < len(speech_B) - 1 :
        if speech_B[i+1]['start'] - speech_B[i]['end'] <= JOIN_GAP :
            speech_B[i]['end'] = speech_B[i+1]['end']
            speech_B[i]['utterance'] = speech_B[i]['utterance'] + " " + speech_B[i+1]['utterance']
            speech_B.pop(i+1)
        else :
            i += 1
    return speech_A, speech_B
    

# i assume 2 channels (stereo)
def segment(transcript, waveform, sample_rate) :
    return [{'transcript' : t['utterance'], 'audio' : waveform[int(t['start'] * sample_rate) : int(t['end'] * sample_rate)]  } for t in transcript]