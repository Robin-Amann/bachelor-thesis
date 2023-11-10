import whisper
import utils.file as utils
from progress.bar import ChargingBar
from pathlib import Path
import os
import torch


def load_model(model) :
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device:", device)
    if model == 'whisper' :
        if os.name == 'posix' :
            transcription_model = whisper.load_model('base', device=device, download_root='export/data3/bachelor_theses/ramann/models')
            print("os:", os.name)
        else :
            transcription_model = whisper.load_model('base', device=device)
            print("os:", os.name)
    else :
        transcription_model = whisper.load_model('base', device=device)
    return transcription_model

def transcribe_dir(speech_dir, transcript_dir, model="whisper") :
    transcription_model = load_model(model)
      
    files = utils.get_directory_files(speech_dir, 'wav')
    for f in ChargingBar("Transcribe Audio").iter(files) :
        stem = f.stem
        parent = str(f.parent)[len(speech_dir) : ] + "\\"
        transcript = transcription_model.transcribe(str(f), language='en', fp16 = False)
        transcript = transcript['text']       
        utils.write_file(transcript_dir + parent + stem + ".txt", transcript)


def transcribe_dir(segments_dir, speech_dir, transcript_dir, sample_rate, model="whisper") :
    transcription_model = load_model(model)

    files = utils.get_dir_tuples([segments_dir, speech_dir], ['txt', 'wav'], [ lambda s : 'Speech' in s, lambda s : True ], lambda s1, s2 : s1[2:7] in s2 )
    files = [(s, f1, f2[0][1]) for (s, f1), f2 in files]

    for stem, segment_file, speech_file in ChargingBar("Transcribe Audio").iter(files) :
        segments = utils.read_timestamps_from_file(str(segment_file))
        speech = utils.read_audio(str(speech_file), sample_rate)[0]
        
        for index, segment in enumerate(segments) :
            transcript_file = utils.repath(segment_file, segments_dir, transcript_dir, [stem[6]], stem= stem[:7] + "{:03d}".format(index))

            start = segment['start']
            end = segment['end']
            temp_audio_file = str(segment_file.with_suffix('.wav'))
            utils.write_audio(temp_audio_file, speech[int(start*sample_rate) : int(end*sample_rate)], sample_rate)
            transcript = transcription_model.transcribe(temp_audio_file, language='en', fp16 = False)
            os.remove(temp_audio_file)

            transcript = transcript['text'].strip()
            utils.write_file(transcript_file, transcript)
            