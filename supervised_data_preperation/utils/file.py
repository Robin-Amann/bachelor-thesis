import torchaudio
import pathlib
import os
from pathlib import Path

def get_directory_files(directory, filetype) :
    pattern = "**\*." if os.name == 'nt' else "**/*."
    files = [f for f in pathlib.Path(directory).glob(pattern + filetype)]    
    return files

# def get_single_dir_tuples(dir_list, type_list, names, condition) :
#     all_files = []
#     all_files.append([f for f in get_directory_files(dir_list[0], type_list[0]) if condition(f)])
    
#     for dir, t, name in zip(dir_list[1:], type_list[1:], names) :
#         all_files.append([repath(f, dir_list[0], dir, stem = name(f) ,suffix=t) for f in all_files[0] ])
    
#     return list(zip(*all_files))

def _get_dir_tuples(dir_list, type_list, conditions, merge_condition) :
    all_files = []
    for d, t, c in zip(dir_list, type_list, conditions) :
        files = get_directory_files(d, t)
        files = [(f.stem, f) for f in files if c(f.stem)]
        all_files.append(files)
    tuples = []
    mc = merge_condition
    for index, f in enumerate(all_files[0]) :
        if type(merge_condition) == list :
            mc = merge_condition[index]
        suitable = []
        for files in all_files[1 : ] :
            suitable.append([x for x in files if mc(f[0], x[0])])
        if all(len(x) > 0 for x in suitable) :
            tuples.append((f, *suitable))
    return tuples


def get_dir_tuples(*args) :
    if len(args) == 4 :
        return _get_dir_tuples(args[0], args[1], args[2], args[3])
    if len(args) == 2 :
        dir_list = [d[0] for d in args[0]]
        type_list = [d[1] for d in args[0]]
        conditions = [d[2] for d in args[0]]
        return _get_dir_tuples(dir_list, type_list, conditions, args[1])
    if len(args) == 1 :
        dir_list = [d[0] for d in args[0]]
        type_list = [d[1] for d in args[0]]
        conditions = [d[2] for d in args[0]]
        merge_condition = [d[3] for d in args[0]]
        return _get_dir_tuples(dir_list, type_list, conditions, merge_condition)
        

def repath(file, old_grand_dir_p, new_grad_dir_p, sub_dir=[], stem=None, suffix=None) :
    #   grad dirs     parent dirs     sub dirs  stem suffix
    #  |-------------|---------------|---------|-----------|
    #   change        stay the same   add       maybe edit 
    file = Path(file)
    old_grand_dir = Path(old_grand_dir_p)
    new_grad_dir = Path(new_grad_dir_p)
    if stem == None :
        stem = file.stem
    if suffix == None :
        suffix = file.suffix

    n = len(old_grand_dir.parts)
    return new_grad_dir / Path('/'.join(list(file.parts[n : -1]) + sub_dir)) / (stem + suffix)
    

def read_audio(file_path, sample_rate) :
    if not os.path.isfile(file_path) :
        return []
    waveform, _ = torchaudio.load(file_path)  
    if torchaudio.info(file_path).sample_rate != sample_rate :    
        waveform = torchaudio.functional.resample(
            orig_freq=torchaudio.info(file_path).sample_rate, 
            new_freq=sample_rate, 
            waveform=waveform)
    return waveform

    
def write_audio(file_path, waveform, sample_rate) :
    if waveform.dim() == 1 :
        waveform = waveform[None, :]
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    torchaudio.save(file_path, waveform, sample_rate)


def read_file(file_path) :
    content = ""
    with open(file_path, "r", encoding="utf8") as file :
        content = file.read()
    return content


def write_file(file_path, content, mode='w') :
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode, encoding='utf8') as file :
        file.write(content)



def read_obj_from_file(file_path, keys, types = [], separator='<|>') :
    content = read_file(file_path)
    lines = content.split('\n')
    data = [dict(zip(keys, line.split(separator))) for line in lines]
    if types :
        bundle = list(zip(keys, types))
        for value in data :
            for key, type in bundle :
                if type == bool :
                    value[key] = 'True' == value[key]
                else :
                    value[key] = type(value[key])
    return data

def write_obj_to_file(file_path, data_p, separator='<|>') :
    data = data_p.copy()
    for value in data :
        for key in value.keys() :
            value[key] = str(value[key])
    data = [separator.join(list(value.values())) for value in data]
    write_file(file_path, '\n'.join(data))

### ----- Read / Write Objects ----- ###

def read_vocabulary(file_path) :
    file_content = read_file(file_path).split('\n')
    vocabulary = [ tuple(w.split('<|>')) for w in file_content if w and not w.isspace()]
    vocabulary = [ (w, int(c)) for w, c in vocabulary]
    return dict(vocabulary)


def write_vocabulary(file_path, vocabulary) :
    sorted_vocabulary = sorted(vocabulary.items(), key=lambda item: item[1])[::-1]
    file_content = '\n'.join([ w + '<|>' + str(c) for w, c in sorted_vocabulary])
    write_file(file_path, file_content)


from enum import Enum
LABELS = Enum('Label', ['SILENCE', 'SPEECH', 'HESITATION'])

def read_words_from_file(file_path) :
    return read_obj_from_file(file_path, keys=['transcript', 'start', 'end', 'score'], types=[str, int, int, float])

def write_words_to_file(file_path, data) :
    write_obj_to_file(file_path, data)


def read_label_timings_from_file(file_path) :
    return read_obj_from_file(file_path, keys=['word', 'annotation', 'pause_type', 'is_restart', 'start', 'end'], types=[str, str, str, bool, float, float])
    
def write_label_timings_to_file(file_path, data) :
    write_obj_to_file(file_path, data)


def read_timestamps_from_file(file_path) :
    return read_obj_from_file(file_path, keys=['start', 'end'], types=[float, float])
    
def write_timestamps_to_file(file_path, data) :
    write_obj_to_file(file_path, data)


