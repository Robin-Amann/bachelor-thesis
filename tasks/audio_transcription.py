import os
from enum import Enum
import torch
import whisper
import utils.file as utils
import utils.constants as constants
import tasks.transcript_cleanup as cleanup
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


def transcribe_whisper_large_v3(pipe, speech, transcript_file) :
    result = pipe(speech.numpy())['chunks']
    result = [ tuple(x.values()) for x in result ]
    result = [ { 'word' : text.strip(), 'start' : start, 'end' : end } for text, (start, end) in result ]
    utils.write_dict(transcript_file, result)


def transcribe_whisper(transcription_model, speech, transcript_file) :
    transcript = transcription_model.transcribe(speech, language='en', fp16 = False)
    transcript = transcript['text'].strip()
    transcript = transcript.replace('…', '...')

    if len(set(transcript) - constants.ALLOWED_CHARS) > 0 :
        utils.write_file(constants.error_dir / 'audio_transcription.txt', "Could not transcribe properly " + transcript_file.stem + "\nTranscript: " + transcript + "\n", 'a')

    transcript = cleanup.remove_non_words(transcript)
    utils.write_file(transcript_file, transcript)


def transcribe_dir(segments_dir, speech_dir, transcript_dir, sample_rate, model=MODELS.whisper) :
    transcription_model = load_model(model)
    
    files = utils.get_dir_tuples([ (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), (speech_dir, lambda f : f.stem[2:7], None, 'wav')])
    grouped = utils.group_files(files, 3)

    for p in grouped.keys() :
        print("Transcribe dir", p)
        for segment_file, speech_file in ChargingBar("Transcribe Audio").iter(grouped[p]) :
            stem = segment_file.stem

            segments = utils.read_dict(str(segment_file))
            speech = utils.read_audio(str(speech_file), sample_rate)[0]
         
            for index, segment in enumerate(segments) :
                transcript_file = utils.repath(segment_file, segments_dir, transcript_dir, [stem[6]], stem= stem[:7] + "{:03d}".format(index))

                start = segment['start']
                end = segment['end']
                if model == MODELS.whisper :
                    transcribe_whisper(transcription_model, speech[int(start*sample_rate) : int(end*sample_rate)].to(device), transcript_file)
                elif model == MODELS.whisper_large_v3 :
                    transcribe_whisper_large_v3(transcription_model, speech[int(start*sample_rate) : int(end*sample_rate)], transcript_file)
                                    