import tasks.transcript_alignment.wer_align as wer 
import utils.file as utils
from progress.bar import ChargingBar
from pathlib import Path
import re

def lines_to_words(ann) :
    trans = []
    special = set()
    pause_type = ""
    is_restart = False
    for line in ann :
        for part in line.split() :
            if part.startswith('{') :
                pause_type = part[1]
                continue
            elif part.endswith('}') :
                pause_type = ""
                continue
            elif part.startswith('[') :
                is_restart = True
                continue
            elif part.endswith(']') :
                is_restart = False
                continue
            elif len(part.split('/')) == 2 :
                word, annotation = part.split('/')
                trans.append({
                    'word' : word,
                    'annotation' : annotation,
                    'pause_type' : pause_type,
                    'is_restart' : is_restart
                })
            else :
                special.add(part)
    return trans, special


def merge_abbreviations(trans) :
    for i in range(len(trans) - 1) :
        if "'" in trans[i + 1]['word'] :
            trans[i]['word'] = trans[i]['word'] + trans[i+1]['word']
            trans[i]['annotation'] = trans[i]['annotation'] + "+" + trans[i+1]['annotation']
            trans[i+ 1]['word'] = ""
    trans = [w for w in trans if w['word']]
    return trans


def extract_timing(timing_content, timing_patterns) :
    for pattern in timing_patterns :
        timing_content = re.sub(pattern, ' ', timing_content)
    timing_content = timing_content.split('\n')
    
    timing_content = [l for l in timing_content if l and not l.isspace()]
    x = []
    for line in timing_content :
        _, s, e, w = line.split()
        if not (w.startswith('[') and w.endswith(']')) :
            x.append({'word': w, 'start': float(s), 'end': float(e)})
    return x


# trans {word, annotation, pause_type, is_restart}
# timing {word, start, end}
# both lowered
def align(trans_p, timing_p) :
    trans = trans_p.copy()
    timing = timing_p.copy()
    operations = wer.get_operations([w['word'] for w in trans], [w['word'] for w in timing])
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
        elif ''.join(xi) == yi[0] or ''.join(yi) == xi[0] :
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


def lower_words(words) :
    for value in words :
        value['word'] = value['word'].lower()    
    

def seperate_speaker(ann_content) :
    ann_content_temp = []
    start = 0
    while start < len(ann_content) :
        end = start
        while end < len(ann_content) and ann_content[end] != '' :
            end += 1
        ann_content_temp.append(ann_content[start:end])
        start = end + 1
    ann_A = [block[1:] for block in ann_content_temp if len(block) > 1 and 'SpeakerA' in block[0]]
    ann_B = [block[1:] for block in ann_content_temp if len(block) > 1 and 'SpeakerB' in block[0]]
    # flatten lists
    return [line for block in ann_A for line in block], [line for block in ann_B for line in block]


def process_file(annotated_file, word_timing_file_A, word_timing_file_B, ann_patterns=[], timing_patterns=[]) :
    # read files
    ann_content = utils.read_file(annotated_file)   
    timing_A_content = utils.read_file(word_timing_file_A)
    timing_B_content = utils.read_file(word_timing_file_B)

    # remove patterns
    for pattern in ann_patterns :
        ann_content = re.sub(pattern, ' ', ann_content)
    ann_content = ann_content.split('\n')[31:]
    
    # seperate speaker blocks
    ann_A, ann_B = seperate_speaker(ann_content)
    
    # lines to words
    trans_A, speacial_A = lines_to_words(ann_A)
    trans_B, speacial_B = lines_to_words(ann_B)
    special = speacial_A.union(speacial_B)

    trans_A = merge_abbreviations(trans_A)  
    trans_B = merge_abbreviations(trans_B)
    
    # list of words. also contains -- , . ? ! and stuff like this  -- always appears as -- --
    trans_A = [x for x in trans_A if not x['annotation'] in [':', '.', ',']]
    trans_B = [x for x in trans_B if not x['annotation'] in [':', '.', ',']]
    
    # # timings
    timing_A = extract_timing(timing_A_content, timing_patterns)
    timing_B = extract_timing(timing_B_content, timing_patterns)

    lower_words(trans_A)  
    lower_words(trans_B)  
    lower_words(timing_A)  
    lower_words(timing_B)  

    return align(trans_A, timing_A), align(trans_B, timing_B)


def process_dir(annotation_dir, timing_dir, desination_dir, annotation_type='mgd', timing_type='text', ann_patterns=[], timing_patterns=[]) :
    annotation_files = utils.get_directory_files(annotation_dir, annotation_type)
    annotation_files = [(f.stem, f) for f in annotation_files]
    timing_files = utils.get_directory_files(timing_dir, timing_type)
    timing_files = [(f.stem, f) for f in timing_files if f.stem.endswith('word')]

    desination_dir = Path(desination_dir)
    for stem, file in ChargingBar("Prepare Transcripts").iter(annotation_files) :
        timing_a = next(y for x, y in timing_files if x.startswith(stem + "A"))
        timing_b = next(y for x, y in timing_files if x.startswith(stem + "B"))
        a, b = process_file(str(file), str(timing_a), str(timing_b), ann_patterns, timing_patterns)
        utils.write_label_timings_to_file(desination_dir / stem[2 : 4] / (stem + "A.txt"), a)
        utils.write_label_timings_to_file(desination_dir / stem[2 : 4] / (stem + "B.txt"), b)
