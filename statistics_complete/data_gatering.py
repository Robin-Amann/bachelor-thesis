import utils.file as utils
import utils.wer_alignment as alignment
import utils.constants as c
import utils.alignment_metric as metric
import utils.transcript as word_utils

from progress.bar import ChargingBar
from pathlib import Path
import random
import shutil
import os


# # #   after preprocessing    # # #
def manual_segment_length(manual_dir, min_len=1, filter_condition = utils.base_filter) :
    'returns [ (length by words, length by time) ]'
    files = utils.get_dir_tuples([
        (manual_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), 
        (manual_dir, lambda f : f.stem[2:7], lambda f : not 'Speech' in f.stem)], 
        filter_condition=filter_condition)
    
    data = []
    for length_f, manual_files in ChargingBar('segment lengths').iter(files) :
        segments = utils.read_dict(length_f)
        for index, segment in enumerate(segments) :
            manual_f = next( iter(f for f in manual_files if (length_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            if not manual_f : continue    # is a contraversial file
            manual = utils.read_dict(manual_f) 
            if len(manual) < min_len :
                continue

            length = segment['end'] - segment['start']
            data.append( (len(manual), length) )
    return data


def hesitation_percentages(seg_dir, min_len=1) :
    files = [ f for f in utils.get_dir_files(seg_dir, 'txt') if not 'Speech' in f.stem ]
    words, filled_pauses, repetitions, repetitions_and_filled_pauses, hesitations = (0, 0, 0, 0, 0)
    for f in ChargingBar('percentages').iter(files) :
        content = utils.read_dict(f)
        if len(content) < min_len :
            continue
        words += len(content)
        filled_pauses += len([ w for w in content if w['pause_type']])
        repetitions += len([ w for w in content if w['is_restart']])
        repetitions_and_filled_pauses += len([ w for w in content if w['pause_type'] and w['is_restart']])
        hesitations += len([ w for w in content if w['pause_type'] or w['is_restart']])
    return filled_pauses / words, repetitions / words, repetitions_and_filled_pauses / words, hesitations / words


# # #   after transcription    # # #
def segment_length(manual_dir, automatic_dir, automatic_aligned=False, hesitation_dir=None, min_len=1, filter_condition = utils.base_filter) :
    'returns [( length manual in words, length automatic in words), audio length]'
    files = utils.get_dir_tuples([
        (manual_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), 
        (manual_dir, lambda f : f.stem[2:7], lambda f : not 'Speech' in f.stem),
        (automatic_dir, lambda f : f.stem[2:7])], filter_condition=filter_condition)
    if hesitation_dir :
        hesitation_files = [ f for f in utils.get_dir_files(hesitation_dir, 'txt', filter_condition=filter_condition) ]

    data = []
    for length_f, manual_files, automatic_files in ChargingBar('segment lengths').iter(files) :

        segments = utils.read_dict(length_f)
        for index, segment in enumerate(segments) :
            manual_f = next( iter(f for f in manual_files if (length_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            if not manual_f : continue    # is a contraversial file
            manual = utils.read_dict(manual_f) 
            if len(manual) < min_len :
                continue
            automatic_f = next( iter(f for f in automatic_files if (length_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None )
            if not automatic_f :
                print(manual_f.stem)
                continue
            if automatic_aligned :
                automatic = utils.read_dict(automatic_f)
            else :
                automatic = utils.read_file(automatic_f).split()
            if hesitation_dir :
                hesitation_f = next( f for f in hesitation_files if automatic_f.stem == f.stem )
                automatic += utils.read_dict(hesitation_f)

            length = segment['end'] - segment['start']
            data.append( (( len(manual), len(automatic)), length) )
    return data


def calculate_wer(manual_dir, automatic_dir, automatic_aligned=False, min_len=1, hesitation_dir=None) :
    'returns [ (wer, ops) for segment ], wer'
    if hesitation_dir :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir, hesitation_dir])
        files = [ (f1, (f2, f3)) for f1, f2, f3 in files ]
    else :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])

    wer_data = []
    for manual_f, automatic_f in ChargingBar('WER').iter(files) :
        manual = utils.read_dict(manual_f)
        if len(manual) < min_len :
            continue
        if hesitation_dir :
            automatic_f, hesitation_f = automatic_f
        if automatic_aligned :
            automatic = utils.read_dict(automatic_f)
            if hesitation_dir :
                automatic += utils.read_dict(hesitation_f)
                automatic.sort(key=lambda w : w['start'])

            wer, ops = alignment.wer_and_ops([ w['word'] for w in manual ], [ w['word'] for w in automatic ])
        else :
            automatic = utils.read_file(automatic_f).split()
            wer, ops = alignment.wer_and_ops([ w['word'] for w in manual ], automatic)
        
        wer_data.append((wer, ops))
    
    return wer_data , sum( [wer * len(ops) for wer, ops in wer_data] ) / sum( [len(ops) for wer, ops in wer_data] )


def gaps_containing_speech_manual_time(manual_dir, automatic_dir) :
    files = utils.get_dir_tuples([(manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])
    gaps = []
    for manual_f, automatic_f in ChargingBar('gaps').iter(files) :
        manual = utils.read_dict(manual_f)
        automatic = [ {'word' : w} for w in utils.read_file(automatic_f).split() ]
        
        manual, automatic, _ = alignment.align_words(manual, automatic, insertion_obj={'word' : ''})
        start = 0
        in_gap = False
        i = 0
        while i < len(manual) :
            while i < len(manual) and automatic[i]['word'] :
                in_gap = False
                if manual[i]['word'] :
                    start = manual[i]['end']
                i += 1
            while i < len(manual) and not automatic[i]['word'] :
                in_gap = True
                i += 1
            if i < len(manual) :
                gaps.append( manual[i]['start'] - start )
                in_gap = False
                start = manual[i]['end']

        if in_gap :
            gaps.append( max( [ w['end'] for w in manual if 'end' in w ] ) - start )
    return gaps


# # #     after alignment      # # #
def gaps_containing_speech_automatic_time(manual_dir, automatic_dir) :
    files = utils.get_dir_tuples([(manual_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), (manual_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), (automatic_dir, lambda f: f.stem[2:7])])
    gaps = []

    for segment_f, manual_files, automatic_files in ChargingBar('gaps').iter(files) :
        segments = utils.read_dict(segment_f)
        for index, segment in enumerate(segments) :
            start, end = segment.values()
            
            manual_f = next( iter(f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            automatic_f = next( iter(f for f in automatic_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            if not (manual_f and automatic_f) :
                continue

            manual = utils.read_dict(manual_f)
            automatic = utils.read_dict(automatic_f)

            manual_aligned, automatic_aligned, _ = alignment.align_words(manual, automatic, insertion_obj={'word' : '', 'start' : 0, 'end' : 0, 'is_restart' : False, 'pause_type' : ''})
            manual_untranscribed = [ m for m, a in zip(manual_aligned, automatic_aligned) if m['word'] and not a['word'] ]
            
            if not manual_untranscribed :
                continue

            for pre, post in zip( [{'end' : 0}] + automatic, automatic + [{'start' : end - start}]) :
                gap = (pre['end'], post['start'])
                # not transcribed word at least 50% in gap
                if any( word_utils.overlap(gap, w) >= (w['end'] - w['start']) / 2 for w in manual_untranscribed ) :
                    gaps.append(gap[1] - gap[0])
    return gaps   


def transcript_alignment(manual_dir, automatic_dir, hesitation_dir=None, hesitation_radius=-1, min_len=1, position=True, length=True) :
    'returns [ alignment metric ] per word'
    if hesitation_dir :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir, hesitation_dir])
        files = [ (f1, (f2, f3)) for f1, f2, f3 in files ]
    else :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])

    data = []
    for manual_f, automatic_f in ChargingBar('transcript alignment').iter(files) :
        manual = utils.read_dict(manual_f)
        if len(manual) < min_len :
            continue
        if hesitation_dir :
            automatic_f, hesitation_f = automatic_f
        automatic = utils.read_dict(automatic_f)
        if hesitation_dir :
            automatic += utils.read_dict(hesitation_f)
            automatic.sort(key=lambda w : w['start'])
        
        manual, automatic, _ = alignment.align_words(manual, automatic, insertion_obj={'word' : '', 'start' : -1, 'end' : -1})
        if hesitation_radius >= 0 :
            hesitation_enviroment = [False] * len(manual)
            upper_bound = len(manual)
            for index, word in enumerate(manual) :
                if word['word'] and (word['pause_type'] or word['is_restart']) :
                    start = max(0, index-hesitation_radius)
                    end = min(index + hesitation_radius + 1, upper_bound)
                    hesitation_enviroment[start:end] = [True] * (end - start)
            manual = [ word for word, env in zip(manual, hesitation_enviroment) if env ]
            automatic = [ word for word, env in zip(automatic, hesitation_enviroment) if env ]
        x = [ (m, a) for m, a in zip(manual, automatic) if m['word'] and a['word']]
        if len(x) > 0 :
            manual, automatic = list(map(list, zip(*x)))
            # this also includes replacements [ simplify(w_manual) != simplify(w_automatic) ] but this is alright
            # data.append(metric.alignment_error(manual, automatic))
            data += metric.alignment_error_per_word(manual, automatic, position, length)

    return data


def untranscribed_speech_reachable(manual_dir, automatic_dir, gaps = [0.1, 10, 0.1]) :
    'gaps=[start, number of buckets, increment], returns list of [correct, not correct]'

    data_containing = [ [ [ 0 for _ in range(2) ] for _ in range(3) ] for _ in range(gaps[1]) ]   # buckets x 3 x 2
    data_reachable = [  [ 0 for _ in range(3) ] for _ in range(gaps[1]) ]                         # buckets x 3
    number_of_hesitations = 0

    files = utils.get_dir_tuples([(manual_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), (manual_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), (automatic_dir, lambda f: f.stem[2:7])])
        
    for segment_f, manual_files, automatic_files in ChargingBar('untranscribed speech').iter(files) :                                   # this block of code occurs a couple of times
        segments = utils.read_dict(segment_f)                                                                                           #
        for index, segment in enumerate(segments) :                                                                                     #
            start, end = segment.values()                                                                                               #
                                                                                                                                        #
            manual_f = next( iter(f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)           #
            automatic_f = next( iter(f for f in automatic_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)     #
            if not (manual_f and automatic_f) :                                                                                         #
                continue                                                                                                                #
                                                                                                                                        #
            manual = utils.read_dict(manual_f)                                                                                          #
            automatic = utils.read_dict(automatic_f)                                                                                    #

            manual_aligned, automatic_aligned, _ = alignment.align_words(manual, automatic, {'word': '' })

            manual_untranscribed = [ m for m, a in zip(manual_aligned, automatic_aligned) if m['word'] and not a['word'] ]
            number_of_hesitations += len(manual_untranscribed)
            reachable = [  [ set() for _ in range(3) ] for _ in range(gaps[1]) ]
            
            # for each gap size: in what percentage of gaps are hesitations
            for pre, post in zip([{'end' : 0}] + automatic, automatic + [{'start' : end - start}]) :
                if post['start'] - pre['end'] > gaps[0] :
                    gap = [pre['end'], post['start']]
                    bucket = min( int( (gap[1] - gap[0] - gaps[0]) / gaps[2]), gaps[1] - 1)
                    
                    partial = [ w for w in manual_untranscribed if word_utils.overlap(gap, w) > 0 ]
                    partial_50 = [ w for w in manual_untranscribed if word_utils.overlap(gap, w) >= (w['end'] - w['start']) / 2 ]
                    total = [ w for w in manual_untranscribed if pre['end'] <= w['start'] <= w['end'] <= post['start'] ]
                    for i, evaluation in enumerate([partial, partial_50, total]) :
                        if evaluation :  data_containing[bucket][i][0] += 1
                        else :  data_containing[bucket][i][1] += 1
                        reachable[bucket][i].update( [ (w['start'], w['end']) for w in evaluation ] )
        
            for bucket, reaachable_words_list in enumerate(reachable) :
                for i, reaachable_words in enumerate(reaachable_words_list) :
                    data_reachable[bucket][i] += len(reaachable_words)
                    
    return data_containing, data_reachable, number_of_hesitations


def transcript_alignment_full_package(manual_dir, automatic_dir, hesitation_dir=None, min_len=1) :
    all_data = [[[], []], [[], []]]
    
    if hesitation_dir :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir, hesitation_dir])
        files = [ (f1, (f2, f3)) for f1, f2, f3 in files ]
    else :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])

    for manual_f, automatic_f in ChargingBar('transcript alignment').iter(files) :
        manual = utils.read_dict(manual_f)
        if len(manual) < min_len :
            continue
        if hesitation_dir :
            automatic_f, hesitation_f = automatic_f
        automatic = utils.read_dict(automatic_f)
        if hesitation_dir :
            automatic += utils.read_dict(hesitation_f)
            automatic.sort(key=lambda w : w['start'])
        
        manual, automatic, _ = alignment.align_words(manual, automatic, insertion_obj={'word' : '', 'start' : -1, 'end' : -1})
        alignment_all = [ (m, a) for m, a in zip(manual, automatic) if m['word'] and a['word']]
        hesitation_radius = 2
        hesitation_enviroment = [False] * len(manual)
        upper_bound = len(manual)
        for index, word in enumerate(manual) :
            if word['word'] and not automatic[index]['word'] :
                start = max(0, index-hesitation_radius)
                end = min(index + hesitation_radius + 1, upper_bound)
                hesitation_enviroment[start:end] = [True] * (end - start)
        manual = [ word for word, env in zip(manual, hesitation_enviroment) if env ]
        automatic = [ word for word, env in zip(automatic, hesitation_enviroment) if env ]
        alignment_around_hesitations = [ (m, a) for m, a in zip(manual, automatic) if m['word'] and a['word']]
        if len(alignment_all) > 0 :
            manual, automatic = list(map(list, zip(*alignment_all)))
            all_data[0][0] += metric.alignment_error_per_word(manual, automatic, True, False)
            all_data[0][1] += metric.alignment_error_per_word(manual, automatic, False, True)
        if len(alignment_around_hesitations) > 0 :
            manual, automatic = list(map(list, zip(*alignment_around_hesitations)))
            all_data[1][0] += metric.alignment_error_per_word(manual, automatic, True, False)
            all_data[1][1] += metric.alignment_error_per_word(manual, automatic, False, True)

    return all_data


def best_case_scenario(manual_dir, automatic_dir, min_lens=[0.2]) :
    'returns [min_len] x [base, partial, 50, total] x [i, d, r, n, all]'
    files = utils.get_dir_tuples([(manual_dir, None, lambda f: not 'Speech' in f.stem), automatic_dir])
    # [min_len] x [base, partial, 50, total] x [i, d, r, n]
    data = [ [ [ 0 for _ in range(4) ] for _ in range(4) ] for _ in min_lens ]
    for i, min_len in enumerate(min_lens) :
        for manual_f, automatic_f in ChargingBar('best case scenario').iter(files) :
            manual = utils.read_dict(manual_f)
            automatic = utils.read_dict(automatic_f)
            new_automatic = [ [] for _ in range(3) ]
            for pre, post in zip(automatic[:-1], automatic[1:]) :
                for j in range(3) :
                    new_automatic[j].append(pre)
                if post['start'] - pre['end'] >= min_len :
                    gap = [pre['end'], post['start']]
                    partial = [ w for w in manual if word_utils.overlap(gap, w) > 0 ]
                    partial_50 = [ w for w in manual if word_utils.overlap(gap, w) >= (w['end'] - w['start']) / 2 ]
                    total = [ w for w in manual if pre['end'] <= w['start'] <= w['end'] <= post['start'] ]
                    new_automatic[0] += partial
                    new_automatic[1] += partial_50
                    new_automatic[2] += total
            if automatic :
                for j in range(3) :
                    new_automatic[j].append(automatic[-1])
            
            for j, a in enumerate( [automatic] + new_automatic ) :
                ops = alignment.get_operations([word_utils.simplify(word['word']) for word in manual], [word_utils.simplify(word['word']) for word in a])
                data[i][j][0] += ops.count('i')
                data[i][j][1] += ops.count('d')
                data[i][j][2] += ops.count('r')
                data[i][j][3] += ops.count('n')

    for i in range(len(min_lens)) :
        data[i][0].append( sum(data[i][0]) ) # base = i, d, r, n, all
        for j in range(1, 4) :
            for k in range(4) :
                data[i][j][k] -= data[i][0][k]  # transcript is offset to base
            data[i][j].append( sum(data[i][j]) ) # transcript = i, d, r, n, all (offset to base)

    return data

        
# # # after gap classification # # #
from tasks.audio_classification.classification_interference import MIN_GAP

def classification_metrics(manual_dir, automatic_dir, classification_dir) :
    'returns TP FP TN FN'
    files = utils.get_dir_tuples([
        (manual_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), 
        (manual_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), 
        (automatic_dir, lambda f: f.stem[2:7]),  
        (classification_dir, lambda f: f.stem[2:7])
    ])
    predictions = [ 0, 0, 0, 0 ]    # TP FP TN FN

    for segment_f, manual_files, automatic_files, classification_files in ChargingBar('classification metrics').iter(files) :
        segments = utils.read_dict(segment_f)
        for index, segment in enumerate(segments) :
            start, end = segment.values()
            
            manual_f = next( iter(f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            automatic_f = next( iter(f for f in automatic_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            classification_f = next( iter(f for f in classification_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            if not (manual_f and automatic_f and classification_f) :
                continue

            manual = utils.read_dict(manual_f)
            automatic = utils.read_dict(automatic_f)
            classification = utils.read_dict(classification_f)

            for pre, post in zip( [{'end' : 0}] + automatic, automatic + [{'start' : end - start}]) :
                gap_start = pre['end']
                gap_end = post['start']
                if gap_end - gap_start > MIN_GAP :
                    label = bool( len([w for w in manual if word_utils.overlap((gap_start, gap_end), w) >= (w['end'] - w['start']) / 2]) > 0 )
                    prediction = bool( {'start' : gap_start, 'end' : gap_end} in classification )
                
                    if       label and prediction     : predictions[0] += 1
                    elif     label and not prediction : predictions[1] += 1
                    elif not label and not prediction : predictions[2] += 1
                    else                              : predictions[3] += 1
    return predictions                
                

def untranscribed_speech_labelling(manual_dir, automatic_dir, classification_dir) :
    'returns TP FP TN FN for word level' 
    files = utils.get_dir_tuples([
        (manual_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), 
        (manual_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), 
        (automatic_dir, lambda f: f.stem[2:7]), 
        (classification_dir, lambda f: f.stem[2:7])
    ])
    untranscribed_words = 0
    missed_words = 0
    correct_labels, incorrect_labls = 0, 0
    label = '\'\'label\'\''

    for segment_f, manual_files, automatic_files, classification_files in ChargingBar('speech labelling').iter(files) :
        segments = utils.read_dict(segment_f)
        for index, segment in enumerate(segments) :
            start, end = segment.values()
            
            manual_f = next( iter(f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            automatic_f = next( iter(f for f in automatic_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            classification_f = next( iter(f for f in classification_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            if not (manual_f and automatic_f and classification_f) :
                continue

            manual = utils.read_dict(manual_f)
            automatic = utils.read_dict(automatic_f)
            manual_aligned, automatic_aligned = alignment.align([ w['word'] for w in manual ], [ w['word'] for w in automatic ])
            untranscribed_words += len( [ m for m, a in zip(manual_aligned, automatic_aligned) if m and not a ] )

            classification = utils.read_dict(classification_f)

            labeled_automatic = []
            for pre, post in zip( [{'end' : 0}] + automatic, automatic + [{'start' : end - start}]) :
                if 'word' in pre and pre['word']:
                    labeled_automatic.append(pre['word'])
                gap_start = pre['end']
                gap_end = post['start']
                if gap_end - gap_start > MIN_GAP :
                    prediction = bool( {'start' : gap_start, 'end' : gap_end} in classification )
                    if prediction :
                        length = len( [ w for w in manual if word_utils.overlap((gap_start, gap_end), w) >= (w['end'] - w['start']) / 2 ] )
                        labeled_automatic += [ label ] * length
                
            manual_aligned, automatic_aligned = alignment.align([ w['word'] for w in manual ], labeled_automatic)

            for m, a in zip(manual_aligned, automatic_aligned) :
                if m and a == label :       correct_labels += 1
                if not m and a == label :   incorrect_labls += 1
                if m and not a :            missed_words += 1

    return (untranscribed_words, missed_words), (correct_labels, incorrect_labls)            


# # #  after retranscription   # # #
def percentage_of_captured_words(manual_dir, automatic_dir, retranscibe_dir) :
    files = utils.get_dir_tuples([(manual_dir, None, lambda f: not 'Speech' in f.stem), automatic_dir, retranscibe_dir])

    transcribed = 0
    untranscribed = 0
    for manual_f, automatic_f, retranscribe_f in ChargingBar('retranscription percentage').iter(files) :
        manual = utils.read_dict(manual_f)
        automatic = utils.read_dict(automatic_f)
        retranscribed = utils.read_dict(retranscribe_f)

        manual_aligned, automatic_aligned, _ = alignment.align_words(manual, automatic, {'word' : ''})
        manual_labeled = [ m | {'transcribed' : True} if a['word'] else m | {'transcribed' : False} for m, a in zip(manual_aligned, automatic_aligned) if m['word'] ]
        
        automatic_whole = automatic + retranscribed
        automatic_whole.sort(key=lambda w : w['start'])
        manual_aligned, automatic_aligned, _ = alignment.align_words(manual_labeled, automatic_whole, {'word' : ''})

        for m, a in zip(manual_aligned, automatic_aligned) :
            if not 'transcribed' in m or m['transcribed'] :
                continue
            if a['word'] :
                transcribed += 1
            else :
                untranscribed += 1

    return transcribed, untranscribed
    

# # #         general          # # #
def collect_alignment_examples(manual_dir, automatic_dirs : list[tuple[Path, Path | None]], audio_dir = c.audio_dir, n=10, save_dir=c.data_base / 'examples') :
    
    args = [ (automatic_dir[0], lambda f : f.stem[2:7]) for automatic_dir in automatic_dirs ] + [ (automatic_dir[1], lambda f : f.stem[2:7]) for automatic_dir in automatic_dirs if automatic_dir[1] ]
    all_files = utils.get_dir_tuples([
        (audio_dir, lambda f : f.stem[3:8], None, 'wav'),
        (manual_dir, lambda f : f.stem[2:7], lambda f: 'Speech' in f.stem),
        (manual_dir, lambda f : f.stem[2:7], lambda f : not 'Speech' in f.stem)] + args)
    random.shuffle(all_files)    
    main_files = [ (f[0], f[1], f[2]) for f in all_files ]
    automatic_files_pack = []
    for files in all_files :
        f0 = files[3:3+len(automatic_dirs)]
        f1 = []
        i = len(automatic_dirs) + 3
        for x in automatic_dirs :
            if x[1] :
                f1.append(files[i])
                i += 1
            else :
                f1.append(None)
        automatic_files_pack.append( tuple(zip(f0, f1)) )

    alignments = []
    for (audio_f, segment_f, manual_files), automatic_files_tuple in zip(main_files, automatic_files_pack) :
        alignment = []
        segments = utils.read_dict(segment_f)
        audio = utils.read_audio(audio_f, c.sample_rate)[0]
        segment = random.choice(segments)
        index = segments.index(segment)
    
        manual_f = next( iter( f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
        if not manual_f : continue    # is a contraversial file
        manual = utils.read_dict(manual_f)
        speech = audio[int(c.sample_rate*segment['start']) : int(c.sample_rate*segment['end'])]
    
        for automatic_files, hesitation_files in automatic_files_tuple :    
            automatic_f = next( f for f in automatic_files if (segment_f.stem[2:7] +  "{:03d}".format(index)) in f.stem )
            automatic = [ w | {'original' : True} for w in utils.read_dict(automatic_f) ]
            if hesitation_files :
                hesitation_f = next( f for f in hesitation_files if (segment_f.stem[2:7] +  "{:03d}".format(index)) in f.stem )
                automatic += [ w | {'original' : False} for w in utils.read_dict(hesitation_f) ]
            automatic = [ dict( (k, w[k]) for k in ('word', 'original', 'start', 'end')) for w in automatic ]
            
            alignment.append(automatic)

        alignments.append((manual, alignment, speech, manual_f.stem))

        if len(alignments) >= n :
            if os.path.isdir(save_dir) :
                shutil.rmtree(save_dir)
                
            for manual, automatic_files, audio, title in alignments :
                utils.write_dict( save_dir / (title + '_manual.txt'), manual)
                utils.write_audio( save_dir / (title + '_audio.wav'), audio, c.sample_rate)
                for i, a in enumerate(automatic_files) :
                    utils.write_dict( save_dir / (title + '_automatic' + str(i) + '.txt'), a)
            return
        

# deprecated but may be usefull in future again
def hesitation_translation(manual_dir, automatic_dir, hesitation_dir = None, hesitations_file = c.hesitations_file, min_len=1) :
    hesitations = list( utils.read_vocabulary(hesitations_file).keys() )
    files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])
    if hesitation_dir :
        hesitation_files = utils.get_dir_files(hesitation_dir, 'txt')
        hesitation_files.sort()
        pool = [ h.stem for h in hesitation_files ]
        files = [ f for f in files if f[0].stem in pool ]

    numbers = [[0, 0, 0], [0, 0, 0]]
    for manual_f, automatic_f in ChargingBar("Hesitation Transcription").iter(files) :
        manual = utils.read_dict(manual_f)
        if len(manual) < min_len :
            continue

        automatic = utils.read_dict(automatic_f)
        if hesitation_dir :
            hesitation_f = next( f for f in hesitation_files if automatic_f.stem == f.stem )
            hesitation_files.remove(hesitation_f)
            automatic += utils.read_dict(hesitation_f)
            automatic.sort(key=lambda w : w['start'])

        manual, automatic, _ = alignment.align_words(manual, automatic, {'word' : ''})
        for m, w in zip(manual, automatic) :
            if not m['word'] :     continue
            if m['pause_type'] :   i = 0
            elif m['is_restart'] : i = 1
            else :                 continue
            w = word_utils.simplify(w['word'], additional='-')
            if not w :                                                       numbers[i][2] += 1
            elif w in hesitations or w[0] == '-' or w[-1] == '-' or m == w:  numbers[i][1] += 1
            else :                                                           numbers[i][0] += 1

    for i, x in enumerate(numbers[0]) :
        numbers[1][i] += x
    return numbers

# deprecated but may be usefull in future again
def manual_hesitation_gaps(manual_dir, automatic_dir) :
    def get_gaps(words) :
        gaps = []
        words = [{'word' : '', 'start' : 0, 'end' : 0, 'is_restart' : False, 'pause_type' : ''}] + words + [{'word' : '', 'start' : words[-1]['end'] + 0.5, 'end' : words[-1]['end'] + 0.5, 'is_restart' : False, 'pause_type' : ''}]

        start =  -1
        for index, word in enumerate(words) :
            if not ( word['is_restart'] or word['pause_type'] ) :  # not hesitation
                if start == index - 1 :
                    start = index
                else :
                    gaps.append( word['start'] - words[start]['end'])
                    start = index
        return gaps

    files = utils.get_dir_tuples([(manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])
    data_all = []
    data_not_trans = []
    for manual_f, automatic_f in ChargingBar('gaps ').iter(files) :
        manual = utils.read_dict(manual_f)
        data_all += get_gaps(manual.copy())
        automatic = utils.read_dict(automatic_f)
        manual, automatic, _ = alignment.align_words(manual, automatic, insertion_obj={'word' : '', 'start' : 0, 'end' : 0, 'is_restart' : False, 'pause_type' : ''})

        manual = [ word_m if not word_a['word'] else word_m | {'is_restart' : False, 'pause_type' : ''}  for word_m, word_a in zip(manual, automatic) if word_m['word'] ]
        data_not_trans += get_gaps(manual)
    return data_all, data_not_trans
