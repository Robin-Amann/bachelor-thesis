import tasks.preprocessing.annotations as annotations
import tasks.preprocessing.timings as timing
import utils.file as utils
import utils.constants as constants
from progress.bar import ChargingBar
from pathlib import Path
import re
import tasks.transcript_alignment as wer


def align(trans_p, timing_p) :
    trans = trans_p.copy()
    timing = timing_p.copy()
    operations = wer.get_operations([w['word'].lower() for w in trans], [w['word'].lower() for w in timing])
    trans_aligned, timing_aligned = wer.align(trans, timing, operations, insertion_obj=dict())
    
    start = 0
    end = 0
    while start < len(trans_aligned) :
        while start < len(trans_aligned) and 'word' in trans_aligned[start] and 'word' in timing_aligned[start] :
            start += 1
        end = start
        while end < len(trans_aligned) and ( not 'word' in trans_aligned[end] or not 'word' in timing_aligned[end] ) :
            end += 1

        xi = [w['word'] for w in trans_aligned[start:end] if 'word' in w]
        yi = [w['word'] for w in timing_aligned[start:end] if 'word' in w]

        # one is empty --> missing information
        if (not ''.join(xi)) or (not ''.join(yi)) :
            trans_aligned = trans_aligned[ : start] + trans_aligned[end : ]
            timing_aligned = timing_aligned[ : start] + timing_aligned[end : ]

        # interruption --> same word
        elif len(xi) == 1 and len(yi) == 1 and (xi[0].endswith('-')  and yi[0].endswith('-') or re.sub('\[.*\]', '', xi[0]).replace('-', '') == re.sub('\[.*\]', '', yi[0]).replace('-', ''))  :
            start = end

        # word split up in multiple words (some time == sometime) --> take whole word
        elif ''.join(xi).lower() == yi[0].lower() or ''.join(yi).lower() == xi[0].lower() :
            trans_i = [v for v in trans_aligned[start : end] if 'word' in v]
            timing_i = [v for v in timing_aligned[start : end] if 'word' in v]
            trans_i = {
                    'word' : ''.join(xi),
                    'annotation' : trans_i[0]['annotation'],
                    'pause_type' : trans_i[0]['pause_type'],
                    'is_restart' : trans_i[0]['is_restart']
            }
            timing_i = {
                'word' : ''.join(yi),
                'start' : timing_i[0]['start'],
                'end' : timing_i[-1]['end']
            }
            trans_aligned = trans_aligned[ : start] + [trans_i ] + trans_aligned[end : ]
            timing_aligned = timing_aligned[ : start] + [timing_i] + timing_aligned[end : ]
            start += 1

        # same amount of non empty words (can not be 0) --> missunderstanding, treat as same words
        elif len([w for w in xi if w]) == len([w for w in yi if w]) :
            start = end

        # not compareable --> ignore
        else :
            trans_aligned = trans_aligned[ : start] + trans_aligned[end : ]
            timing_aligned = timing_aligned[ : start] + timing_aligned[end : ]

    return [{'word' : a['word'], 'annotation' : a['annotation'], 'pause_type' : a['pause_type'], 'is_restart' : a['is_restart'], 'start' : b['start'], 'end' : b['end']} for a, b in zip(trans_aligned, timing_aligned)]  


def process_file(annotated_file, word_timing_file_A, word_timing_file_B, ann_patterns=[], timing_patterns=[]) :
    
    # process files
    ann_content = utils.read_file(annotated_file)   
    timing_A_content = utils.read_file(word_timing_file_A)
    timing_B_content = utils.read_file(word_timing_file_B)

    # annotations
    for pattern in ann_patterns :
        ann_content = re.sub(pattern, ' ', ann_content)
    ann_content = ann_content.split('\n')[31:]
    
    ann_A, ann_B = annotations.seperate_speaker(ann_content)

    trans_A, speacial_A = annotations.lines_to_words(ann_A)
    trans_B, speacial_B = annotations.lines_to_words(ann_B)
    special = speacial_A.union(speacial_B)

    trans_A = annotations.merge_abbreviations(trans_A)  
    trans_B = annotations.merge_abbreviations(trans_B)
    
    # list of words. also contains -- , . ? ! and stuff like this  -- always appears as -- --
    trans_A = [x for x in trans_A if not x['annotation'] in [':', '.', ',']]
    trans_B = [x for x in trans_B if not x['annotation'] in [':', '.', ',']]
    
    # timings
    timing_A = timing.extract_timing(timing_A_content, timing_patterns)
    timing_B = timing.extract_timing(timing_B_content, timing_patterns)

    return align(trans_A, timing_A), align(trans_B, timing_B)


def process_dir(annotation_dir, timing_dir, desination_dir, annotation_type='mgd', timing_type='text', ann_patterns=[], timing_patterns=[]) :

    files = utils.get_dir_tuples(
        [annotation_dir, timing_dir, timing_dir], 
        [annotation_type, timing_type, timing_type], 
        [
            lambda s : True, 
            lambda s : s.endswith('A-ms98-a-word'), 
            lambda s : s.endswith('B-ms98-a-word')
        ], 
        lambda s, sn : sn.startswith(s) 
    )    
    files = [ (s, f0, f1[0][1], f2[0][1]) for (s, f0), f1, f2 in files if not s[2:6] in constants.ignore_files]

    for stem, annotation_file, timing_file_A, timing_file_B in ChargingBar("Prepare Transcripts").iter(files) :
        a, b = process_file(str(annotation_file), str(timing_file_A), str(timing_file_B), ann_patterns, timing_patterns)
        utils.write_label_timings_to_file(Path(desination_dir) / stem[2 : 4] / (stem + "A.txt"), a)
        utils.write_label_timings_to_file(Path(desination_dir) / stem[2 : 4] / (stem + "B.txt"), b)
