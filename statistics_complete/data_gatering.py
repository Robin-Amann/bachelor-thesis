import utils.file as utils
import utils.wer_alignment as alignment
from progress.bar import ChargingBar
import utils.constants as constants
import utils.alignment_metric as metric
import random



def segment_length(manual_dir, automatic_dir, hesitation_dir = None, min_len=1) -> tuple[list[tuple[tuple[int, int], float]], float]:
    'returns list of ( ( length manual, length automatic), audio length) and total audio length'
    files = utils.get_dir_tuples([
        (manual_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), 
        (manual_dir, lambda f : f.stem[2:7], lambda f : not 'Speech' in f.stem),
        (automatic_dir, lambda f : f.stem[2:7])])
    if hesitation_dir :
        hesitation_files = [ f for f in utils.get_dir_files(hesitation_dir, 'txt') ]

    data = []
    total_length = 0 # in sec
    for length_f, manual_files, automatic_files in ChargingBar('segment lengths').iter(files) :

        segments = utils.read_dict(length_f)
        for index, segment in enumerate(segments) :
            manual_f = next( iter(f for f in manual_files if (length_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            if not manual_f : continue    # is a contraversial file
            manual = utils.read_dict(manual_f) 
            if len(manual) < min_len :
                continue
            automatic_f = next( f for f in automatic_files if (length_f.stem[2:7] + '{:03d}'.format(index)) in f.stem )
            automatic = utils.read_dict(automatic_f)
            if hesitation_dir :
                hesitation_f = next( f for f in hesitation_files if automatic_f.stem == f.stem )
                automatic += utils.read_dict(hesitation_f)
                automatic.sort(key=lambda w : w['start'])

            length = segment['end'] - segment['start']
            data.append( (( len(manual), len(automatic)), length) )
            total_length += length
    return data, total_length


def transcript_alignment(manual_dir, automatic_dir, hesitation_dir=None, hesitation_radius=-1, min_len=1) :
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
            data += metric.alignment_error_per_word(manual, automatic)

    return data


def calculate_wer(manual_dir, automatic_dir, hesitation_dir=None, min_len=1) :
    if hesitation_dir :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir, hesitation_dir])
        files = [ (f1, (f2, f3)) for f1, f2, f3 in files ]
    else :
        files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])


    data = []
    for manual_f, automatic_f in ChargingBar('WER').iter(files) :
        manual = utils.read_dict(manual_f)
        if len(manual) < min_len :
            continue
        if hesitation_dir :
            automatic_f, hesitation_f = automatic_f
        automatic = utils.read_dict(automatic_f)
        if hesitation_dir :
            automatic += utils.read_dict(hesitation_f)
            automatic.sort(key=lambda w : w['start'])

        wer, operations = alignment.wer_and_ops([ w['word'] for w in manual ], [ w['word'] for w in automatic ])
        if len(operations) > 0 :
            data.append((wer, len(operations)))

    l, wer, dist = (0, 0, [])
    for wer_i, length in data :
        wer += wer_i * length
        l += length
        dist.append(wer_i)
    wer = wer / l
    return dist, wer


def percentage(seg_dir, min_len=1) :
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


import utils.transcript as word_utils

def hesitation_translation(manual_dir, automatic_dir, hesitation_dir = None, hesitations_file = constants.hesitations_file, min_len=1) :
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


