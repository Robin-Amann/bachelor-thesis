import utils.file as utils
import tasks.preprocessing.preprocessing as pre
import tasks.transcript_alignment as alignment
from progress.bar import ChargingBar
import utils.constants as constants


def sb_hesitation_translation(manual_dir, automatic_dir, alignment_dir, hesitations_file = constants.hesitations) :
    hesitations = list( utils.read_vocabulary(hesitations_file).keys() )
    # sw2005A000.txt, sw2005A000.txt, sw2005A000.txt                                                                                                          names are equal
    files = utils.get_dir_tuples([manual_dir, automatic_dir, alignment_dir], ['txt', 'txt', 'txt'], [lambda s : not 'Speech' in s, lambda s : True, lambda s : True], lambda l, ln : l == ln)
    files = [(stub, f0, f1[0][1], f2[0][1]) for (stub, f0), f1, f2 in files]
    numbers = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    for stub, manual_file, automatic_file, alignment_file in ChargingBar("Aligning Transcripts").iter(files) :
        manual_full = utils.read_label_timings_from_file(manual_file)
        automatic = utils.read_file(automatic_file).lower()
        operations = utils.read_file(alignment_file).split()
        manual = [w['word'].lower() for w in manual_full]
        whisper, _ = pre.process(transcript=automatic, patterns=['\.', ',', '\?', '!'])
        manual, whisper = alignment.align(manual, whisper.split(), operations)
        for i, x in enumerate(manual) :
            if not x :
                manual_full.insert(i, {'word' : ''})
        manual = manual_full

        if len(manual) != len(whisper) :
            print(stub)
            continue

        for m, w in zip(manual, whisper) :
            if not m['word'] :  # nothing
                i = 2
            elif m['pause_type'] or m['is_restart'] :  # hesitation
                i = 1
            else :  # word
                i = 0
            if not w :  # nothing
                j = 2
            elif w in hesitations or w[0] == '-' or w[-1] == '-' :  # hesitation
                j = 1
            else :  # word
                j = 0
            numbers[i][j] += 1
        print(manual)
        print(whisper)
        break

    for n in numbers :
        print(n)
