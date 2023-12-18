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
            data.append(metric.alignment_error(manual, automatic))

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


# deprecated
# def collect_alignment_examples(manual_dir, automatic_dir, hesitation_dir, audio_dir = constants.audio_dir, n=10, save_dir=constants.data_base / 'examples') :
#     files = utils.get_dir_tuples([
#         (audio_dir, lambda f : f.stem[3:8], None, 'wav'),
#         (manual_dir, lambda f : f.stem[2:7], lambda f: 'Speech' in f.stem),
#         (manual_dir, lambda f : f.stem[2:7], lambda f : not 'Speech' in f.stem),
#         (automatic_dir, lambda f : f.stem[2:7]),
#         (hesitation_dir, lambda f : f.stem[2:7])
#     ])
#     random.shuffle(files)    
#     alignments = []

#     for audio_f, segment_f, manual_files, automatic_files, hesitation_files in files :
#         segments = utils.read_dict(segment_f)
#         audio = utils.read_audio(audio_f, constants.sample_rate)[0]
#         segment = random.choice(segments)
#         index = segments.index(segment)
#         manual_f = next( iter( f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
#         if not manual_f : continue    # is a contraversial file
#         automatic_f = next( f for f in automatic_files if (segment_f.stem[2:7] +  "{:03d}".format(index)) in f.stem )
#         hesitation_f = next( f for f in hesitation_files if (segment_f.stem[2:7] +  "{:03d}".format(index)) in f.stem )
#         speech = audio[int(constants.sample_rate*segment['start']) : int(constants.sample_rate*segment['end'])]

#         manual = utils.read_dict(manual_f)
#         automatic = [ w | {'original' : True} for w in utils.read_dict(automatic_f) ] + [ w | {'original' : False} for w in utils.read_dict(hesitation_f) ]
#         automatic = [ dict( (k, w[k]) for k in ('word', 'original', 'start', 'end')) for w in automatic ]
#         alignments.append( (manual, automatic, manual_f.stem, speech))

#         if len(alignments) >= n :
#             for manual, automatic, title, audio in alignments :
#                 utils.write_dict( save_dir / (title + '_manual.txt'), manual)
#                 utils.write_dict( save_dir / (title + '_automatic.txt'), automatic)
#                 utils.write_audio( save_dir / (title + '_audio.wav'), audio, constants.sample_rate)
#             return