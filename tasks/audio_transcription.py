import os
from enum import Enum
import torch
import whisper
import utils.file as utils
import utils.transcript as word_utils
import utils.constants as constants
from progress.bar import ChargingBar
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

MODELS = Enum('Model', ['whisper', 'whisper_large_v3'])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(model) :
    print("device:", device)
    print("os:", os.name)
    if model == MODELS.whisper :
        transcription_model = whisper.load_model('base', device=device, download_root=str(constants.model_dir / 'whisper')).to(device)
        return transcription_model
    elif model == MODELS.whisper_large_v3 :
        model_id = "openai/whisper-large-v3"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, use_safetensors=True, cache_dir = str(constants.model_dir / "whisper_timing")
        )
        model.to(device)
        processor = AutoProcessor.from_pretrained(model_id, cache_dir = str(constants.model_dir / "whisper_timing"))
        pipe = pipeline(
            "automatic-speech-recognition", model=model, tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor,
            max_new_tokens=128, batch_size=1, chunk_length_s=35,
            return_timestamps='word', torch_dtype=torch_dtype, device=device)
        return pipe
    else :
        raise NameError(model, "not available")


def transcribe_whisper_large_v3(pipe, speech, end, transcript_file) :
    # transcribe audio
    result = pipe(speech.numpy())['chunks']
    result = [ tuple(x.values()) for x in result ]
    # bring to custom format
    result = [ { 'word' : text.strip(), 'start' : start, 'end' : end } for text, (start, end) in result ]
    if len(result) > 0 and result[-1]['end'] == None :
        result[-1]['end'] = end
    # remove noise
    for word in result :
        word['word'] = word_utils.replace_anomalies(word['word'])
    result = [ w for w in result if word_utils.is_word(w['word']) ]
    utils.write_dict(transcript_file, result)


def transcribe_whisper(transcription_model, speech, transcript_file) :
    # transcribe audio
    transcript = transcription_model.transcribe(speech, language='en', fp16 = False)
    transcript = transcript['text'].strip()
    # remove noise
    words = transcript.split()
    words = [ word_utils.replace_anomalies(word) for word in words ]
    words = [ word for word in words if word_utils.is_word(word) ]
    transcript = ' '.join(words)

    if word_utils.contains_special_chars(transcript, additional=' ') :
        utils.write_file(constants.error_dir / 'audio_transcription.txt', "Could not transcribe properly " + transcript_file.stem + "\nTranscript: " + transcript + "\n", 'a')

    utils.write_file(transcript_file, transcript)


def transcribe_dir(segments_dir, speech_dir, transcript_dir, sample_rate, model=MODELS.whisper) :
    transcription_model = load_model(model)
    
    files = utils.get_dir_tuples([ (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), (speech_dir, lambda f : f.stem[3:8], None, 'wav')] )
    grouped = utils.group_files(files, 3)

    for p in [ 0 < x < 100 for x in grouped.keys() ] :
        print("Transcribe dir", p)
        for segment_file, speech_file in ChargingBar("Transcribe Audio").iter(grouped[p]) :
            stem = segment_file.stem

            segments = utils.read_dict(str(segment_file))
            speech = utils.read_audio(str(speech_file), sample_rate)[0]
            if segments[-1]['end'] > speech.size(0) / sample_rate :
                print('Ignore (to short)', stem)
                continue
            for index, segment in enumerate(segments) :
                transcript_file = utils.repath(segment_file, segments_dir, transcript_dir, [stem[6]], stem= stem[:7] + "{:03d}".format(index))
                if os.path.isfile(transcript_file) :
                    continue

                start = segment['start']
                end = segment['end']
                if model == MODELS.whisper :
                    transcribe_whisper(transcription_model, speech[int(start*sample_rate) : int(end*sample_rate)].to(device), transcript_file)
                elif model == MODELS.whisper_large_v3 :
                    transcribe_whisper_large_v3(transcription_model, speech[int(start*sample_rate) : int(end*sample_rate)], end, transcript_file)
                                    