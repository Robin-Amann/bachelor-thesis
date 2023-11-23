import tasks.preprocessing.preprocessing as pre
import utils.constants as c
import tasks.transcript_alignment as wer
import utils.file as utils
from pathlib import Path
from progress.bar import ChargingBar

### find missing and corrupt audio files in dataset ###

timing_dir = "D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts"
disfluencies_dir = "D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd" 
audio_dir = "D:\\Robin_dataset\\Switchboard\\LDC97S62 Switchboard-1 Release 2"

disfluencies_files = [f.stem for f in utils.get_directory_files(disfluencies_dir, 'mgd')]
timing_files = [f.stem[:7] for f in utils.get_directory_files(timing_dir, 'text') if f.stem.endswith('word')]
audio_files_A = [f.stem[:2] + f.stem[3:7] for f in utils.get_directory_files(audio_dir, 'wav') if f.stem.endswith('A') ]
audio_files_B = [f.stem[:2] + f.stem[3:7] for f in utils.get_directory_files(audio_dir, 'wav') if f.stem.endswith('B') ]
audio_files = [f for f in utils.get_directory_files(audio_dir, 'wav') if f.stem.endswith('B') or f.stem.endswith('A') ]

corrupt_files = []
for f in ChargingBar("Read Audio").iter(audio_files)  :
    try :
        utils.read_audio(f, 8000)
    except Exception :
        corrupt_files.append(f.stem[0:2] + f.stem[3:7])

missing_files = []
for stem in disfluencies_files :
    if not (stem + "A") in timing_files :
        missing_files.append(stem)
    if not (stem + "B") in timing_files :
        missing_files.append(stem)
    if not stem in audio_files_A :
        missing_files.append(stem)
    if not stem in audio_files_B :
        missing_files.append(stem)

print("missing:", missing_files)
print("corrupt:", corrupt_files)
print("ignore: ", [f[2:] for f in list(set(missing_files + corrupt_files))] )



pre.process_dir("D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd", "D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts\\word alignments", "", ann_patterns=c.manual_annotation_patterns)

audio_dir = "D:\\Robin_dataset\\Switchboard\\LDC97S62 Switchboard-1 Release 2"
files = [ f for f in utils.get_directory_files(audio_dir, 'wav') if len(f.stem) == 7]
files = [ (f, Path(f.parent) / (f.stem + "A.wav"), Path(f.parent) / (f.stem + "B.wav") ) for f in files]

corrupt = list()
notsamelen = list()
for x_f, a_f, b_f in ChargingBar("Segment Audio and Transcripts").iter(files) :
    try :
        x = utils.read_audio(x_f, 16000)
        a = utils.read_audio(a_f, 16000)
        b = utils.read_audio(b_f, 16000)
        if not (len(x[0]) == len(a[0]) == len(b[0])) :
            notsamelen.append(x_f.stem)
    except Exception :
        corrupt.append(x_f.stem)

print(corrupt)
print(notsamelen)

dis_file = "D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd\\2\\sw2485.mgd"
word_timing_file_A = "D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts\\word alignments\\24\\2485\\sw2485A-ms98-a-word.text"
word_timing_file_B = "D:\\Robin_dataset\\Switchboard\\\Switchboard-1 Release 2 Transcripts\\word alignments\\24\\2485\\sw2485B-ms98-a-word.text"

trans, timing = pre.process_file(dis_file, word_timing_file_A, word_timing_file_B, c.manual_annotation_patterns )

operations = wer.get_operations([w['word'].lower() for w in trans], [w['word'].lower() for w in timing])
trans_aligned, timing_aligned = wer.align(trans, timing, operations, insertion_obj=dict())
trans_aligned = [w['word'] if 'word' in w else '' for w in trans_aligned ]
timing_aligned = [w['word'] if 'word' in w else '' for w in timing_aligned ]

for i in range( int(len(trans_aligned) / 30 + 1)) :
    wer.print_words(trans_aligned[30*i : 30*(i+1)], timing_aligned[30*i : 30*(i+1)])
    print()

import matplotlib.pyplot as plt
import numpy as np
import utils.constants as c
import utils.file as utils

files = [f for f in utils.get_directory_files(c.manual_seg_dir, 'txt') if not 'Speech' in f.stem]
files = [(f, utils.repath(f, c.manual_seg_dir, c.audio_automatic_align_dir), utils.repath(f, c.manual_seg_dir, c.transcript_align_dir)) for f in files]

data = []
corrupt = set()
for manual_f, automatic_f, operations_f in files :
    m = len(utils.read_label_timings_from_file(manual_f))
    a = len(utils.read_words_from_file(automatic_f))
    operations = utils.read_file(operations_f).split()
    if len(operations) >= 5 and ((operations.count('i') + operations.count('d') + operations.count('r')) / len(operations)) > 0.5:
        corrupt.add(manual_f.stem[2:6])
    data.append( (m, a) )
    if abs(m - a) > 50 :
        print(manual_f, automatic_f)
        print(m, a)
        print()

print(corrupt)
data = list(set(data))
x, y =  list(map(list, zip(*data)))


maximum = max(max(x), max(y))
minimum = min(min(x), min(y))

p = -15
b = 5

plt.scatter(x, y)
plt.plot([minimum, maximum], [(p - b) / p * minimum + b, (p - b) / p * maximum + b], color='red')
plt.plot([minimum, maximum], [p / (p - b) * minimum - p / (p - b) * b, p / (p - b) * maximum - p / (p - b) * b], color='red')
plt.xlim(minimum, maximum)
plt.ylim(minimum, maximum)
plt.tight_layout()
plt.show()



### length of segments and translations

import utils.constants as c
import utils.file as utils
import matplotlib.pyplot as plt
import tasks.transcript_alignment as wer


files = [f for f in utils.get_directory_files(c.manual_seg_dir, 'txt') if not 'Speech' in f.stem and f.stem[2:6] not in c.ignore_files]
files = [(f, utils.repath(f, c.manual_seg_dir, c.audio_automatic_align_dir), utils.repath(f, c.manual_seg_dir, c.transcript_align_dir)) for f in files]

data = []

for manual_f, automatic_f, operations_f in files :
    x = len(utils.read_label_timings_from_file(manual_f))
    y = len(utils.read_words_from_file(automatic_f))
    data.append( (x, y) )

data = list(set(data))
x, y =  list(map(list, zip(*data)))

maximum = max(max(x), max(y))
minimum = min(min(x), min(y))

p = -25
b = 8

plt.scatter(x, y)
plt.plot([minimum, maximum], [(p - b) / p * minimum + b, (p - b) / p * maximum + b], color='red')
plt.plot([minimum, maximum], [p / (p - b) * minimum - p / (p - b) * b, p / (p - b) * maximum - p / (p - b) * b], color='red')
plt.xlim(minimum, maximum)
plt.ylim(minimum, maximum)
plt.tight_layout()
plt.show()