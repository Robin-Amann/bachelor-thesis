import os
import torch
import whisper
import utils.file as utils
import utils.constants as constants
import tasks.transcript_cleanup as cleanup
from progress.bar import ChargingBar
import numpy as np
from transformers import AutoTokenizer, AutoFeatureExtractor, AutoModelForCTC
import torch

MIN_GAP = 0.1


def load_model(model) :
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device:", device)
    print("os:", os.name)
    if model == 'whisper' :
        transcription_model = whisper.load_model('base', device=device, download_root=str(constants.model_dir / 'whisper'))
        return transcription_model
    elif model == 'ctc' :
        transcription_model = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        tokenizer = AutoTokenizer.from_pretrained("facebook/wav2vec2-base-960h")
        feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
        return (transcription_model, tokenizer, feature_extractor)
    else :
        raise NameError(model, "not available")


def transcribe_part_whisper(start, end, speech, sample_rate, model) :
    data = np.asarray([ speech[int(start*sample_rate) : int(end*sample_rate)] ]).astype(np.float32)
    transcript = model.transcribe(data, language='en', fp16 = False)
    transcript = cleanup.remove_non_words(transcript['text'])
    return [ { "word": transcript.lower(), "start": start, "end": end } ] 


def transcribe_part_ctc(start, end, speech, sample_rate, model) :
    transcription_model, tokenizer, feature_extractor = model
    data = np.asarray(speech[int(start*sample_rate) : int(end*sample_rate)]).astype(np.float32)
    input_values = feature_extractor(data, return_tensors="pt", sampling_rate=sample_rate).input_values
    logits = transcription_model(input_values).logits[0]
    pred_ids = torch.argmax(logits, axis=-1)

    outputs = tokenizer.decode(pred_ids, output_word_offsets=True)
    time_offset = transcription_model.config.inputs_to_logits_ratio / feature_extractor.sampling_rate
    words = [ { "word": d["word"].lower(), "start": round(d["start_offset"] * time_offset, 2) + start, "end": round(d["end_offset"] * time_offset, 2) + start } for d in outputs.word_offsets ]
    return words


def predict_file(transcript_file, speech, destination_file, sample_rate, transcription_function, model) :
    transcript_old = utils.read_words_from_file(transcript_file)
    transcript_new = []
    start = 0
    if len(transcript_old) == 0 :
        end = len(speech) / sample_rate
    for word in transcript_old :
        end = word['start']
        if end - start > MIN_GAP :
            transcript_new = transcript_new + transcription_function(start, end, speech, sample_rate, model)
        start = word['end']
    end = len(speech) / sample_rate
    if end - start > MIN_GAP :
        transcript_new = transcript_new + transcription_function(start, end, speech, sample_rate, model)
    t = ' '.join(w['word'] for w in transcript_new)
    if t and not t.isspace() :
        print(t)
    utils.write_words_to_file(destination_file, transcript_new)


def predict_dir(segments_dir, speech_dir, transcript_dir, destination_dir, sample_rate, model) :
    transcription_model = load_model(model)

    files = utils.get_dir_tuples([
        (segments_dir, 'txt', lambda s : 'Speech' in s, lambda s, s1 : True),                       # 1
        (speech_dir, 'wav', lambda s : True, lambda s1, s2 : s1[2:7] in s2),  # number + speaker    # 1
        (transcript_dir, 'txt', lambda s : True, lambda s1, s3 : s1[2:7] in s3)                     # n
    ])
    files = [(f1, f2[0][1], [f for _, f in f3]) for (s, f1), f2, f3 in files if not s in constants.controversial_files and not s[2:6] in constants.ignore_files]
    files = files[:1]
    # group files
    s = 1
    grouped = list(map(lambda f :  {int(f[0].parts[-3]) : f}, files))                                               # map files to (parent, file)
    grouped = { k : [f[k] for f in grouped if k in f.keys() ] for k in set([list(g.keys())[0] for g in grouped])}   # group files by parent
    ps = [x for x in grouped.keys() if x >= s]                                                                      # get keys greater than starting point
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

                if model == 'whisper' :
                    predict_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcribe_part_whisper, transcription_model)
                elif model == 'ctc' :
                    predict_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcribe_part_ctc, transcription_model)
                                