import os
import torch
import torchaudio
import utils.file as utils
import utils.constants as constants
from progress.bar import ChargingBar
from transformers import AutoModelForCTC, Wav2Vec2ProcessorWithLM
from enum import Enum
import utils.transcript as word_utils
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

MODELS = Enum('Model', ['whisper_large', 'wav2vec2', 'wav2vec2LM', 'wav2vec2_custom_LM', 'wav2vec2_custom_LM_hesitations'])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(model) :
    print("device:", device)
    print("os:", os.name)
    if model == MODELS.whisper_large :
        model_id = "openai/whisper-large-v3"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, use_safetensors=True, cache_dir = str(constants.model_dir / "whisper_timing")
        )
        processor = AutoProcessor.from_pretrained(model_id, cache_dir = str(constants.model_dir / "whisper_timing"))
        pipe = pipeline(
            "automatic-speech-recognition", model=model, tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor,
            max_new_tokens=128, batch_size=1, chunk_length_s=35,
            return_timestamps='word', torch_dtype=torch_dtype, device=device)
    elif model == MODELS.wav2vec2 :
        pipe = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h", tokenizer='facebook/wav2vec2-base-960h', feature_extractor='facebook/wav2vec2-base-960h')
    elif model == MODELS.wav2vec2LM :
        model_id = 'patrickvonplaten/wav2vec2-base-960h-4-gram'
        print('download model')
        model = AutoModelForCTC.from_pretrained(model_id)
        print('download processor')
        processor = AutoProcessor.from_pretrained(model_id, cache_dir='/export/data3/bachelor_theses/ramann/data')
        pipe = pipeline("automatic-speech-recognition", model=model, tokenizer=processor, feature_extractor=processor.feature_extractor, decoder=processor.decoder)
    elif model == MODELS.wav2vec2_custom_LM :
        processor = Wav2Vec2ProcessorWithLM.from_pretrained(constants.model_dir / 'wav2vec2_custom_LM_2')
        pipe = pipeline("automatic-speech-recognition", model="jonatasgrosman/wav2vec2-large-xlsr-53-english", tokenizer=processor, feature_extractor=processor.feature_extractor, decoder=processor.decoder, device=0)
    elif model == MODELS.wav2vec2_custom_LM_hesitations :
        processor = Wav2Vec2ProcessorWithLM.from_pretrained(constants.model_dir / 'wav2vec2_custom_LM_hesitations_2')
        pipe = pipeline("automatic-speech-recognition", model="jonatasgrosman/wav2vec2-large-xlsr-53-english", tokenizer=processor, feature_extractor=processor.feature_extractor, decoder=processor.decoder, device=0)
    else :
        raise NameError(model, "not available")
    return (pipe, 16000)


def transcribe_part_pipe(start, end, speech, sample_rate, model, score) :
    pipe, model_sample_rate = model
    if sample_rate != model_sample_rate:
        data = torchaudio.functional.resample(data, sample_rate, model_sample_rate)
    data = speech[int(start*model_sample_rate) : int(end*model_sample_rate)].numpy()
    result = pipe(data)['text'].split()
    result = [ { 'word' : ' '.join( word_utils.replace_anomalies(w) for w in result), 'start' : start, 'end' : end, 'score' : score } ]
    return result


def predict_file(gaps_file, speech, destination_file, sample_rate, model) :
    gaps = utils.read_dict(gaps_file)
    start = 0
    transcript = []
    for gap in gaps :
        start, end, score = gap['start'], gap['end'], gap['score']
        transcript += transcribe_part_pipe(start, end, speech, sample_rate, model, score)
    utils.write_dict(destination_file, transcript)


def predict_dir(segments_dir, speech_dir, gaps_dir, destination_dir, sample_rate, model, start_dir=0, end_dir=100) :
    import transformers
    transformers.logging.set_verbosity_error()
    
    transcription_model = load_model(model)

    files = utils.get_dir_tuples([ (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), (speech_dir, lambda f : f.stem[3:8], None, 'wav'), (gaps_dir, lambda f : f.stem[2:7])])
    grouped = utils.group_files(files, 3)

    for p in [ p for p in grouped.keys() if start_dir <= int(p) <= end_dir ] :
        print("Hesitation Translation dir", p)
        for segment_file, speech_file, gaps_files in ChargingBar("Hesitation Translation").iter(grouped[p]) :

            segments = utils.read_dict(str(segment_file))
            speech = utils.read_audio(str(speech_file), sample_rate)[0]
            
            for index, segment in enumerate(segments) :
                if segment_file.stem[:7] + "{:03d}".format(index) in constants.controversial_files :
                    continue
                gaps_file = next(f for f in gaps_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
                destination_file = utils.repath(gaps_file, gaps_dir, destination_dir)                
                start = segment['start']
                end = segment['end']

                predict_file(gaps_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcription_model)