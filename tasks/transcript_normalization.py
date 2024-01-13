from nemo_text_processing.text_normalization.normalize import Normalizer
import utils.file as utils
import utils.transcript as word_utils
from progress.bar import ChargingBar

def normalize_file(file_path, normalizer = None, filename_extention = None) :
    if normalizer == None :
        normalizer = Normalizer(input_case='cased', lang='en')

    transcript = utils.read_file(file_path)
    transcript = normalizer.normalize(transcript, punct_post_process=True)
    write = utils.write_file

    if filename_extention != None:
        write(file_path[:-4] + "_" + filename_extention + ".txt", transcript)
    else :
        write(file_path, transcript)
    
    

def normalize_dir(directory_path, filename_extention = None) :
    files = [ f for f in utils.get_dir_files(directory_path, "txt") if not 'Speech' in f.stem ]
    normalizer = Normalizer(input_case='cased', lang='en')
    for file in ChargingBar("Normalize Transcript").iter(files) :
        normalize_file(str(file), normalizer, filename_extention)    


import re

def before_normalization(old_dir, new_dir) :
    files = utils.get_dir_files(old_dir, filter_condition=lambda f: True)
    j = 0
    for file in files :
        words = [ w['word'] for w in utils.read_dict(file) ]
        i = 0
        while i < len(words) - 1 :
            if re.search('[0-9]', words[i]) and re.search('[0-9]', words[i+1]) :
                if ('$' in words[i] and not '$' in words[i+1]) or words[i+1].startswith(',000') or words[i+1].startswith('.'):
                    x = words[i] + words[i+1]
                    print(x.ljust(15), end='')
                    j += 1
                    if j % 15 == 0 :
                        print()
                    words = words[:i] + [x] + words[i+2:]
                    continue
            i += 1
        new_file = utils.repath(file, old_dir, new_dir)
        utils.write_file(new_file, ' '.join(words))


# go through non-words missed by normalizer and correct them by hand
def after_normalization(old_dir, new_dir, radius = 2) :
    files = utils.get_dir_files(old_dir, filter_condition=lambda f: True)
    changed_files = set()
    incidents = 0
    for file in files :
        words = utils.read_file(file).split()
        incidents += len( [ word for word in words if not word_utils.simplify(word) ])
    print('number of words to be corrected:', incidents)
    
    print('continue? (y/n)', end=' ')
    if input() == 'y' :
        for file in files :
            words = utils.read_file(file).split()
            for i, word in enumerate(words) :
                if not word_utils.simplify(word) :
                    if i > 0 :
                        print(' '.join(words[max(0, i-radius):i]), end='')
                    print(' >', words[i], '< ', sep='', end='')
                    if i < len(words)-1 :
                        print(' '.join(words[i+1: i+1+radius]))
                    user_input = input()
                    if user_input == '>>end<<' :
                        break
                    if user_input :
                        words[i] = user_input
                        changed_files.add(file[2:10])
            else :
                new_file = utils.repath(file, old_dir, new_dir)
                utils.write_file(new_file, ' '.join(words))
                continue
            break
        changed_files = list(changed_files)
        changed_files.sort()
        print(changed_files)