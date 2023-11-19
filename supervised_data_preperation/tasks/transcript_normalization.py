from nemo_text_processing.text_normalization.normalize import Normalizer
import utils.file as utils
from progress.bar import ChargingBar
from contextlib import contextmanager
import sys, os


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


def normalize_file(file_path, normalizer = None, filename_extention = None, dataset = 'whisper') :
    if normalizer == None :
        normalizer = Normalizer(input_case='cased', lang='en')
    
    if dataset == 'whisper' :
        transcript = utils.read_file(file_path)
        if not set("$%&0123456789ß").intersection(set(transcript)) :
            return
        transcript = normalizer.normalize(transcript, punct_post_process=True)
        write = utils.write_file
    elif dataset == 'switchboard' :
        content = utils.read_label_timings_from_file(file_path)
        transcript = [w['word'] for w in content]
        transcript = normalizer.normalize_list(transcript, punct_post_process=True)
        for c, t in zip(content, transcript) :
            c['word'] = t
        transcript = content
        write = utils.write_label_timings_to_file

    if filename_extention != None:
        write(file_path[:-4] + "_" + filename_extention + ".txt", transcript)
    else :
        write(file_path, transcript)
    
    

def normalize_dir(directory_path, dataset, filename_extention = None) :
    files = [f for f in utils.get_directory_files(directory_path, "txt") if not 'Speech' in f.stem]
    normalizer = Normalizer(input_case='cased', lang='en')
    for file in ChargingBar("Normalize Transcript").iter(files) :
        with suppress_stdout():
            normalize_file(str(file), normalizer, filename_extention, dataset)    

# normalized = normalizer.normalize(transcipt, verbose=False, punct_post_process=True)
        