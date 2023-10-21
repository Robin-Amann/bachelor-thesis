import utils.file as utils

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


def segment_directory(speech_dir_source, transcript_dir_source, speech_dir_destination, transcript_dir_destination, sample_rate) :
    files = utils.get_directory_files(transcript_dir_source, "txt")
    # file = source + parent + stem + suffix
    for file in files :
        print("segment", str(file))
        stem = file.stem
        parent = str(file.parent)[len(transcript_dir_source) : ] + "\\"
        transcript_file = transcript_dir_source + parent + stem + ".txt"
        audio_file = speech_dir_source + parent + stem + ".wav"        # -4: .txt

        transcript = utils.read_file(transcript_file)
        waveform = utils.read_audio(audio_file, sample_rate)

        speech_A = waveform[0]
        speech_B = waveform[1]
        transcript_A, transcript_B = extract_speaker(transcript)

        A = segment(transcript_A, speech_A, sample_rate)
        B = segment(transcript_B, speech_B, sample_rate)

        for index, seg in enumerate(A) :
            utils.write_audio(speech_dir_destination + parent + stem + "\\A_" + str(index) + ".wav", seg['audio'], sample_rate)
            utils.write_file(transcript_dir_destination + parent + stem + "\\A_" + str(index) + ".txt", seg['transcript'])
        for index, seg in enumerate(B) :
            utils.write_audio(speech_dir_destination + parent + stem + "\\B_" + str(index) + ".wav", seg['audio'], sample_rate)
            utils.write_file(transcript_dir_destination + parent + stem + "\\B_" + str(index) + ".txt", seg['transcript'])