import utils.file as utils
import utils.constants as c
import datasets 
from datasets import Dataset
from huggingface_hub import login
from progress.bar import ChargingBar
import shutil
import os
import utils.transcript as word_utils

sample_rate = c.sample_rate
ds_dir = c.data_base / 'dataset'

# # # calculate data needed for training

# from datasets import load_dataset, Audio, ClassLabel
# from transformers import AutoModelForAudioClassification, TrainingArguments, Trainer
# from transformers import Wav2Vec2ForCTC
# model = AutoModelForAudioClassification.from_pretrained("facebook/wav2vec2-base", num_labels=2, label2id={'1' : 1, '2' : 2}, id2label={1 : '1', 2 : '2'})
# print(model.num_parameters())
# model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base", gradient_checkpointing=True, ctc_loss_reduction="mean")# pad_token_id=processor.tokenizer.pad_token_id,)
# print(model.num_parameters())

# https://malay-haldar.medium.com/how-much-training-data-do-you-need-da8ec091e956
# lower bound:
# (94.569.090 - 94.396.320) * 10 = 1.727.700


# stupid idea
def calculate_gap(manual, start_a, end_a, total_end) :
    start_words = [ w for w in manual if w['start'] <= start_a ]
    if not start_words :
        start = 0
    elif start_words[-1]['end'] <= start_a or ( start_a - start_words[-1]['start'] >= start_words[-1]['end'] - start_a ) : # lands between words (widen gap)
        start = start_words[-1]['end']
    elif len(start_words) == 1 :
        start = 0
    else :
        start = start_words[-2]['end']

    end_words = [ w for w in manual if w['end'] >= end_a ]
    if not end_words :
        end = total_end
    elif end_words[0]['start'] >= end_a or ( end_a - end_words[0]['start'] <= end_words[0]['end'] - end_a ) : # lands between words (widen gap)
        end = end_words[0]['start']
    elif len(end_words) == 1 :
        end = total_end
    else :
        end = end_words[1]['start']
    
    return start, end

# 3917 is 80% of dataset
def create_dataset_files(total_length_h = 0, upper_bound=3916) :
    if os.path.isdir(ds_dir) :
        shutil.rmtree(ds_dir)

    files = utils.get_dir_tuples([ 
        (c.manual_seg_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), 
        (c.audio_dir, lambda f: f.stem[3:8], None, 'wav'), 
        (c.manual_seg_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), 
        (c.automatic_align_dir / 'custom ctc' / '0', lambda f: f.stem[2:7])
        ])

    # total = 0
    for segmens_file, audio_file, manual_files, automatic_files in ChargingBar('Create Dataset Files').iter(files) :
        if int(segmens_file.stem[2:6]) >= upper_bound :
            continue
        segments = utils.read_dict(segmens_file)
        audio = utils.read_audio(audio_file, sample_rate)[0]
        for manual_file, automatic_file in zip(sorted(manual_files), sorted(automatic_files)) :
            segment_id = int(manual_file.stem[7:10])
            audio_start, audio_end = list(segments[segment_id].values())
            automatic = utils.read_dict(automatic_file)
            manual = utils.read_dict(manual_file)
            i = 0
            for pre, post in zip([{'end' : 0}] + automatic, automatic + [{'start' : audio_end - audio_start}]) :
                start = pre['end']
                end = post['start']
                if end - start >= c.MIN_GAP :
                    gap_transcript = ' '.join( [ w['word'] for w in manual if word_utils.overlap((start, end), w) >= (w['end'] - w['start']) / 2 ] )
                    audio_segment = audio[ int( (audio_start + start) * sample_rate ) : int( ( audio_start + end ) * sample_rate ) ]

                    destination_file = utils.repath(manual_file, c.manual_dir, ds_dir, stem= manual_file.stem + '_' + str(i).rjust(3, '0'), suffix='.wav')                    
                    utils.write_audio(destination_file, audio_segment, sample_rate)
                    utils.write_file(destination_file.with_suffix('.txt'), gap_transcript)
                    i += 1

                    # start, end = calculate_gap(manual, start_a, end_a, audio_end - audio_start)
                    # if end - start > 0.1 :
                    #     destination_file = utils.repath(manual_file, c.manual_dir, ds_dir, stem= manual_file.stem + '_' + str(i).rjust(3, '0'), suffix='.wav')                    

                    #     audio_segment = audio[ int( (audio_start + start) * sample_rate ) : int( ( audio_start + end ) * sample_rate ) ]
                    #     utils.write_audio(destination_file, audio_segment, sample_rate)
                    #     gap_transcript = ' '.join( w['word'] for w in manual if start <= w['start'] and w['end'] <= end)
                    #     utils.write_file(destination_file.with_suffix('.txt'), gap_transcript)
                    #     i += 1

                    #     if int(total / 60 / 60) != int((total + end - start) / 60 / 60) :
                    #         print(int(total + end - start))
                    #     total += end - start
                    #     if total / 60 / 60 >= total_length_h :
                    #         print('last file:', destination_file.stem)
                    #         return


def ds_generator() :
    files = utils.get_dir_tuples([ 
        (ds_dir, lambda f: f.stem), 
        (ds_dir, lambda f: f.stem, None, 'wav'), 
        ])
    print()
    print(len(files))
    print()
    for transcript_file, audio_file in files :
        transcript = utils.read_file(transcript_file).strip()
        yield {
            'audio' : str(audio_file),
            'audio_length' : len(utils.read_audio(audio_file, sample_rate)[0]) / sample_rate,
            'transcript' : transcript,
            'label' : 1 if transcript else 0 
        }


def create_dataset() :
    login(token='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')
    
    # I hope there will be no memory problems
    ds = Dataset.from_generator(ds_generator, cache_dir=str(c.data_base))
    
    ds = ds.cast_column('audio', datasets.Audio(sampling_rate=sample_rate))
    ds = ds.cast_column('label', datasets.ClassLabel(names=['silence', 'hesitation']))
    print(ds)
    print(len(ds))
    ds = ds.train_test_split(test_size=0.2)
    ds.push_to_hub('Robin-Amann/my_first_dataset')

    if os.path.isdir(str(c.data_base / 'generator')) :
        shutil.rmtree(str(c.data_base / 'generator'))