import os
import torch
import whisper
import utils.file as utils
import utils.constants as constants
import tasks.transcript_cleanup as cleanup
from progress.bar import ChargingBar
import numpy as np

download_root = str(constants.model_dir / 'whisper')
MIN_GAP = 1

def load_model(model) :
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device:", device)
    if model == 'whisper' :
            transcription_model = whisper.load_model('base', device=device, download_root=download_root)
            print("os:", os.name)
    else :
        raise NameError(model, "not available")
    return transcription_model

def transcribe_part(start, end, audio_file, speech, sample_rate, model) :
    transcript = ""
    if start - end > MIN_GAP :
        utils.write_audio(audio_file, speech[int(start*sample_rate) : int(end*sample_rate)], sample_rate)
        # transcript = model.transcribe(str(audio_file), language='en', fp16 = False)
        data = np.asarray([ speech[int(start*sample_rate) : int(end*sample_rate)] ]).astype(np.float32)
        transcript = model.transcribe(data, language='en', fp16 = False)
        transcript = cleanup.remove_non_words(transcript['text'])
        os.remove(audio_file)
        if transcript and not transcript.isspace() :
            print("additional transcript (", audio_file.stem, "): '", transcript, "'", sep='')
    return transcript


def predict_file(transcript_file, speech, destination_file, sample_rate, model = None) :
    if model == None or model == 'whisper':
        model = load_model('whisper')
    audio_file = transcript_file.with_suffix('.wav')
    transcript_old = utils.read_words_from_file(transcript_file)
    transcript_new = ""
    start = 0
    if len(transcript_old) == 0 :
        end = len(speech) / sample_rate
    for word in transcript_old :
        end = word['start']
        transcript_new += " " + transcribe_part(start, end, audio_file, speech, sample_rate, model) + " " + word['word']
        start = word['end']

    transcript_new += " " + transcribe_part(start, len(speech) / sample_rate, audio_file, speech, sample_rate, model)
    transcript_new = ' '.join(transcript_new.split())
    utils.write_file(destination_file, transcript_new)


def predict_dir(segments_dir, speech_dir, transcript_dir, destination_dir, sample_rate, model) :
    transcription_model = load_model(model)

    files = utils.get_dir_tuples([
        (segments_dir, 'txt', lambda s : 'Speech' in s, lambda s, s1 : True),                       # 1
        (speech_dir, 'wav', lambda s : True, lambda s1, s2 : s1[2:7] in s2),  # number + speaker    # 1
        (transcript_dir, 'txt', lambda s : True, lambda s1, s3 : s1[2:7] in s3)                     # n
    ])
    files = [(f1, f2[0][1], [f for _, f in f3]) for (s, f1), f2, f3 in files if not s in constants.controversial_files and not s[2:6] in constants.ignore_files]

    # group files
    s = 1
    grouped = dict()
    for f in files :
        p = int(f[0].parts[-3])
        if p in grouped :
            grouped[p].append(f)
        else :
             grouped[p] = [f]       
    ps = [x for x in grouped.keys() if x >= s]
    ps.sort()

    for p in ps :
        print("Hesitation Translation dir", p)
        for segment_file, speech_file, transcript_files in ChargingBar("Hesitation Translation").iter(grouped[p]) :
            segments = utils.read_timestamps_from_file(str(segment_file))
            speech = utils.read_audio(str(speech_file), sample_rate)[0]
            
            for index, segment in enumerate(segments) :
                if segment_file.stem[:7] + "{:03d}".format(index) in constants.controversial_files :
                    continue
                transcript_file = next(f for f in transcript_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
                destination_file = utils.repath(transcript_file, transcript_dir, destination_dir)                
                start = segment['start']
                end = segment['end']

                predict_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcription_model)
                