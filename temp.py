from multiprocessing import Pool
import pickle
import torch
import utils.file as utils
import utils.constants as constants
from progress.bar import ChargingBar
from tasks.hesitation_predition import MIN_GAP, load_model, device, MODELS


def preprocess(transcript_file, destination_file, processor, audio, sample_rate) :
    transcript_old = utils.read_words_from_file(transcript_file)
    inputs_new = []
    start = 0
    for word in transcript_old :
        end = word['start']
        if end - start > MIN_GAP :
            audio_gap = audio[int(start*sample_rate) : int(end*sample_rate)]
            inputs = processor(audio_gap, sampling_rate=sample_rate, return_tensors="pt")
            inputs_new.append( {'logits' : inputs, 'start' : start, 'end' : end} )
        start = word['end']
    end = len(audio) / sample_rate
    if end - start > MIN_GAP :
        audio_gap = audio[int(start*sample_rate) : int(end*sample_rate)]
        inputs = processor(audio_gap, sampling_rate=sample_rate, return_tensors="pt")
        inputs_new.append({'logits' : inputs, 'start' : start, 'end' : end})

    with open(destination_file, 'wb') as f :
        pickle.dump(inputs_new, f)


def postprocess(destination_file, processor) :
    inputs = []
    with open(destination_file, 'rb') as f :
        inputs = pickle.load(f)

    transcripts = []
    for input in inputs :
        transcript = processor.batch_decode(input['logits'])
        transcripts.append({ "word": transcript['text'][0], "start": input['start'], "end": input['end'] })

    utils.write_words_to_file(destination_file, transcripts)


def multiprocess_transcribe(destination_file, transcription_model) :
    
    inputs = []
    with open(destination_file, 'rb') as f :
        inputs = pickle.load(f)
    
    outputs = []
    for input in inputs :
        input_values = input['logits']
        with torch.no_grad():
            input_values = input_values.to(device)
            logits = transcription_model(input_values.input_values, attention_mask=input_values.attention_mask).logits
            
            outputs.append({'logits' : logits.cpu().numpy(), "start": input['start'], "end": input['end']})

    with open(destination_file, 'wb') as f :
        pickle.dump(outputs, f)


def multiprocess(files, sample_rate, transcript_dir, destination_dir, processor, function) :
    print(1, end=' | ')
    for segment_file, speech_file, transcript_files in files :
        segments = utils.read_timestamps_from_file(str(segment_file))
        speech = utils.read_audio(str(speech_file), sample_rate)[0]
        
        print(2, end=' | ')
        for index, segment in enumerate(segments) :
            if segment_file.stem[:7] + "{:03d}".format(index) in constants.controversial_files :
                continue
            transcript_file = next(f for f in transcript_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
            destination_file = utils.repath(transcript_file, transcript_dir, destination_dir)                
            start = segment['start']
            end = segment['end']
            audio = speech[int(start*sample_rate) : int(end*sample_rate)]
            print(3, end=' | ')
    
            if function == 'pre' :
                print(destination_file)
                preprocess(transcript_file, destination_file, processor, audio, sample_rate)
            if function == 'post' :
                postprocess(destination_file, processor)
            print(4, end=' | ')
    

def predict_dir_multiprocess(segments_dir, speech_dir, transcript_dir, destination_dir, sample_rate, model) :
    processor, transcription_model = load_model(model)

    print('gather files')
    files = utils.get_dir_tuples([
        (segments_dir, 'txt', lambda s : 'Speech' in s, lambda s, s1 : True),                       # 1
        (speech_dir, 'wav', lambda s : True, lambda s1, s2 : s1[2:7] in s2),  # number + speaker    # 1
        (transcript_dir, 'txt', lambda s : True, lambda s1, s3 : s1[2:7] in s3)                     # n
    ])
    files = [(f1, f2[0][1], [f for _, f in f3]) for (s, f1), f2, f3 in files if not s in constants.controversial_files and not s[2:6] in constants.ignore_files]
    # group files
    s = 1
    grouped = list(map(lambda f :  {int(f[0].parts[-3]) : f}, files))                                               # map files to (parent, file)
    grouped = { k : [f[k] for f in grouped if k in f.keys() ] for k in set([list(g.keys())[0] for g in grouped])}   # group files by parent
    ps = [x for x in grouped.keys() if x >= s]                                                                      # get keys greater than starting point

    print('preprocess')    
    with Pool(len(ps)) as p :
        print( [ len(x[0]) for x in [ (f, sample_rate, transcript_dir, destination_dir, processor, 'pre') for f in grouped.values() ] ] )
        p.starmap(multiprocess, [ (f, sample_rate, transcript_dir, destination_dir, processor, 'pre') for f in grouped.values() ])
    
    for p in ps :
        print("Hesitation Translation dir", p)
        for segment_file, speech_file, transcript_files in ChargingBar("Hesitation Translation").iter(grouped[p]) :
            segments = utils.read_timestamps_from_file(str(segment_file))
            for index, _ in enumerate(segments) :
                if segment_file.stem[:7] + "{:03d}".format(index) in constants.controversial_files :
                    continue
                transcript_file = next(f for f in transcript_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
                destination_file = utils.repath(transcript_file, transcript_dir, destination_dir)                
                multiprocess_transcribe(destination_file, transcription_model)

    print('postprocess')
    with Pool(len(ps)) as p :
        p.starmap(multiprocess, [ (f, sample_rate, transcript_dir, destination_dir, processor, 'post') for f in grouped.values() ])


predict_dir_multiprocess(constants.manual_seg_dir, constants.audio_dir, constants.automatic_align_dir, constants.retranscibed_dir / 'wav2vec2_custom_LM_hesitations_experiment', constants.sample_rate, model=MODELS.wav2vec2_custom_LM_hesitations)
# [68, 70, 66, 80, 92, 84, 86, 84, 86, 52, 122, 96, 136, 124, 92, 94, 74, 78, 54, 38, 66, 68, 74, 4, 8, 56, 52, 42, 16] --> 2062
#  20  21  22  23  24  25  26  27  28  29  30   31  32   33   34  35  36  37  38  39  40  41  43 44 45  46  47  48  49 



















# 2. Getting data for your language model
# from datasets import Dataset
# import utils.file as utils
# import utils.constants as c
# import re

# files = [ f for f in utils.get_directory_files(c.manual_seg_dir, 'txt') if not 'Speech' in f.stem ]

# sep = ' '

# def gen():
#   for file in files :
#     text = ' '.join( w['word'].lower() if w['pause_type'] or w['is_restart'] else '_' for w in utils.read_label_timings_from_file(file))
#     text = re.sub('(_ )*_', '_', text)
#     text = re.sub(' _ ', sep, text)
#     text = text.strip('_ ')

#     if text and not text.isspace() :
#         yield {'text' : text }

# ds = Dataset.from_generator(gen)

# # store dataset in txt file
# with open("text.txt", "w") as file:
#   file.write(sep.join(ds["text"]))
