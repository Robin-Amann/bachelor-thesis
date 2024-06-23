import utils.file as utils
import utils.constants as c
import datasets 
from datasets import Dataset
from huggingface_hub import login
from progress.bar import ChargingBar
import shutil
import os
import utils.transcript as word_utils

sample_rate = 16000
ds_dir = c.data_base / 'gap_dataset'


# 3917 is 80% of dataset
def create_dataset_files(upper_bound=3916, PERCENTAGE=0.8) :
    if os.path.isdir(ds_dir) :
        shutil.rmtree(ds_dir)

    files = utils.get_dir_tuples([ 
        (c.manual_seg_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), 
        (c.audio_dir, lambda f: f.stem[3:8], None, 'wav'), 
        (c.manual_seg_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), 
        (c.automatic_align_dir / 'custom ctc' / '1', lambda f: f.stem[2:7])
        ])

    print(len(files))
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
                    gap_transcript = ' '.join( [ w['word'] for w in manual if word_utils.overlap((start, end), w) >= (w['end'] - w['start']) * PERCENTAGE ] )
                    audio_segment = audio[ int( (audio_start + start) * sample_rate ) : int( ( audio_start + end ) * sample_rate ) ]

                    destination_file = utils.repath(manual_file, c.manual_dir, ds_dir, stem= manual_file.stem + '_' + str(i).rjust(3, '0'), suffix='.wav')                    
                    utils.write_audio(destination_file, audio_segment, sample_rate)
                    utils.write_file(destination_file.with_suffix('.txt'), gap_transcript)
                    i += 1


def ds_generator() :
    files = utils.get_dir_tuples([ 
        (ds_dir, lambda f: f.stem), 
        (ds_dir, lambda f: f.stem, None, 'wav'), 
        ])
    for transcript_file, audio_file in files :
        transcript = utils.read_file(transcript_file).strip()
        yield {
            'audio' : str(audio_file),
            'audio_length' : len(utils.read_audio(audio_file, sample_rate)[0]) / sample_rate,
            'transcript' : transcript,
            'label' : 1 if transcript else 0 
        }


def create_dataset(name='gap_dataset') :
    login(token='old token is invalid')
    
    # I hope there will be no memory problems
    ds = Dataset.from_generator(ds_generator, cache_dir=str(c.data_base))
    
    ds = ds.cast_column('audio', datasets.Audio(sampling_rate=sample_rate))
    ds = ds.cast_column('label', datasets.ClassLabel(names=['silence', 'hesitation']))
    print(ds)
    print(len(ds))
    ds = ds.train_test_split(test_size=0.2)
    ds.push_to_hub('Robin-Amann/' + name)

    if os.path.isdir(str(c.data_base / 'generator')) :
        shutil.rmtree(str(c.data_base / 'generator'))