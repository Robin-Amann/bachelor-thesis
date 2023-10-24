from collections import Counter
import re
import utils.file as utils
from progress.bar import ChargingBar

# common 5000: https://github.com/mahsu/IndexingExercise/blob/master/5000-words.txt


def get_vocabulary(directory, patterns=[]) :
    files = utils.get_directory_files(directory, "txt")
    vocabulary = dict()
    for file in ChargingBar("Collecting Vocabulary").iter(files) :
        content = utils.read_file(str(file))
        content = content.replace('\n', ' ')
        for pattern in patterns :
            content = re.sub(pattern, ' ', content)
        content = content.lower()
        content = content.split()
        words = dict(Counter(content))
        for word, count in words.items() :
            if vocabulary.get(word) == None : 
                vocabulary[word] = count
            else :
                vocabulary[word] += count
    return vocabulary


def get_vocabulary_set(source_directory, destination_directory, patterns=[], hesitations_set=set("uhmoyaein-")) :
    english_most_commen = utils.read_file("code\\sample_data\\vocabulary\\english_most_commen_5000.txt").split('\n')
    common_limit = 100
    
    vocabulary = get_vocabulary(source_directory, patterns)
    utils.write_vocabulary(destination_directory + "\\vocabulary.txt", vocabulary)
    common = {w: c for w, c in vocabulary.items() if c >= common_limit}
    utils.write_vocabulary(destination_directory + "\\vocabulary_common.txt", common)
    hesitations = {w: c for w, c in vocabulary.items() if hesitations_set.issuperset(set(w)) and w[-1] != '-' and w[0] != '-' and not w in english_most_commen}
    utils.write_vocabulary(destination_directory + "\\hesitations.txt", hesitations)
    stutter = {w: c for w, c in vocabulary.items() if w[-1] == '-' or w[0] == '-'}
    utils.write_vocabulary(destination_directory + "\\stutter.txt", stutter)



# vocabulary = read_vocabulary("code\\sample_data\\vocabulary\\vocabulary.txt")
# common = read_vocabulary("code\\sample_data\\vocabulary\\vocabulary_common.txt")
# hesitations = read_vocabulary("code\\sample_data\\vocabulary\\hesitations.txt")
# hesitations_eye = read_vocabulary("code\\sample_data\\vocabulary\\hesitations_by_eye.txt")
# stutter = read_vocabulary("code\\sample_data\\vocabulary\\stutter.txt")
# print("vocabulary:",      len(vocabulary),      sum([c for w, c in vocabulary.items()]))
# print("common:",          len(common),          sum([c for w, c in common.items()]))
# print("hesitations:",     len(hesitations),     sum([c for w, c in hesitations.items()]))
# print("hesitations eye:", len(hesitations_eye), sum([c for w, c in hesitations_eye.items()]))
# print("stutter:",         len(stutter),         sum([c for w, c in stutter.items()]))





