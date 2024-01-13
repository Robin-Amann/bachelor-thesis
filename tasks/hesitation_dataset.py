import utils.file as utils
import utils.constants as c
import datasets 
from datasets import Dataset
from huggingface_hub import login
from progress.bar import ChargingBar

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

sample_rate = c.sample_rate

import shutil
import os

ds_dir = c.data_base / 'dataset'

def create_dataset_files(total_length_h) :
    if os.path.isdir(ds_dir) :
        shutil.rmtree(ds_dir)

    files = utils.get_dir_tuples([ 
        (c.manual_seg_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), 
        (c.audio_dir, lambda f: f.stem[3:8], None, 'wav'), 
        (c.manual_seg_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), 
        (c.automatic_align_dir / '0', lambda f: f.stem[2:7])
        ])

    total = 0
    for segmens_file, audio_file, manual_files, automatic_files in ChargingBar('Create Dataset Files').iter(files) :
        segments = utils.read_dict(segmens_file)
        audio = utils.read_audio(audio_file, sample_rate)[0]
        for manual_file, automatic_file in zip(sorted(manual_files), sorted(automatic_files)) :
            segment_id = int(manual_file.stem[7:10])
            audio_start, audio_end = list(segments[segment_id].values())
            automatic = utils.read_dict(automatic_file)
            manual = utils.read_dict(manual_file)
            i = 0
            for pre, post in zip([{'end' : 0}] + automatic, automatic + [{'start' : audio_end - audio_start}]) :
                start_a = pre['end']
                end_a = post['start']
                gap = end_a - start_a
                if gap > 0.2 :
                    start, end = calculate_gap(manual, start_a, end_a, audio_end - audio_start)
                    if end - start > 0.1 :
                        destination_file = utils.repath(manual_file, c.manual_dir, ds_dir, stem= manual_file.stem + '_' + str(i).rjust(3, '0'), suffix='.wav')                    

                        audio_segment = audio[ int( (audio_start + start) * sample_rate ) : int( ( audio_start + end ) * sample_rate ) ]
                        utils.write_audio(destination_file, audio_segment, sample_rate)
                        gap_transcript = ' '.join( w['word'] for w in manual if start <= w['start'] and w['end'] <= end)
                        utils.write_file(destination_file.with_suffix('.txt'), gap_transcript)
                        i += 1

                        if int(total / 60 / 60) != int((total + end - start) / 60 / 60) :
                            print(int(total + end - start))
                        total += end - start
                        if total / 60 / 60 >= total_length_h :
                            print('last file:', destination_file.stem)
                            return


def ds_generators() :
    files = utils.get_dir_tuples([ 
        (ds_dir, lambda f: f.stem), 
        (ds_dir, lambda f: f.stem, None, 'wav'), 
        ])
    print()
    print(len(files))
    print()
    for transcript_file, audio_file in files :
        yield {
            'audio' : str(audio_file),
            'audio_length' : len(utils.read_audio(audio_file, sample_rate)[0]) / sample_rate,
            'transcript' : utils.read_file(transcript_file)
        }


def create_dataset() :
    login(token='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')
    
    # I hope there will be no memory problems
    ds = Dataset.from_generator(ds_generators).cast_column('audio', datasets.Audio(sampling_rate=sample_rate))
    print(ds)
    print(len(ds))
    ds = ds.train_test_split(test_size=0.2)
    ds.push_to_hub('Robin-Amann/my_first_dataset')

