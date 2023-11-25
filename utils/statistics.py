import utils.file as utils
import tasks.transcript_cleanup as pre
import tasks.transcript_alignment as alignment
from progress.bar import ChargingBar
import utils.constants as constants
import utils.alignment_metric as metric

def sb_hesitation_translation(manual_dir, automatic_dir, alignment_dir, hesitations_file = constants.hesitations_file, with_repetitions = True, min_len=1) :
    hesitations = list( utils.read_vocabulary(hesitations_file).keys() )

    # sw2005A000.txt, sw2005A000.txt, sw2005A000.txt  (names are equal)
    files = [(f.stem, f) for f in utils.get_directory_files(manual_dir, 'txt') if not 'Speech' in f.stem and not f.stem in constants.controversial_files and not f.stem[2:6] in constants.ignore_files]
    files = [ (s, f, utils.repath(f, manual_dir, automatic_dir), utils.repath(f, manual_dir, alignment_dir)) for (s, f) in files ]
    numbers = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    for stub, manual_file, automatic_file, alignment_file in ChargingBar("Aligning Transcripts").iter(files) :
        manual_full = utils.read_label_timings_from_file(manual_file)
        if len(manual_full) < min_len :
            continue
        manual_full = [ [w | {'word': wi} for wi in  w['word'].split()] for w in manual_full]
        manual_full = [item for sublist in manual_full for item in sublist]           
        operations = utils.read_file(alignment_file).split()
        automatic = ' '.join( [ w['word'] for w in utils.read_words_from_file(automatic_file) ] )
        manual = ' '.join([w['word'] for w in manual_full])
        _, manual = pre.process(transcript=manual.lower())
        _, whisper = pre.process(transcript=automatic.lower())
        manual, whisper = alignment.align(manual.split(), whisper.split(), operations)
        for i, x in enumerate(manual) :
            if not x :
                manual_full.insert(i, {'word' : ''})
        manual = manual_full

        if len(manual) != len(whisper) :
            continue

        for m, w in zip(manual, whisper) :
            if not m['word'] :  # nothing
                i = 2
            elif m['pause_type'] or (with_repetitions and m['is_restart']) :  # hesitation  (maybe just pause_type)
                i = 1
            else :  # word
                i = 0
            if not w :  # nothing
                j = 2
            elif w in hesitations or w[0] == '-' or w[-1] == '-' or (i == 1 and m == w):  # hesitation
                j = 1
            else :  # word
                j = 0

            numbers[i][j] += 1

    return numbers


# return list of (number of words, length of segment)
def segment_length(seg_dir, min_len=1) :
    files = [f for f in utils.get_directory_files(seg_dir, 'txt') if not 'Speech' in f.stem and not f.stem in constants.controversial_files and not f.stem[2:6] in constants.ignore_files]
    data = []
    total_length = 0 # in sec
    for f in files :
        content = utils.read_label_timings_from_file(f)
        if len(content) < min_len :
            continue
        data.append((len(content), content[-1]['end']))
        total_length += content[-1]['end']
    return data, total_length


# all, speech, repetitions, filled pauses, repetitions and filled pauses, hesitations
def wer(seg_dir, align_dir, min_len=1) :
    files = [f for f in utils.get_directory_files(seg_dir, 'txt') if not 'Speech' in f.stem and not f.stem in constants.controversial_files and not f.stem[2:6] in constants.ignore_files]
    files = [(f, utils.repath(f, seg_dir, align_dir)) for f in files]
    data = []
    wer_data = [ [0] * 4 for _ in range(6) ]

    for transcript_file, align_file in files :
        transcript = utils.read_label_timings_from_file(transcript_file)
        if len(transcript) < min_len :
            continue
        operations_all = utils.read_file(align_file).split()
        for index, op in enumerate(operations_all) :
            if op == 'i' :
                if index > 0 :
                    transcript.insert(index, transcript[index-1] | {'word' : ''})
                transcript.insert(index, {'word' : '', 'annotation' : '', 'pause_type' : '', 'is_restart' : False, 'start' : 0, 'end' : 0})
                    

        operations_speech = [ op for (op, w) in zip(operations_all, transcript) if not (w['pause_type'] or w['is_restart']) ]
        operations_rep = [op for (op, w) in zip(operations_all, transcript) if w['is_restart']]
        operations_pauses = [op for (op, w) in zip(operations_all, transcript) if w['pause_type'] ]
        operations_rep_and_pauses = [op for (op, w) in zip(operations_all, transcript) if w['pause_type'] and w['is_restart'] ]
        operations_hesitations = [op for (op, w) in zip(operations_all, transcript) if w['pause_type'] or w['is_restart'] ]
        
        d = []
        for index, ops in enumerate([operations_all, operations_speech, operations_rep, operations_pauses, operations_rep_and_pauses, operations_hesitations]) :
            wer = 0
            if len(ops) > 0 :
                wer = ( ops.count('d') + ops.count('i') + ops.count('r') ) / len(ops)
                wer_data[index][0] += ops.count('i')
                wer_data[index][1] += ops.count('d')
                wer_data[index][2] += ops.count('r')
                wer_data[index][3] += len(ops)
            d.append(wer)

        data.append(d)

    for i in range(6) :
        wer_data[i] = (wer_data[i][0] + wer_data[i][1] + wer_data[i][2]) / wer_data[i][3]
    return data, wer_data


# manual and automatic dir need alignment to audio information
def transcript_alignment(manual_dir, automatic_dir, align_dir, min_len=1) :
    
    files = [ f for f in utils.get_directory_files(manual_dir, 'txt') if not 'Speech' in f.stem and not f.stem in constants.controversial_files and not f.stem[2:6] in constants.ignore_files]
    files = [ (f, utils.repath(f, manual_dir, automatic_dir), utils.repath(f, manual_dir, align_dir) ) for f in files]

    data = []
    gaps = []
    empty_word = dict({'word' : '', 'start' : -1, 'end' : -1})
    for manual_file, automatic_file, align_file in files :
        operations = utils.read_file(align_file).split()
        manual = utils.read_label_timings_from_file(manual_file)
        if len(manual) < min_len :
            continue
        automatic = utils.read_words_from_file(automatic_file)
        if len(automatic) == 0 :
            print([w['word'] for w in manual])
        if len(automatic) > 1 :
            for i in range(len(automatic) - 1) :
                gap = automatic[i+1]['start'] - automatic[i]['end']
                gaps.append(gap)
        for index, op in enumerate(operations) :
            if op == 'i' :
                manual.insert(index, empty_word)
            elif op == 'd' :
                automatic.insert(index, empty_word)
        data.append(metric.alignment_error(manual, automatic))

    return data, gaps

def percentage(seg_dir, min_len=1) :
    files = [f for f in utils.get_directory_files(seg_dir, 'txt') if not 'Speech' in f.stem and not f.stem in constants.controversial_files and not f.stem[2:6] in constants.ignore_files]
    words = 0
    filled_pauses = 0
    repetitions = 0
    repetitions_and_filled_pauses = 0
    hesitations = 0
    for f in files :
        content = utils.read_label_timings_from_file(f)
        if len(content) < min_len :
            continue
        words += len(content)
        filled_pauses += len([ w for w in content if w['pause_type']])
        repetitions += len([ w for w in content if w['is_restart']])
        repetitions_and_filled_pauses += len([ w for w in content if w['pause_type'] and w['is_restart']])
        hesitations += len([ w for w in content if w['pause_type'] or w['is_restart']])
    return filled_pauses / words, repetitions / words, repetitions_and_filled_pauses / words, hesitations / words



