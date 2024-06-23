import utils.file as utils
import utils.constants as c
import utils.transcript as word_utils
import torch
from transformers import AutoModelForCTC, Wav2Vec2Processor, pipeline
from progress.bar import ChargingBar
from huggingface_hub import login


# model = AutoModelForCTC.from_pretrained("Robin-Amann/wav2vec2-base-sb-finetune")
# processor = Wav2Vec2Processor.from_pretrained("Robin-Amann/wav2vec2-base-sb-finetune")

# login(token='old token is invalid')
#ds = load_dataset("Robin-Amann/gap_dataset")

# for i in range(10) :
#     example = ds['test'][i]
#     with torch.no_grad():
#         input_values = processor(example["audio"]["array"], return_tensors="pt", padding="longest").input_values
#         logits = model(input_values).logits

#     predicted_ids = torch.argmax(logits, dim=-1)
#     transcription = processor.batch_decode(predicted_ids)

#     print('hypothesis:', example['transcript'])
#     print('transcript:', transcription)


def load_model() :
    login(token='old token is invalid')
    model_id = 'Robin-Amann/wav2vec2-base-sb-finetune'
    model = AutoModelForCTC.from_pretrained(model_id)
    processor = Wav2Vec2Processor.from_pretrained(model_id) #, cache_dir='/export/data3/bachelor_theses/ramann/data')
    pipe = pipeline("automatic-speech-recognition", model=model, tokenizer=processor, feature_extractor=processor.feature_extractor)
    return pipe, 16000

import utils.wer_alignment as alignmnet


def transcribe_file(transcript_file, manual_file, speech, destination_file, sample_rate, model, processor) :
    original_transcipt = utils.read_dict(transcript_file)
    manual_transcript = utils.read_dict(manual_file)
    m_aligned, a_aligned, _ = alignmnet.align_words(manual_transcript, original_transcipt, {'word' : ''})
    manual_transcript_untranscribed = [ m for m, a in zip(m_aligned, a_aligned) if m['word'] and not a['word'] ]
    transcript = []
    x = []
    for pre, post in zip( [ {'end' : 0} ] + original_transcipt, original_transcipt + [ {'start' : speech.size(0) / sample_rate} ] ) :
        start, end = pre['end'], post['start']
        if end - start >= c.MIN_GAP :
            data = speech[int(start*sample_rate) : int(end*sample_rate)].numpy()

            with torch.no_grad():
                input_values = processor(data, return_tensors="pt", sampling_rate=sample_rate, padding="longest").input_values
                logits = model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            result = processor.batch_decode(predicted_ids)
            result = ' '.join(result)
            manual = ' '.join([ w['word'] for w in manual_transcript if word_utils.overlap((start, end), w) >= (w['end'] - w['start']) / 2])
            manual_untranscribed = ' '.join([ w['word'] for w in manual_transcript_untranscribed if word_utils.overlap((start, end), w) >= (w['end'] - w['start']) / 2])
            x.append( [manual, manual_untranscribed, result])
            transcript.append( { 
                'word' : ' '.join( word_utils.replace_anomalies(w) for w in result.split()), 
                'start' : start, 
                'end' : end 
            } )
    # utils.write_dict(destination_file, transcript)
    return x

import utils.console as console

def transcribe_dir(segments_dir, speech_dir, transcript_dir, destination_dir, lower_bound=c.DATA_SPLIT, start_dir=0, end_dir=100) :    
    model = AutoModelForCTC.from_pretrained("Robin-Amann/wav2vec2-base-sb-finetune")
    processor = Wav2Vec2Processor.from_pretrained("Robin-Amann/wav2vec2-base-sb-finetune")
    sample_rate = 16000

    files = utils.get_dir_tuples([ 
        (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), 
        (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' not in f.stem), 
        (speech_dir, lambda f : f.stem[3:8], None, 'wav'), 
        (transcript_dir, lambda f : f.stem[2:7])])
    grouped = utils.group_files(files, 3)

    # for p in [ p for p in grouped.keys() if start_dir <= int(p) <= end_dir ] :
    #     if (int(p) + 1) * 100 < lower_bound : 
    #         continue 
    #     print("direct retranscription dir", p)
#        for segment_file, manual_files, speech_file, transcript_files in grouped[p] : # ChargingBar("direct retranscription").iter(grouped[p]) :
    result = [['manual', 'untranscribed', 'predicted']]
    i = 0
    for segment_file, manual_files, speech_file, transcript_files in ChargingBar("direct retranscription").iter(files) :
        if int(segment_file.stem[2:6]) < lower_bound or i == 10:
            continue
        i += 1
        print(i)
        segments = utils.read_dict(str(segment_file))
        speech = utils.read_audio(str(speech_file), sample_rate)[0]
        
        for index, segment in enumerate(segments) :
            if segment_file.stem[:7] + "{:03d}".format(index) in c.controversial_files :
                continue
            manual_file = next(f for f in manual_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
            transcript_file = next(f for f in transcript_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
            destination_file = utils.repath(transcript_file, transcript_dir, destination_dir)                
            start = segment['start']
            end = segment['end']

            result += transcribe_file(transcript_file, manual_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, model, processor)
    utils.write_file(destination_dir / 'table.txt', '\n'.join(console.create_table_representation(result)))