import random
from pathlib import Path
def collect_alignment_examples(manual_dir, automatic_dirs : list[tuple[Path, Path | None]], audio_dir = constants.audio_dir, n=10, save_dir=constants.data_base / 'examples') :
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
        audio = utils.read_audio(audio_f, constants.sample_rate)[0]
        segment = random.choice(segments)
        index = segments.index(segment)
    
        manual_f = next( iter( f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
        if not manual_f : continue    # is a contraversial file
        manual = utils.read_dict(manual_f)
        speech = audio[int(constants.sample_rate*segment['start']) : int(constants.sample_rate*segment['end'])]
    
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
            for manual, automatic_files, audio, title in alignments :
                utils.write_dict( save_dir / (title + '_manual.txt'), manual)
                utils.write_audio( save_dir / (title + '_audio.wav'), audio, constants.sample_rate)
                for i, a in enumerate(automatic_files) :
                    utils.write_dict( save_dir / (title + '_automatic' + str(i) + '.txt'), a)
            return


def overlap(gap, word):
    return max(0, min(gap[1], word['end']) - max(gap[0], word['start']))
        
def hesitation_gaps(manual_dir, automatic_dir, retranscibed_dir, gaps = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]) -> list[list]:
    'returns list of [correct, not correct]'

    # for each gap size: in what percentage of gaps are hesitations
    result = []
    files = utils.get_dir_tuples([(manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir, retranscibed_dir])
    number_of_hesitations = 0
    for manual_f, automatic_f, retranscribe_f in ChargingBar('number of hesitations').iter(files) :
        manual = [ w for w in utils.read_dict(manual_f) if w['pause_type'] or w['is_restart'] ]
        number_of_hesitations += len(manual)
    print(number_of_hesitations)
    for GAP in gaps :
        data = [[0, 0, 0],  # gap contained hesitation
                [0, 0, 0],  # gap contained no hesitation
                [0, 0, 0]]  # number of hesitations
        captured = [0, 0, 0]
        for manual_f, automatic_f, retranscribe_f in ChargingBar('gaps ' + str(GAP)).iter(files) :
            manual = [ w for w in utils.read_dict(manual_f) if w['pause_type'] or w['is_restart'] ]
            automatic = utils.read_dict(automatic_f)
            all_partial = set()
            all_partial_50 = set()
            all_total = set()
            for pre, post in zip(automatic[:-1], automatic[1:]) :
                if post['start'] - pre['end'] > GAP :
                    gap = [pre['end'], post['start']]
                    partial = [ w for w in manual if overlap(gap, w) > 0 ]
                    partial_50 = [ w for w in manual if overlap(gap, w) >= (w['end'] - w['start']) / 2 ]
                    total = [ w for w in manual if pre['end'] <= w['start'] <= w['end'] <= post['start'] ]
                    for i, x in enumerate([partial, partial_50, total]) :
                        if x :
                            data[0][i] += 1
                            data[1][i] += len(x)
                        else :                      
                            data[2][i] += 1
                    all_partial.update([ (w['start'], w['end']) for w in partial ])
                    all_partial_50.update([ (w['start'], w['end']) for w in partial_50 ])
                    all_total.update([ (w['start'], w['end']) for w in total ])
            captured[0] += len(all_partial)
            captured[1] += len(all_partial_50)
            captured[2] += len(all_total)
        result.append([data, captured])
    
    # for dataset: what is success rate of retranscription (assuming words are correct)
    success_rate = [[0, 0, 0], 
                     [0, 0, 0]]
    for manual_f, automatic_f, retranscribe_f in ChargingBar('GAPS').iter(files) :
        manual = [ w for w in utils.read_dict(manual_f) if w['pause_type'] or w['is_restart'] ]
        retranscribe = utils.read_dict(retranscribe_f)

        for gap in retranscribe :
            partial = [ w for w in manual if overlap([gap['start'], gap['end']], w) > 0 ]
            partial_50 = [ w for w in manual if overlap([gap['start'], gap['end']], w) >= (w['end'] - w['start']) / 2 ]
            total = [ w for w in manual if gap['start'] <= w['start'] <= w['end'] <= gap['end'] ]
            for i, x in enumerate([partial, partial_50, total]) :
                if (x and gap['word']) or (not x and not gap['word']) :
                    success_rate[0][i] += 1
                else :                      
                    success_rate[1][i] += 1

    return success_rate, result


# # GAP: 0.1
# # partial: 95690 / 223589 = 42.8 %
# # partial_50: 43811 / 223589 = 19.59 %
# # total: 31478 / 223589 = 14.08 %
# # GAP: 0.2
# # partial: 79006 / 159473 = 49.54 %
# # partial_50: 40509 / 159473 = 25.4 %
# # total: 30797 / 159473 = 19.31 %
# # GAP: 0.3
# # partial: 68070 / 130814 = 52.04 %
# # partial_50: 36034 / 130814 = 27.55 %
# # total: 28615 / 130814 = 21.87 %
# # GAP: 0.4
# # partial: 58449 / 108766 = 53.74 %
# # partial_50: 31384 / 108766 = 28.85 %
# # total: 25536 / 108766 = 23.48 %
# # GAP: 0.5
# # partial: 49978 / 90246 = 55.38 %
# # partial_50: 27447 / 90246 = 30.41 %
# # total: 22645 / 90246 = 25.09 %
# # GAP: 0.6
# # partial: 42626 / 74575 = 57.16 %
# # partial_50: 24121 / 74575 = 32.34 %
# # total: 20164 / 74575 = 27.04 %
# # GAP: 0.7
# # partial: 35905 / 61213 = 58.66 %
# # partial_50: 21052 / 61213 = 34.39 %
# # total: 17780 / 61213 = 29.05 %
# # GAP: 0.8
# # partial: 30030 / 50298 = 59.7 %
# # partial_50: 18277 / 50298 = 36.34 %
# # total: 15632 / 50298 = 31.08 %
# # GAP: 0.9
# # partial: 24974 / 41359 = 60.38 %
# # partial_50: 15752 / 41359 = 38.09 %
# # total: 13608 / 41359 = 32.9 %
# # GAP: 1
# # partial: 20678 / 34072 = 60.69 %
# # partial_50: 13431 / 34072 = 39.42 %
# # total: 11730 / 34072 = 34.43 %

# [[24826, 11721, 8493], [42114, 55219, 58447]]
# 37.09 %
# 17.51 %
# 12.69 %