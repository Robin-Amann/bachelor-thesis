import os
import torch
import torchaudio
import whisper
import utils.file as utils
import utils.constants as constants
import tasks.transcript_cleanup as cleanup
from progress.bar import ChargingBar
import numpy as np
from transformers import AutoTokenizer, AutoFeatureExtractor, AutoModelForCTC, Wav2Vec2ProcessorWithLM, Wav2Vec2ForCTC
from torchaudio.models.decoder import download_pretrained_files, ctc_decoder
from enum import Enum
import utils.transcript as word_utils

MIN_GAP = 0.1

MODELS = Enum('Model', ['whisper', 'wav2vec2', 'wav2vec2LM', 'wav2vec2_custom_LM', 'wav2vec2_custom_LM_hesitations'])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(model) :
    print("device:", device)
    print("os:", os.name)
    if model == MODELS.whisper :
        transcription_model = whisper.load_model('base', device=device, download_root=str(constants.model_dir / 'whisper'))
        transcription_model.to(device)
        return transcription_model
    elif model == MODELS.wav2vec2 :
        transcription_model = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h").to(device)
        tokenizer = AutoTokenizer.from_pretrained("facebook/wav2vec2-base-960h").to(device)
        feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h").to(device)
        return (transcription_model, tokenizer, feature_extractor)
    elif model == MODELS.wav2vec2LM :
        bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_10M
        LM_WEIGHT = 3.23
        WORD_SCORE = -0.26
        BEAM_SIZE = 1500
        files = download_pretrained_files("librispeech-4-gram") # language model
        beam_search_decoder = ctc_decoder(
            lexicon=files.lexicon,
            tokens=files.tokens,
            lm=files.lm,
            nbest=1,
            beam_size=BEAM_SIZE,
            lm_weight=LM_WEIGHT,
            word_score=WORD_SCORE,
        )
        return (bundle.get_model().to(device), bundle.sample_rate, beam_search_decoder)
    elif model == MODELS.wav2vec2_custom_LM :
        processor = Wav2Vec2ProcessorWithLM.from_pretrained(constants.model_dir / 'wav2vec2_custom_LM_2')
        transcription_model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-english").to(device)
        return (processor, transcription_model)
    elif model == MODELS.wav2vec2_custom_LM_hesitations :
        processor = Wav2Vec2ProcessorWithLM.from_pretrained(constants.model_dir / 'wav2vec2_custom_LM_hesitations_2')
        transcription_model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-english").to(device)
        return (processor, transcription_model)
    else :
        raise NameError(model, "not available")


def transcribe_part_whisper(start, end, speech, sample_rate, model) :
    data = speech[int(start*sample_rate) : int(end*sample_rate)].to(device)
    transcript = model.transcribe(data, language='en', fp16 = False)
    transcript = ' '.join([ word for word in transcript['text'].split() if word_utils.is_word(word)])
    return [ { "word": transcript.lower(), "start": start, "end": end } ] 


def transcribe_part_ctc(start, end, speech, sample_rate, model) :
    transcription_model, tokenizer, feature_extractor = model
    data = np.asarray(speech[int(start*sample_rate) : int(end*sample_rate)]).astype(np.float32)
    input_values = feature_extractor(data, return_tensors="pt", sampling_rate=sample_rate).input_values.to(device)
    logits = transcription_model(input_values).logits[0]
    pred_ids = torch.argmax(logits, axis=-1)

    outputs = tokenizer.decode(pred_ids, output_word_offsets=True)
    time_offset = transcription_model.config.inputs_to_logits_ratio / feature_extractor.sampling_rate
    words = [ { "word": d["word"].lower(), "start": round(d["start_offset"] * time_offset, 2) + start, "end": round(d["end_offset"] * time_offset, 2) + start } for d in outputs.word_offsets ]
    return words

def transcribe_part_ctc_language(start, end, speech, sample_rate, model) :
    acoustic_model, sample_rate, beam_search_decoder = model
    if sample_rate != sample_rate:                                                                  # TODO : makes no sense
        speech = torchaudio.functional.resample(speech, sample_rate, sample_rate)   
    speech = speech[None, int(start*sample_rate) : int(end*sample_rate)].to(device)
    with torch.no_grad():
        emission, _ = acoustic_model(speech)
        beam_search_result = beam_search_decoder(emission.cpu())
    transcript = " ".join(beam_search_result[0][0].words).strip()
    return [ { "word": transcript, "start": start, "end": end } ]    

    # predicted_tokens = beam_search_decoder.idxs_to_tokens(beam_search_result.tokens)
    # tokens_str = "".join(predicted_tokens)
    # transcript = " ".join(tokens_str.split("|"))
    # timesteps = beam_search_result.timesteps


def transcribe_part_ctc_custom_language(start, end, speech, sample_rate, model) :
    processor, transcription_model = model
    if sample_rate != sample_rate:                                                                  # TODO : makes no sense
        speech = torchaudio.functional.resample(speech, sample_rate, sample_rate)
    speech = speech[int(start*sample_rate) : int(end*sample_rate)]
    inputs = processor(speech, sampling_rate=sample_rate, return_tensors="pt").to(device)
    
    with torch.no_grad():
        logits = transcription_model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    transcript = processor.batch_decode(logits.cpu().numpy())
    return [ { "word": transcript['text'][0], "start": start, "end": end } ]


def predict_file(transcript_file, speech, destination_file, sample_rate, transcription_function, model) :
    transcript_old = utils.read_dict(transcript_file)
    transcript_new = []
    start = 0
    for word in transcript_old :
        end = word['start']
        if end - start > MIN_GAP :
            transcript_new = transcript_new + transcription_function(start, end, speech, sample_rate, model)
        start = word['end']
    end = len(speech) / sample_rate
    if end - start > MIN_GAP :
        transcript_new = transcript_new + transcription_function(start, end, speech, sample_rate, model)
    utils.write_dict(destination_file, transcript_new)


def predict_dir(segments_dir, speech_dir, transcript_dir, destination_dir, sample_rate, model) :
    transcription_model = load_model(model)

    files = utils.get_dir_tuples([ (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), (speech_dir, lambda f : f.stem[2:7], None, 'wav'), (transcript_dir, lambda f : f.stem[2:7])])
    grouped = utils.group_files(files, 3)

    for p in grouped.keys() :
        print("Hesitation Translation dir", p)
        for segment_file, speech_file, transcript_files in ChargingBar("Hesitation Translation").iter(grouped[p]) :
            segments = utils.read_dict(str(segment_file))
            speech = utils.read_audio(str(speech_file), sample_rate)[0]
            
            for index, segment in enumerate(segments) :
                if segment_file.stem[:7] + "{:03d}".format(index) in constants.controversial_files :
                    continue
                transcript_file = next(f for f in transcript_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
                destination_file = utils.repath(transcript_file, transcript_dir, destination_dir)                
                start = segment['start']
                end = segment['end']

                if model == MODELS.whisper :
                    predict_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcribe_part_whisper, transcription_model)
                elif model == MODELS.wav2vec2 :
                    predict_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcribe_part_ctc, transcription_model)
                elif model == MODELS.wav2vec2LM :
                    predict_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcribe_part_ctc_language, transcription_model)
                elif model == MODELS.wav2vec2_custom_LM or model == MODELS.wav2vec2_custom_LM_hesitations :
                    predict_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, transcribe_part_ctc_custom_language, transcription_model)


