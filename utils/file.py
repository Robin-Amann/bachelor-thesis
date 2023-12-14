import torchaudio
import pathlib
import os
from pathlib import Path
import utils.constants as c
from pydoc import locate 


base_filter = lambda f : not (f.stem in c.controversial_files or f.stem[2:6] in c.ignore_files)


def get_dir_files(directory : str, filetype : str = 'txt', filter_condition = base_filter) -> list[Path]:
    pattern = "**\*." if os.name == 'nt' else "**/*."
    files = [f for f in pathlib.Path(directory).glob(pattern + filetype)]
    return [ f for f in files if filter_condition(f) ]


def get_multiple_dir_files(directories : list[tuple | Path | str], filter_condition = base_filter) -> list[list[tuple[Path]]]:
    for i, dir in enumerate(directories) :
        if type(dir) != tuple :
            directories[i] = (dir, 'txt')
    return [ get_dir_files(dir, filetype, filter_condition) for dir, filetype in directories ]


# def get_dir_tuples(directories : list[tuple | Path | str], base_condition, merge_conditions : list, filter_condition = base_filter) -> list[tuple]:
#     all_dirs_files = get_multiple_dir_files(directories, filter_condition)
#     # if all( [ len(all_dirs_files[0]) == len(all_dirs_files[i]) for i in range(1, len(all_dirs_files))] ) :
#     #     all_dirs_files = [ sorted(x) for x in all_dirs_files ]
#     #     return list(zip(*all_dirs_files))
#     base_dir_files = [ f for f in all_dirs_files[0] if base_condition(f) ]
#     other_dirs_files = all_dirs_files[1:]
#     result = []
#     for base_file in base_dir_files :
#         suitable_files = []
#         for files, condition in zip(other_dirs_files, merge_conditions) :
#             suitable = [ f for f in files if condition(base_file, f)]
#             if len(suitable) > 0 :
#                 if len(suitable) == 1 :
#                     suitable_files.append(suitable[0])
#                 else :
#                     suitable_files.append(suitable)
#         if len(suitable_files) == len(other_dirs_files) :
#             result.append( [base_file] + suitable_files)            
#     return result
                

# (dir) | (dir, merge) | (dir, merge, filter) | (dir, merge, filter, filetype)
def get_dir_tuples(dirs : list[tuple | Path | str], filter_condition=base_filter) -> list[tuple[Path | list]]:
    ''' 
    dirs -> list of: dir | (dir, merge) | (dir, merge, filter) | (dir, merge, filter, filetype)

    defaults: 
    - merge = lambda f: f.stem[2:10] dddd + A/B + ddd
    - filer = lambda f: True 
    - filetype = 'txt' 
    '''
    for index, dir in enumerate(dirs) :
        if type(dir) != tuple :
            dirs[index] = (dir, None, None, 'txt')
        if len(dir) == 2 : dirs[index] = (dir[0], dir[1], None, 'txt')
        if len(dir) == 3 : dirs[index] = (dir[0], dir[1], dir[2], 'txt')
    all_files = get_multiple_dir_files([ (d[0], d[3]) for d in dirs], filter_condition)
    filter_conditions = [dir[2] for dir in dirs]
    merge_conditions = [dir[1] for dir in dirs]
    all_files = [ filter(cond, files) for cond, files in zip([ c if c != None else lambda f: True for c in filter_conditions ], all_files) ]
    all_dicts = []
    all_keys = set()
    for files, condition in zip(all_files, [ c if c != None else lambda f: f.stem[2:10] for c in merge_conditions ]) :
        file_dict = dict()
        for file in files :
            key = condition(file)
            if key in file_dict :
                file_dict[key].append(file)
            else :
                file_dict[key] = [file]
                all_keys.add(key) 
        all_dicts.append(file_dict)

    result = []
    for k in sorted(list(all_keys)) :
        matches = []
        for d in all_dicts :
            if k in d : matches.append(d[k])
            else : break
        else :
            result.append(matches)

    result = [ tuple([files if len(files) > 1 else files[0] for files in matches]) for matches in result ]
    return result


def group_files(files, level) :
    grouped = list(map(lambda f :  {f[1].parts[- level] : f}, files))                       # map files to (parent, file)
    all_keys = [ list(g.keys())[0] for g in grouped ]
    all_keys = [ key for index, key in enumerate(all_keys) if not key in all_keys[:index] ]
    grouped = { key : [f[key] for f in grouped if key in f.keys() ] for key in all_keys}    # group files by parent
    return grouped


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
        print('audiofile does not exist', file_path)
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


def read_dict(file_path, seperator='<|>') :
    dictionary = []
    lines = read_file(file_path)
    if not lines :
        return dictionary
    lines = lines.split('\n')
    keys, types = lines[:2]
    keys = keys.split(seperator)
    types = [ locate(t) for t in types.split(seperator)]
    types = [ t if t != int else float for t in types ]
    data = lines[2:]
    for d in data :
        dictionary.append( dict(zip(keys, [ t(v) if t != bool else v == 'True' for t, v in zip(types, d.split(seperator)) ])) )
    return dictionary


def write_dict(file_path, data_p, separator='<|>') :
    data = data_p.copy()
    if type(data) != list or not all(type(item) == dict for item in data) :
        return
    if len(data) == 0 :
        write_file(file_path, '')
        return
    keys = list(data[0].keys())
    types = [type(data[0][key]).__name__ for key in keys ]
    types = [ t if t != int else float for t in types ]
    lines = [separator.join(keys), separator.join(types)]
    for value in data :
        line = []
        for key in keys :
            line.append(str(value[key]))
        lines.append( separator.join(line) )
    write_file(file_path, '\n'.join(lines))


def read_vocabulary(file_path) :
    file_content = read_file(file_path).split('\n')
    vocabulary = [ tuple(w.split('<|>')) for w in file_content if w and not w.isspace()]
    vocabulary = [ (w, int(c)) for w, c in vocabulary]
    return dict(vocabulary)


def write_vocabulary(file_path, vocabulary) :
    sorted_vocabulary = sorted(vocabulary.items(), key=lambda item: item[1])[::-1]
    file_content = '\n'.join([ w + '<|>' + str(c) for w, c in sorted_vocabulary])
    write_file(file_path, file_content)