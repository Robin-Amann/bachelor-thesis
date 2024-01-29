import utils.file as utils
import utils.wer_alignment as alignment
from progress.bar import ChargingBar
import utils.constants as constants
import utils.alignment_metric as metric
import random
import utils.transcript as word_utils
import random
from pathlib import Path
import shutil
import os

def segment_length(manual_dir, automatic_dir, hesitation_dir = None, min_len=1, filter_condition = utils.base_filter) -> tuple[list[tuple[tuple[int, int], float]], float]:
    'returns list of ( ( length manual, length automatic), audio length) and total audio length'
    files = utils.get_dir_tuples([
        (manual_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), 
        (manual_dir, lambda f : f.stem[2:7], lambda f : not 'Speech' in f.stem),
        (automatic_dir, lambda f : f.stem[2:7])], filter_condition=filter_condition)
    if hesitation_dir :
        hesitation_files = [ f for f in utils.get_dir_files(hesitation_dir, 'txt', filter_condition=filter_condition) ]

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


def transcript_alignment(manual_dir, automatic_dir, hesitation_dir=None, hesitation_radius=-1, min_len=1, position=True, length=True) :
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

# I know I should change that
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
        x1 = [ (m, a) for m, a in zip(manual, automatic) if m['word'] and a['word']]
        hesitation_radius = 2
        hesitation_enviroment = [False] * len(manual)
        upper_bound = len(manual)
        for index, word in enumerate(manual) :
            if word['word'] and (word['pause_type'] or word['is_restart']) :
                start = max(0, index-hesitation_radius)
                end = min(index + hesitation_radius + 1, upper_bound)
                hesitation_enviroment[start:end] = [True] * (end - start)
        manual = [ word for word, env in zip(manual, hesitation_enviroment) if env ]
        automatic = [ word for word, env in zip(automatic, hesitation_enviroment) if env ]
        x2 = [ (m, a) for m, a in zip(manual, automatic) if m['word'] and a['word']]
        if len(x1) > 0 :
            manual, automatic = list(map(list, zip(*x1)))
            all_data[0][0] += metric.alignment_error_per_word(manual, automatic, True, False)
            all_data[0][1] += metric.alignment_error_per_word(manual, automatic, False, True)
        if len(x2) > 0 :
            manual, automatic = list(map(list, zip(*x2)))
            all_data[1][0] += metric.alignment_error_per_word(manual, automatic, True, False)
            all_data[1][1] += metric.alignment_error_per_word(manual, automatic, False, True)

    return all_data


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
            if os.path.isdir(save_dir) :
                shutil.rmtree(save_dir)
                
            for manual, automatic_files, audio, title in alignments :
                utils.write_dict( save_dir / (title + '_manual.txt'), manual)
                utils.write_audio( save_dir / (title + '_audio.wav'), audio, constants.sample_rate)
                for i, a in enumerate(automatic_files) :
                    utils.write_dict( save_dir / (title + '_automatic' + str(i) + '.txt'), a)
            return
        

