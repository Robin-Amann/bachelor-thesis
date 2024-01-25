from transformers import pipeline
import utils.file as utils
from progress.bar import ChargingBar
import utils.constants as c
import os

MIN_GAP = 0.2

def classify_audio_file(transcript_file, speech, destination_file, sample_rate, pipe) :
    transcript = utils.read_dict(transcript_file)
    audio_file = destination_file.with_suffix('.wav')
    gaps = []
    for pre, post in zip( [{'end' : 0}] + transcript, transcript + [{'start' : len(speech) / sample_rate}]) :
        start = pre['end']
        end = post['start']
        if end - start > MIN_GAP :
            utils.write_audio(audio_file, speech[int(start * sample_rate) : int(end * sample_rate)], sample_rate)
            probabilities = pipe(str(audio_file))
            label = max(probabilities, key=lambda p: p['score'])['label']
            if label == 'hesitation' :
                gaps.append({'start' : start, 'end' : end})
            os.remove(audio_file)
                
    utils.write_dict(destination_file, gaps)


def classify_audio_dir(segments_dir, speech_dir, transcript_dir, destination_dir, sample_rate, lower_bound=3916) :
    pipe = pipeline("audio-classification", model="Robin-Amann/classification_model")

    files = utils.get_dir_tuples([ (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), (speech_dir, lambda f : f.stem[3:8], None, 'wav'), (transcript_dir, lambda f : f.stem[2:7])])
    grouped = utils.group_files(files, 3)

    for p in grouped.keys() :
        if (int(p) + 1) * 100 < lower_bound : 
            continue 
        print("Classification dir", p)
        for segment_file, speech_file, transcript_files in ChargingBar("Audio Classification").iter(grouped[p]) :
            if int(segment_file.stem[2:6]) < lower_bound :
                continue
            segments = utils.read_dict(str(segment_file))
            speech = utils.read_audio(str(speech_file), sample_rate)[0]
            
            for index, segment in enumerate(segments) :
                if segment_file.stem[:7] + "{:03d}".format(index) in c.controversial_files :
                    continue
                transcript_file = next(f for f in transcript_files if segment_file.stem[2:7] + "{:03d}".format(index) in f.stem )
                destination_file = utils.repath(transcript_file, transcript_dir, destination_dir)                
                start = segment['start']
                end = segment['end']

                classify_audio_file(transcript_file, speech[int(start*sample_rate) : int(end*sample_rate)], destination_file, sample_rate, pipe)

