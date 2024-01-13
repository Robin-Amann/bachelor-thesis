import tasks.preprocessing.preprocessing as pre
import utils.constants as c
import tasks.transcript_alignment as wer
import utils.file as utils
from pathlib import Path
from progress.bar import ChargingBar
import utils.ignore_files as ignore

### find missing and corrupt audio files in dataset ###
# missing files
# corrupt audio files
# too short audio files
# switched files (audio, transcript)

# dirs
timing_dir = Path("D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts")
disfluencies_dir = Path("D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd") 
audio_dir = Path("D:\\Robin_dataset\\Switchboard\\LDC97S62 Switchboard-1 Release 2")
manual_seg_dir = c.manual_seg_dir

# switched timing, annotation through preprocessing

# corrupt audio files
def corrupt_audio_files() :
    corrupt_files = set() # swdddd
    all_audio_files = utils.get_dir_files(audio_dir, 'wav', filter_condition= lambda f : True)
    for file in ChargingBar("Corrupt Audio Files").iter(all_audio_files)  :
        try :
            utils.read_audio(file, 8000)
        except Exception :
            corrupt_files.add(file.stem[3:7])
    print('# corrupt_audio_files =', list(corrupt_files))
    return list(corrupt_files)


# missing files (disfluencies is complete)
def missing_files() :
    disfluencies_files = [f for f in utils.get_dir_files(disfluencies_dir, 'mgd', filter_condition= lambda f : True)]
    timing_files =       [f for f in utils.get_dir_files(timing_dir, 'text',      filter_condition= lambda f : True) if f.stem.endswith('word')]
    audio_files_A =      [f for f in utils.get_dir_files(audio_dir, 'wav',        filter_condition= lambda f : True) if f.stem.endswith('A') ]
    audio_files_B =      [f for f in utils.get_dir_files(audio_dir, 'wav',        filter_condition= lambda f : True) if f.stem.endswith('B') ]
    missing_files = set()
    timing_names = [ f.stem[2:7] for f in timing_files ]
    audio_A_names = [ f.stem[3:8] for f in audio_files_A ]
    audio_B_names = [ f.stem[3:8] for f in audio_files_B ]
    for file in ChargingBar('Missing files').iter(disfluencies_files) :
        name = file.stem[2:6]
        if not (name + "A") in timing_names :
            missing_files.add(name)
        if not (name + "B") in timing_names :
            missing_files.add(name)
        if not (name + "A") in audio_A_names :
            missing_files.add(name)
        if not (name + "B") in audio_B_names :
            missing_files.add(name)
    print('# missing_files =', list(missing_files))
    return list(missing_files)

# too short audio files
# assuming all files are present  
def to_short_audio_files() :
    too_short_files = set()
    files = utils.get_dir_tuples([(manual_seg_dir, lambda f: f.stem[2:7], lambda f : 'Speech' in f.stem), (audio_dir, lambda f: f.stem[3:8], lambda f : not f.stem[3:7] in ignore.corrupt_audio_files, 'wav')], filter_condition=lambda f: True)
    for segments_file, audio_file in ChargingBar('To Short').iter( files ) :
        segments = utils.read_dict(segments_file)
        audio = utils.read_audio(audio_file, 8000)[0]
        if segments[-1]['end'] > audio.size(0) / 8000 :
            too_short_files.add(segments_file.stem[2:6])
    print('# to_short_audio =', list(too_short_files))
    return list(too_short_files)

# audio with diffrent lengths
def audio_files_with_different_lengths() :
    notsamelen = list()
    files = utils.get_dir_tuples([(audio_dir, lambda f : f.stem[3:7], lambda f : not ('A' in f.stem or 'B' in f.stem), 'wav'), 
                                  (audio_dir, lambda f : f.stem[3:7], lambda f : 'A' in f.stem, 'wav'), 
                                  (audio_dir, lambda f : f.stem[3:7], lambda f : 'B' in f.stem, 'wav')], filter_condition= lambda f: not f.stem[3:7] in ignore.corrupt_audio_files)
    for x_f, a_f, b_f in ChargingBar("Audio Diffrent Lengths").iter(files) :
        x = utils.read_audio(x_f, 16000)
        a = utils.read_audio(a_f, 16000)
        b = utils.read_audio(b_f, 16000)
        if not (len(x[0]) == len(a[0]) == len(b[0])) :
            notsamelen.append(x_f.stem[3:7])
    print('# audio_diffrent_length =', notsamelen)
    return notsamelen

