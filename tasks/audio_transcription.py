import whisper
import utils.file as utils
import utils.constants as constants
import tasks.transcript_cleanup as cleanup
from progress.bar import ChargingBar
import os
import torch
import re

download_root = str(constants.model_dir / 'whisper')

def load_model(model) :
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device:", device)
    if model == 'whisper' :
            transcription_model = whisper.load_model('base', device=device, download_root=download_root)
            print("os:", os.name)
    else :
        raise NameError(model, "not available")
    return transcription_model


def transcribe_dir(segments_dir, speech_dir, transcript_dir, sample_rate, model="whisper") :
    transcription_model = load_model(model)
    
    files = utils.get_dir_tuples([segments_dir, speech_dir], ['txt', 'wav'], [ lambda s : 'Speech' in s, lambda s : True ], lambda s1, s2 : s1[2:7] in s2 )
    files = [(s, f1, f2[0][1]) for (s, f1), f2 in files if not s[2:6] in constants.ignore_files]
    
    # group files
    s = 1
    grouped = dict()
    for f in files :
        p = int(f[1].parts[-3])
        if p in grouped :
            grouped[p].append(f)
        else :
             grouped[p] = [f]       
    ps = [x for x in grouped.keys() if x >= s]
    ps.sort()

    for p in ps :
        print("Transcribe dir", p)
        for stem, segment_file, speech_file in ChargingBar("Transcribe Audio").iter(grouped[p]) :
            segments = utils.read_timestamps_from_file(str(segment_file))
            speech = utils.read_audio(str(speech_file), sample_rate)[0]
            
            for index, segment in enumerate(segments) :
                transcript_file = utils.repath(segment_file, segments_dir, transcript_dir, [stem[6]], stem= stem[:7] + "{:03d}".format(index))

                transcript = "<|>"
                if os.path.isfile(transcript_file) :
                    transcript = utils.read_file(transcript_file)
                    if len(set(transcript) - constants.ALLOWED_CHARS) == 0 :
                        continue

                start = segment['start']
                end = segment['end']
                temp_audio_file = str(segment_file.with_suffix('.wav'))
                utils.write_audio(temp_audio_file, speech[int(start*sample_rate) : int(end*sample_rate)], sample_rate)

                tries = 0
                while tries < 3 and len(set(transcript) - constants.ALLOWED_CHARS) > 0 :
                    transcript = transcription_model.transcribe(temp_audio_file, language='en', fp16 = False)
                    transcript = transcript['text'].strip()
                    transcript = transcript.replace('…', '...')
                    tries += 1

                if len(set(transcript) - constants.ALLOWED_CHARS) > 0 :
                    utils.write_file(constants.error_dir / 'audio_transcription.txt', "Could not transcribe properly " + stem + "\nTranscript: " + transcript + "\n", 'a')

                os.remove(temp_audio_file)

                transcript = cleanup.remove_non_words(transcript)
                
                utils.write_file(transcript_file, transcript)