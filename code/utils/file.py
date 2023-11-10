import torchaudio
import pathlib
import os

def get_directory_files(directory, filetype) :
    system = os.name
    pattern = "**/*."
    if system == 'nt' :
        pattern = "**\*."
    files = [f for f in pathlib.Path(directory).glob(pattern + filetype)]    
    return files


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


def read_file(path) :
    content = ""
    with open(path, "r", encoding="utf8") as file :
        content = file.read()
    return content


def write_file(path, content, mode='w') :
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding='utf8') as file :
        file.write(content)



def read_obj_from_file(file_path, keys, types = [], separator='|') :
    content = read_file(file_path)
    lines = content.split('\n')
    data = [dict(zip(keys, line.split(separator))) for line in lines]
    if types :
        bundle = list(zip(keys, types))
        for value in data :
            for key, type in bundle :
                value[key] = type(value[key])
    return data

def write_obj_to_file(file_path, data_p, separator='|') :
    data = data_p.copy()
    for value in data :
        for key in value.keys() :
            value[key] = str(value[key])
    data = [separator.join(list(value.values())) for value in data]
    write_file(file_path, '\n'.join(data))

    
def read_vocabulary(path) :
    file_content = read_file(path).split('\n')
    vocabulary = [ tuple(w.split('|')) for w in file_content if w and not w.isspace()]
    vocabulary = [ (w, int(c)) for w, c in vocabulary]
    return dict(vocabulary)


def write_vocabulary(path, vocabulary) :
    sorted_vocabulary = sorted(vocabulary.items(), key=lambda item: item[1])[::-1]
    file_content = '\n'.join([ w + '|' + str(c) for w, c in sorted_vocabulary])
    write_file(path, file_content)


from enum import Enum
LABELS = Enum('Label', ['SILENCE', 'SPEECH', 'HESITATION'])

def read_audio_labels_from_file(file_path) :
    segments = read_file(file_path)
    segments = segments.split('\n')
    segments = [tuple(l.split('|')) for l in segments]
    segments = [ { 'label' : LABELS[label], 'start' : int(start), 'end' : int(end)} for label, start, end in segments ]
    return segments


def write_audio_labels_to_file(audio_file, segments) :
    segments = [seg['label'].name + '|' + str(seg['start']) + '|'+ str(seg['end']) for seg in segments]
    segments = '\n'.join(segments)
    write_file(audio_file[:-4] + ".txt", segments)


def read_words_from_file(file_path) :
    words = read_file(file_path)
    words = words.split('\n')
    words = [tuple(l.split('|')) for l in words]
    words = [ { 'transcript' : transcript, 'start' : int(start), 'end' : int(end), 'score' : float(score) } for transcript, start, end, score in words ]
    return words


def write_words_to_file(words, destination_file) :
    words = [word['transcript'] + '|' + str(word['start']) + '|'+ str(word['end']) + '|' + str(word['score']) for word in words]
    words = '\n'.join(words)
    write_file(destination_file, words)


def read_label_timings_from_file(file_path) :
    return read_obj_from_file(file_path, keys=['word', 'annotation', 'pause_type', 'is_restart', 'start', 'end'], types=[str, str, str, bool, float, float], separator='|')
    

# word, annotation, pause_type, is_restart, start, end
def write_label_timings_to_file(file_path, data) :
    write_obj_to_file(file_path, data, separator='|')


def read_timestamps_from_file(file_path) :
    return read_obj_from_file(file_path, keys=['start', 'end'], types=[float, float])
    

# word, annotation, pause_type, is_restart, start, end
def write_timestamps_to_file(file_path, data) :
    write_obj_to_file(file_path, data)


def get_dir_tuples(dir_list, type_list, conditions, merge_condition) :
    all_files = []
    for d, t, c in zip(dir_list, type_list, conditions) :
        files = get_directory_files(d, t)
        files = [(f.stem, f) for f in files if c(f.stem)]
        all_files.append(files)
    tuples = []
    for f in all_files[0] :
        suitable = []
        for files in all_files[1 : ] :
            suitable.append([x for x in files if merge_condition(f[0], x[0])])
        if all(len(x) > 0 for x in suitable) :
            tuples.append((f, *suitable))
    return tuples
