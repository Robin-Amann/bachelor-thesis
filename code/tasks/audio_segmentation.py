import utils.file as utils
from progress.bar import ChargingBar

JOIN_GAP = 0.5  # in sec

def extract_speaker(transcript, speaker_A = "A", speaker_B = "B", header_lines = 2) :
    lines = [l for l in transcript.split("\n") if l and not l.isspace() and any(c.isalpha() for c in l)][header_lines:]
    text = []
    for l in lines :
        line = l.split()
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

    speech = [[t for t in text if t['speaker'] == speaker_A], [t for t in text if t['speaker'] == speaker_B]]
    for s in speech :
        i = 0
        while i < len(s) - 1 :
            if s[i+1]['start'] - s[i]['end'] < JOIN_GAP :
                s[i]['end'] = s[i+1]['end']
                s[i]['utterance'] = s[i]['utterance'] + ' ' + s[i+1]['utterance']
                s.pop(i+1)
            else :
                i += 1

    return speech[0], speech[1]
    

# i assume 2 channels (stereo)
def segment(transcript, waveform, sample_rate) :
    return [{'transcript' : t['utterance'], 'audio' : waveform[int(t['start'] * sample_rate) : int(t['end'] * sample_rate)]  } for t in transcript]


def segment_directory(speech_dir_source, transcript_dir_source, speech_dir_destination, transcript_dir_destination, sample_rate) :
    files = utils.get_directory_files(transcript_dir_source, "txt")
    # file = source + parent + stem + suffix
    for file in ChargingBar("Segment Audio and Transcripts").iter(files) :
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