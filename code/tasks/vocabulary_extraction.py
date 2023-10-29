from collections import Counter
import re
import utils.file as utils
from progress.bar import ChargingBar
import utils.constants as constants

# common 5000: https://github.com/mahsu/IndexingExercise/blob/master/5000-words.txt


# word --> remove patters --> remove .,!? --> lower --> vocabulary
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
    english_most_commen = utils.read_file(constants.english_most_common).split('\n')
    common_limit = 100
    
    vocabulary = get_vocabulary(source_directory, patterns)
    pattern = re.compile("^[(a-zA-Z0-9'-\[\])_]+$")
    weird = []
    for w, c in vocabulary.items() :
        if not pattern.match(w) :
            weird.append(w)
    vocabulary = { w: c for w, c in vocabulary.items() if not w in weird }
    utils.write_vocabulary(destination_directory + "\\vocabulary.txt", vocabulary)
    common = {w: c for w, c in vocabulary.items() if c >= common_limit}
    utils.write_vocabulary(destination_directory + "\\vocabulary_common.txt", common)
    hesitations = {w: c for w, c in vocabulary.items() if hesitations_set.issuperset(set(w)) and w[-1] != '-' and w[0] != '-' and not w in english_most_commen}
    utils.write_vocabulary(destination_directory + "\\hesitations.txt", hesitations)
    stutter = {w: c for w, c in vocabulary.items() if w[-1] == '-' or w[0] == '-'}
    utils.write_vocabulary(destination_directory + "\\interruptions.txt", stutter)





