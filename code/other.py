from utils import constants
import utils.file as utils
import utils.constants as constants
from progress.bar import ChargingBar
import re
import os

# delete files
files = utils.get_directory_files(constants.segmented_transcript_dir, 'txt')
for file in files :
    f = str(file)
    content = utils.read_file(f)
    if not any(c.isalpha() for c in content) :
        print(file, content)
        os.remove(f)       # transcript
        os.remove(constants.segmented_speech_dir + f[len(constants.segmented_transcript_dir) : - 4] + '.wav')   # audio
        os.remove(constants.whisper_dir + f[len(constants.segmented_transcript_dir) : - 4] + '.txt')    # whisper transcript
        os.remove(constants.transcript_alignment_dir + f[len(constants.segmented_transcript_dir) : - 4] + '.txt')    # whisper transcript



def repretitions(directory, rep, patterns=[]) :
    files = utils.get_directory_files(directory, "txt")
    repetitions = []
    for file in ChargingBar("Collecting Vocabulary").iter(files) :
        content = utils.read_file(str(file))
        content = content.replace('\n', ' ')
        for pattern in patterns :
            content = re.sub(pattern, ' ', content)
        content = content.lower()
        content = content.split()
        for i in range(len(content) - rep + 1) :
            for j in range(1, rep) :
                if content[i] != content[i+j] :
                    break
            else :
                repetitions.append(content[i])
    print(set(repetitions))

# fisher_english_patterns = ["# Transcribed at the LDC", "# Transcribed by BBN/WordWave", "# fe_[0-9]{2}_[0-9]{5}.sph", "A:", "B:", "\t", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)", '\.', ',', '!', '\?']
# repretitions(constants.fe_transcripts, 5, fisher_english_patterns)