from collections import Counter
import re
import utils.file as utils

# common 5000: https://github.com/mahsu/IndexingExercise/blob/master/5000-words.txt

def read_vocabulary(path) :
    file_content = utils.read_file(path).split('\n')
    vocabulary = [ tuple(w.split('|')) for w in file_content]
    vocabulary = [ (w, int(c)) for w, c in vocabulary]
    return dict(vocabulary)


def write_vocabulary(path, vocabulary) :
    sorted_vocabulary = sorted(vocabulary.items(), key=lambda item: item[1])[::-1]
    file_content = '\n'.join([ w + '|' + str(c) for w, c in sorted_vocabulary])
    utils.write_file(path, file_content)


def get_vocabulary(directory) :
    files = utils.get_directory_files(directory, "txt")
    vocabulary = dict()
    patterns = patterns=["A:", "B:", "\t", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)"]
    for file in files :
        content = utils.read_file(str(file))
        content = " ".join(content.split("\n")[2:])
        for pattern in patterns :
            content = re.sub(pattern, ' ', content)
        content = content.split()
        words = dict(Counter(content))
        for word, count in words.items() :
            if vocabulary.get(word) == None : 
                vocabulary[word] = count
            else :
                vocabulary[word] += count
    return vocabulary



# vocabulary = get_vocabulary("D:\\Robin_dataset\\fisher english\\transcripts")
# write_vocabulary("code\\sample_data\\vocabulary\\vocabulary.txt", vocabulary)


# common = {w: c for w, c in vocabulary.items() if c >= 100}
# write_vocabulary("code\\sample_data\\vocabulary\\vocabulary_common.txt", common)
# hesitations = {w: c for w, c in vocabulary.items() if superset.issuperset(set(w)) and w[-1] != '-' and w[0] != '-' and not w in english_most_commen}
# write_vocabulary("code\\sample_data\\vocabulary\\hesitations.txt", hesitations)
# stutter = {w: c for w, c in vocabulary.items() if w[-1] == '-' or w[0] == '-'}
# write_vocabulary("code\\sample_data\\vocabulary\\stutter.txt", stutter)


# superset = set("uhmoyaein-")
# english_most_commen = utils.read_file("code\\sample_data\\vocabulary\\english_most_commen_5000.txt").split('\n')
vocabulary = read_vocabulary("code\\sample_data\\vocabulary\\vocabulary.txt")
common = read_vocabulary("code\\sample_data\\vocabulary\\vocabulary_common.txt")
hesitations = read_vocabulary("code\\sample_data\\vocabulary\\hesitations.txt")
hesitations_eye = read_vocabulary("code\\sample_data\\vocabulary\\hesitations_by_eye.txt")
stutter = read_vocabulary("code\\sample_data\\vocabulary\\stutter.txt")

print("vocabulary:", sum([c for w, c in vocabulary.items()]))
print("common:", sum([c for w, c in common.items()]))
print("hesitations:", sum([c for w, c in hesitations.items()]))
print("hesitations eye:", sum([c for w, c in hesitations_eye.items()]))
print("stutter:", sum([c for w, c in stutter.items()]))



# word count:      words  occurence
# vocabulary:      65095 21.905.138
# common:           5278 21.380.013  97.60 %
# hesitations:       435  1.857.364   8.48 %
# hesitations eye:   110    824.366   3.76 %
# stutter:          6756    153.168   0.67 %




