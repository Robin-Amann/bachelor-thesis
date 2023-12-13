import torchaudio
import pathlib
import os
from pathlib import Path
import utils.constants as c
from pydoc import locate 


def get_directory_files(directory, filetype) :
    pattern = "**\*." if os.name == 'nt' else "**/*."
    files = [f for f in pathlib.Path(directory).glob(pattern + filetype)]    
    return files

def _get_dir_tuples(dir_list, type_list, conditions, merge_condition) :
    all_files = []
    for d, t, c in zip(dir_list, type_list, conditions) :
        files = get_directory_files(d, t)
        files = [(f.stem, f) for f in files if c(f.stem)]
        all_files.append(files)
    tuples = []
    if type(merge_condition) != list :
            mc = [merge_condition] * len(dir_list)
    else :
        mc = merge_condition
    for f in all_files[0] :
        suitable = []
        for files, m in zip(all_files[1 : ], mc[1 : ]) :
            suitable.append([x for x in files if m(f[0], x[0])])
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
    if len(args) == 1 : # [ {dir, type, condition, merge} ]
        dir_list = [d[0] for d in args[0]]
        type_list = [d[1] for d in args[0]]
        conditions = [d[2] for d in args[0]]
        merge_condition = [d[3] for d in args[0]]
        return _get_dir_tuples(dir_list, type_list, conditions, merge_condition)


def dir_tuples_simple(dirs, condition = lambda f : True, filter = lambda f : not (f.stem in c.controversial_files or f.stem[2:6] in c.ignore_files) ) :
    if type(dirs[0]) != list : dirs = [ [d] for d in dirs]
    for d in dirs :
        if len(d) == 1 : d.append('txt')
        if len(d) == 2 : d.append(lambda s: s)
    # dir, fileype, name_translation
    all_files = [[f] for f in get_directory_files(dirs[0][0], dirs[0][1]) if condition(f) and filter(f)]
    for dir in dirs[1:] :
        for files in all_files :
            files.append( repath(files[0], dirs[0][0], dir[0], stem=dir[2](files[0].stem), suffix= '.' + dir[1]) )
    all_files = [ files for files in all_files if all( [ os.path.isfile(str(f)) for f in files ] )]
    if len(all_files[0]) == 1 :
        all_files = [ f[0] for f in all_files ]
    return all_files
        

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
    data = [dict(zip(keys, line.split(separator))) for line in lines if line]     ## if line --> for empty lines (empty file)
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


def write_dict(file_path, data_p, separator='<|>') :
    data = data_p.copy()
    if type(data) != list or not all(type(item) == dict for item in data) :
        return
    if len(data) == 0 :
        write_file(file_path, '')

    keys = list(data[0].keys())
    types = [type(data[0][key]).__name__ for key in keys ]
    lines = [separator.join(keys), separator.join(types)]
    for value in data :
        line = []
        for key in keys :
            line.append(str(value[key]))
        lines.append( separator.join(line) )
    write_file(file_path, '\n'.join(lines))


def read_dict(file_path, seperator='<|>') :
    dictionary = []
    lines = read_file(file_path)
    if not lines :
        return dictionary
    lines = lines.split('\n')
    keys, types = lines[:2]
    keys = keys.split(seperator)
    types = [ locate(t) for t in types.split(seperator)]
    data = lines[2:]
    for d in data :
        dictionary.append( dict(zip(keys, [ t(v) if t != bool else v == 'True' for t, v in zip(types, d.split(seperator)) ])) )
    return dictionary


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


def read_words_from_file(file_path) :
    return read_obj_from_file(file_path, keys=['word', 'start', 'end', 'score'], types=[str, float, float, float])

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


def read_complementary_words_from_file(file_path) :
    return read_obj_from_file(file_path, keys=['word', 'start', 'end'], types=[str, float, float])

def write_complementary_words_to_file(file_path, data) :
    write_obj_to_file(file_path, data)