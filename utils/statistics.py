import utils.file as utils
import tasks.transcript_cleanup as pre
import tasks.transcript_alignment as alignment
from progress.bar import ChargingBar
import utils.constants as constants
import utils.alignment_metric as metric
import os
import tasks.transcript_cleanup as cleanup


def sb_hesitation_translation(manual_dir, automatic_dir, alignment_dir, retranscribe_dir = None, hesitations_file = constants.hesitations_file, min_len=1) :
    hesitations = list( utils.read_vocabulary(hesitations_file).keys() )

    # sw2005A000.txt, sw2005A000.txt, sw2005A000.txt  (names are equal)
    if retranscribe_dir:
        files = utils.dir_tuples_simple([manual_dir, automatic_dir, retranscribe_dir, alignment_dir], lambda f : not 'Speech' in f.stem )
        files = [ (f1, (f2, f3), f4) for f1, f2, f3, f4 in files ]
    else :
        files = utils.dir_tuples_simple([manual_dir, automatic_dir, alignment_dir], lambda f : not 'Speech' in f.stem )
    

    numbers = [[0, 0, 0], [0, 0, 0]]
    for manual_file, automatic_file, alignment_file in ChargingBar("Hesitation Transcription").iter(files) :
        manual_full = utils.read_label_timings_from_file(manual_file)
        if len(manual_full) < min_len :
            continue
        manual_full = [ [w | {'word': wi} for wi in  w['word'].split()] for w in manual_full]
        manual_full = [item for sublist in manual_full for item in sublist]           
        operations = utils.read_file(alignment_file).split()
        if retranscribe_dir :
            automatic_file, retranscribe_file = automatic_file
            t = utils.read_words_from_file(automatic_file) + [ w for w in utils.read_complementary_words_from_file(retranscribe_file) if w['word']]
            t = sorted(t, key=lambda w: w['start'])
            automatic = ' '.join( w['word'] for w in t) 
        else :
            automatic = ' '.join( w['word'] for w in utils.read_words_from_file(automatic_file) )
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
            if not m['word'] :
                continue
            if m['pause_type']  :  # pause type and maybe restart
                i = 0
            elif m['is_restart'] : # just restart
                i = 1
            else :
                continue
            if not w :  # nothing
                numbers[i][2] += 1
            elif w in hesitations or w[0] == '-' or w[-1] == '-' or (i == 1 and m == w):  # hesitation
                numbers[i][1] += 1
            else :  # word
                numbers[i][0] += 1

    for i, x in enumerate(numbers[0]) :
        numbers[1][i] += x
    return numbers


# return list of (number of words, length of segment)
def segment_length(seg_dir, min_len=1) :
    files = utils.dir_tuples_simple([seg_dir], lambda f : not 'Speech' in f.stem )
    data = []
    total_length = 0 # in sec
    for f in files :
        content = utils.read_label_timings_from_file(f)
        if len(content) < min_len :
            continue
        data.append((len(content), content[-1]['end']))
        total_length += content[-1]['end']
    return data, total_length


# all
def wer(manual_dir, automatic_dir, retranscribe_dir=None, min_len=1) :
    files = utils.dir_tuples_simple([manual_dir, automatic_dir], lambda f : not 'Speech' in f.stem)
    data = []

    for manual_f, automatic_f in files :
        manual = ' '.join( w['word'] for w in utils.read_label_timings_from_file(manual_f) )
        if len(manual.split()) < min_len :
            continue
        if retranscribe_dir :
            retranscribe_f = utils.repath(manual_f, manual_dir, retranscribe_dir)
            if not os.path.isfile(retranscribe_f) :
                continue
            t = utils.read_words_from_file(automatic_f) + [ w for w in utils.read_complementary_words_from_file(retranscribe_f) if w['word']]
            t = sorted(t, key=lambda w: w['start'])
            automatic = ' '.join( w['word'] for w in t)
        else :
            automatic = ' '.join( w['word'] for w in utils.read_words_from_file(automatic_f) )

        _, manual = cleanup.process(manual)
        _, automatic = cleanup.process(automatic)
        ops = alignment.get_operations(manual.split(), automatic.split())
        wer = ( ops.count('d') + ops.count('i') + ops.count('r') ) / len(ops)
        data.append((wer, len(ops)))

    l = 0
    wer = 0
    dist = []
    for wer_i, length in data :
        wer += wer_i * length
        l += length
        dist.append(wer_i)
    wer = wer / l
    return dist, wer


# manual and automatic dir need alignment to audio information
def transcript_alignment(manual_dir, automatic_dir, align_dir, min_len=1) :
    files = utils.dir_tuples_simple([manual_dir, automatic_dir, align_dir], lambda f : not 'Speech' in f.stem)

    data = []
    gaps = []
    empty_word = dict({'word' : '', 'start' : -1, 'end' : -1})
    for manual_file, automatic_file, align_file in files :
        operations = utils.read_file(align_file).split()
        manual = utils.read_label_timings_from_file(manual_file)
        if len(manual) < min_len :
            continue
        automatic = utils.read_words_from_file(automatic_file)
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
    files = utils.dir_tuples_simple([seg_dir], lambda f : not 'Speech' in f.stem )
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



