import whisper
import utils.file as utils
from progress.bar import ChargingBar
from pathlib import Path
import os
import torch


def load_model(model) :
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if model == 'whisper' :
        if os.name is 'posix' :
            transcription_model = whisper.load_model('base', device=device, download_root='export/data3/bachelor_theses/ramann/models')
        else :     
            transcription_model = whisper.load_model('base', device=device)
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


def sb_transcribe_dir(segments_dir, speech_dir, transcript_dir, sample_rate, model="whisper") :
    transcription_model = load_model(model)

    segment_files = [ (f.stem, f) for f in utils.get_directory_files(segments_dir, 'txt') if 'Speech' in f.stem]
    speech_files = [ (f.stem, f) for f in utils.get_directory_files(speech_dir, 'wav')]

    stub = len(Path(segments_dir).parts)
    for stem, segment_file in ChargingBar("Transcribe Audio").iter(segment_files) :   
        speech_file =  next(f for s, f in speech_files if stem[2:7] in s) # number and speaker
        segments = utils.read_timestamps_from_file(str(segment_file))
        speech = utils.read_audio(str(speech_file), sample_rate)[0]
        
        for index, segment in enumerate(segments) :
            start = segment['start']
            end = segment['end']
            temp_audio_file = str(segment_file.with_suffix('.wav'))
            utils.write_audio(temp_audio_file, speech[int(start*sample_rate) : int(end*sample_rate)], sample_rate)
            transcript = transcription_model.transcribe(temp_audio_file, language='en', fp16 = False)
            transcript = transcript['text'].strip()
            transcript_file = Path(transcript_dir) / Path('/'.join(list(segment_file.parts[stub : -1]) + [stem[6]])) / (stem[:7] + "{:03d}".format(index) + '.txt')
            utils.write_file(transcript_file, transcript)
            os.remove(temp_audio_file)
 

#                                                   WindowsPath(D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html)                       
# str(f)        --> string representation  (\\)     D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html
# f.as_posix()  --> string representation  (/)      D:/Robin_dataset/fisher english/training speech 2/fe_03_p2_sph1/index.html
# f.parent      --> directory                       D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1
# f.name        --> filename (with extention)       index.html
# f.suffix      --> only suffix                     .html
# f.stem        --> file name                       index