def hesitation_gaps(manual_dir, automatic_dir, retranscibed_dir=None, gaps = [0.1, 10, 0.1]) -> list[list]:
    'gaps=[start, number of buckets, increment], returns list of [correct, not correct]'

    data_containing = [ [ [ 0 for _ in range(2) ] for _ in range(3) ] for _ in range(gaps[1]) ]   # buckets x 3 x 2
    data_reachable = [  [ 0 for _ in range(3) ] for _ in range(gaps[1]) ]                         # buckets x 3
    success_rate = [ [ 0 for _ in range(3) ] for _ in range(4) ]                                  # 4 x 3
    number_of_hesitations = 0

    if retranscibed_dir :
        files = [ (f1, (f2, f3)) for f1, f2, f3 in utils.get_dir_tuples([(manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir, retranscibed_dir]) ]
    else :
        files = utils.get_dir_tuples([(manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir])
        
    for manual_f, automatic_f in ChargingBar('gaps ').iter(files) :
        if retranscibed_dir :
            automatic_f, retranscribe_f = automatic_f
        manual = [ w for w in utils.read_dict(manual_f) if w['pause_type'] or w['is_restart'] ]
        number_of_hesitations += len(manual)
        automatic = utils.read_dict(automatic_f)
        reachable = [  [ set() for _ in range(3) ] for _ in range(gaps[1]) ]
        
        # for each gap size: in what percentage of gaps are hesitations
        for pre, post in zip(automatic[:-1], automatic[1:]) :
            if post['start'] - pre['end'] > gaps[0] :
                gap = [pre['end'], post['start']]
                bucket = min( int( (gap[1] - gap[0] - gaps[0]) / gaps[2]), gaps[1] - 1)
                
                partial = [ w for w in manual if word_utils.overlap(gap, w) > 0 ]
                partial_50 = [ w for w in manual if word_utils.overlap(gap, w) >= (w['end'] - w['start']) / 2 ]
                total = [ w for w in manual if pre['end'] <= w['start'] <= w['end'] <= post['start'] ]
                for i, x in enumerate([partial, partial_50, total]) :
                    if x :  data_containing[bucket][i][0] += 1
                    else :  data_containing[bucket][i][1] += 1
                    reachable[bucket][i].update( [ (w['start'], w['end']) for w in x ] )
    
        for bucket, l in enumerate(reachable) :
            for i, s in enumerate(l) :
                data_reachable[bucket][i] += len(s)

        if retranscibed_dir :
            retranscribe = utils.read_dict(retranscribe_f)
            for gap in retranscribe :
                partial = [ w for w in manual if word_utils.overlap([gap['start'], gap['end']], w) > 0 ]
                partial_50 = [ w for w in manual if word_utils.overlap([gap['start'], gap['end']], w) >= (w['end'] - w['start']) / 2 ]
                total = [ w for w in manual if gap['start'] <= w['start'] <= w['end'] <= gap['end'] ]
                for i, x in enumerate([partial, partial_50, total]) :
                    if   gap['word'] and x :         success_rate[0][i] += 1    # TP
                    elif not gap['word'] and x :     success_rate[1][i] += 1    # FP
                    elif not gap['word'] and not x : success_rate[2][i] += 1    # TN
                    else :                           success_rate[3][i] += 1    # FN
                
    return data_containing, data_reachable, success_rate, number_of_hesitations


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

def manual_hesitation_gaps(manual_dir, automatic_dir) :
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


def best_possible_solution() :
    import utils.constants as c

    files = utils.get_dir_tuples([(c.manual_seg_dir, None, lambda f: not 'Speech' in f.stem), c.automatic_align_dir / '0'])

    print(len(files))

    data = [ [ 0 for _ in range(4) ] for _ in range(4) ]
    for manual_f, automatic_f in ChargingBar('wer').iter(files) :
        manual = utils.read_dict(manual_f)
        automatic = utils.read_dict(automatic_f)
        new_automatic = [ [] for _ in range(3) ]
        for pre, post in zip(automatic[:-1], automatic[1:]) :
            for i in range(3) :
                new_automatic[i].append(pre)
            if post['start'] - pre['end'] > 0.5 :
                gap = [pre['end'], post['start']]
                partial = [ w for w in manual if word_utils.overlap(gap, w) > 0 ]
                partial_50 = [ w for w in manual if word_utils.overlap(gap, w) >= (w['end'] - w['start']) / 2 ]
                total = [ w for w in manual if pre['end'] <= w['start'] <= w['end'] <= post['start'] ]
                new_automatic[0] += partial
                new_automatic[1] += partial_50
                new_automatic[2] += total
        if automatic :
            for i in range(3) :
                new_automatic[i].append(automatic[-1])
        
        for i, a in enumerate( [automatic] + new_automatic ) :
            ops = alignment.get_operations([word_utils.simplify(word['word']) for word in manual], [word_utils.simplify(word['word']) for word in a])
            data[i][0] += ops.count('i')
            data[i][1] += ops.count('d')
            data[i][2] += ops.count('r')
            data[i][3] += ops.count('n')

    print(data)
    for i in range(4) :
        print(data[i], round( sum(data[i][:3]) / sum( data[i] ), 4))

    # d should go down and n up
    # i should stay the same

    # 0.2     [[ 91125, 121739, 61065, 1032183, 1306112], [343071,  46076, 53740, 1115171, 1558058], [144654,  62371, 61194, 1091422, 1359641], [101027,  77545, 60880, 1076562, 1316014]]
    #               i       d      r        n        l    wer
    # base    [ 91.125, 121.739, 61.065, 1.032.183, 1.306.112] 0.2097             i        d       r        n 
    # partial [343.071,  46.076, 53.740, 1.115.171, 1.558.058] 0.2843      [+251.946, -75.663, -7.325, +82.988]
    # 50      [144.654,  62.371, 61.194, 1.091.422, 1.359.641] 0.1973      [ +53.529, -59.368,   +129, +59.239]
    # total   [101.027,  77.545, 60.880, 1.076.562, 1.316.014] 0.182       [  +9.902, -44.194,   -185, +44.379]

    # 0.5     [[ 91125, 121739, 61065, 1032183, 1306112], [236493,  66330, 58188, 1090469, 1451480], [122623,  78361, 61007, 1075619, 1337610], [ 97940,  86420, 60382, 1068185, 1312927]]
    #               i       d      r        n        l    wer
    # base    [ 91.125, 121.739, 61.065, 1.032.183, 1.306.112] 0.2097             i        d       r        n
    # partial [236.493,  66.330, 58.188, 1.090.469, 1.451.480] 0.2487      [+145.368, -55.409, -2.877, +58.286]
    # 50      [122.623,  78.361, 61.007, 1.075.619, 1.337.610] 0.1959      [ +31.498, -43.378,    -58, +43.436]
    # total   [ 97.940,  86.420, 60.382, 1.068.185, 1.312.927] 0.1864      [  +6.815, -35.319,   -683, +36.002]