# switched files (audio, transcript)
def switched_audio_transcript() :
    import utils.wer_alignment as alignment
    files = utils.get_dir_tuples([(manual_seg_dir,     lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem and not f.stem[2:6] in ignore.ignore_files),
                                  (manual_seg_dir,     lambda f : f.stem[2:7], lambda f : not ('Speech' in f.stem or f.stem[2:6] in ignore.ignore_files)), 
                                  (c.automatic_v3_dir, lambda f : f.stem[2:7], lambda f : not f.stem[2:6] in ignore.ignore_files)])
    i = 0
    switched = set()
    for file, manuals, automatics in ChargingBar("Switched Audio Transcript").iter(files) :
        if len(manuals) != len(automatics) :
            print(file.stem)
            return
        manuals.sort()
        automatics.sort()
        manual = []
        automatic = []
        for manual_f, automatic_f in zip(manuals, automatic) :
            manual += utils.read_dict(manual_f)
            automatic += utils.read_dict(automatic_f)
            
        wer, operations = alignment.wer_and_ops([ word['word'] for word in manual ], [ word['word'] for word in automatic ])
        if len(operations) >= 5 and wer > 0.5:
            switched.add(manual_f.stem[2:6])
            manual, automatic, _ = alignment.align_words(manual, automatic, {'word' : ''})
            manual = [ word['word'] for word in manual ]
            automatic = [ word['word'] for word in automatic ]
            alignment.print_words(manual, automatic)            
            i += 1
            if i == 5:
                return    
    print('# audio_transcript_switched =', list(switched))
    return list(switched)

# may be switched(audio, transcript) or too much background noise
def controversial_audio_files() :
    import matplotlib
    import matplotlib.pyplot as plt
    files = utils.get_dir_tuples([(manual_seg_dir,   None, lambda f : not ('Speech' in f.stem or f.stem[2:6] in ignore.ignore_files) ), 
                                (c.automatic_v3_dir, None, lambda f : not f.stem[2:6] in ignore.ignore_files)])
    
    p = -25
    b = 8   
    normal = []
    controversial = []
    controversial_files = []
    for manual_f, automatic_f in ChargingBar("Finding Controversial Files").iter(files) :
        manual = utils.read_dict(manual_f)
        automatic = utils.read_dict(automatic_f)
        x = len(manual)
        y = len(automatic)
        if y > (p - b) / p * x + b or x > (p - b) / p * y + b :
            controversial.append( (x, y) )
            controversial_files.append((manual_f.stem, x, y, abs(x-y)))
        else :
            normal.append( (x, y) )
    
    matplotlib.rcParams["figure.figsize"] = [10, 10]
    plt.xlim((0, 150))
    plt.ylim((0, 150))
    x, y = list(zip(*normal))
    plt.scatter(x,y)
    x, y = list(zip(*controversial))
    plt.scatter(x,y, color='red')
    plt.xlabel('Manual (Ground Truth)')
    plt.ylabel('Automatic (Whisper)')
    plt.tight_layout()
    plt.show()

    controversial_files.sort(key=lambda x: x[3], reverse=True)
    for con in controversial_files[:20] :
        print(con)
    for i in range(20, 50) :
        print('# c' + str(i), '=', [ x[0] for x in controversial_files if int(x[0][2:4]) == i ])
    print('# controversial_files =', ' + '.join([ 'c' + str(i) for i in range(20, 50)]))

def find():
    # ignore.corrupt_audio_files += corrupt_audio_files()
    # ignore.ignore_files += ignore.corrupt_audio_files
    # ignore.missing_files += missing_files()
    # ignore.ignore_files += ignore.missing_files
    # ignore.to_short_audio += to_short_audio_files()
    # ignore.ignore_files += ignore.to_short_audio
    # ignore.audio_diffrent_length += audio_files_with_different_lengths()
    # ignore.ignore_files += ignore.audio_diffrent_length
    # ignore.switched_audio_transcript += switched_audio_transcript()
    # ignore.ignore_files += ignore.switched_audio_transcript
    controversial_audio_files()