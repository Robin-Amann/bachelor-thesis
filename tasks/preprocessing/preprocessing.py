import tasks.preprocessing.annotations as annotations
import tasks.preprocessing.timings as timing
import utils.file as utils
from progress.bar import ChargingBar
import re
import utils.wer_alignment as wer
from pathlib import Path

def align(trans_p, timing_p) :
    trans = trans_p.copy()
    timing = timing_p.copy()
    trans_aligned, timing_aligned, operations = wer.align_words(trans, timing, {})

    start = 0
    end = 0
    while start < len(operations) :
        # find not machting part
        while start < len(operations) and operations[start] == 'n' :
            start += 1
        end = start
        while end < len(operations) and operations[end] != 'n' :
            end += 1

        # extract not matching part
        xi = [w['word'] for w in trans_aligned[start:end] if 'word' in w]
        yi = [w['word'] for w in timing_aligned[start:end] if 'word' in w]

        # one is empty --> missing information
        if (not ''.join(xi)) or (not ''.join(yi)) :
            trans_aligned = trans_aligned[ : start] + trans_aligned[end : ]
            timing_aligned = timing_aligned[ : start] + timing_aligned[end : ]
            operations = operations[ : start] + operations[end : ]

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
            operations = operations[ : start] + ['n'] + operations[end : ]
            start += 1

        # same amount of non empty words (can not be 0) --> missunderstanding, treat as same words
        elif len([w for w in xi if w]) == len([w for w in yi if w]) :
            start = end

        # not compareable --> ignore
        else :
            trans_aligned = trans_aligned[ : start] + trans_aligned[end : ]
            timing_aligned = timing_aligned[ : start] + timing_aligned[end : ]
            operations = operations[ : start] + operations[end : ]
    
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
    trans_A = [x for x in trans_A if re.search("[a-zA-Z]", x['word'])]
    trans_B = [x for x in trans_B if re.search("[a-zA-Z]", x['word'])]
    
    # timings
    timing_A = timing.extract_timing(timing_A_content, timing_patterns)
    timing_B = timing.extract_timing(timing_B_content, timing_patterns)

    # that I even have to add this is stupid
    operations = wer.get_operations([w['word'].lower() for w in trans_A], [w['word'].lower() for w in timing_A])
    if wer.calculate_wer(operations) > 0.5 :
        operations = wer.get_operations([w['word'].lower() for w in trans_A], [w['word'].lower() for w in timing_B])
        if wer.calculate_wer(operations) > 0.5 :
            raise ValueError("preprocessing error: transcript and timing does not match")
        else :
            return annotated_file.stem[2:6], annotated_file.stem[2:6]

    return align(trans_A, timing_A), align(trans_B, timing_B)


def process_dir(annotation_dir, timing_dir, desination_dir, annotation_type='mgd', timing_type='text', ann_patterns=[], timing_patterns=[]) :

    files = utils.get_dir_tuples(
        [(annotation_dir, lambda f: f.stem[2:6], None, annotation_type), 
         (timing_dir, lambda f: f.stem[2:6], lambda f : f.stem.endswith('A-ms98-a-word'), timing_type), 
         (timing_dir, lambda f: f.stem[2:6], lambda f : f.stem.endswith('B-ms98-a-word'), timing_type)], 
        lambda f : True)
  
    swapped = []
    for annotation_file, timing_file_A, timing_file_B in ChargingBar("Prepare Transcripts").iter(files) :
        a, b = process_file(annotation_file, timing_file_A, timing_file_B, ann_patterns, timing_patterns)
        stem = annotation_file.stem
        if type(a) == str :
            swapped.append(a)
        else :
            utils.write_dict(Path(desination_dir) / stem[2 : 4] / (stem + "A.txt"), a)
            utils.write_dict(Path(desination_dir) / stem[2 : 4] / (stem + "B.txt"), b)
    
    print("preprocessing: swap transcripts", swapped)


# example
# annotation: Okay Uh first um I need to know uh        how do you feel about uh about sending uh an elderly uh family member to a nursing home Yes Yeah Uh-huh Yeah Yeah Yeah Yeah   Yeah Uh-huh Uh-huh Yeah Probably the hardest thing in in my family uh my grandmother she had to be put in a nursing home and um she had used the walker for for quite some     time probably about six to nine months And um she had a fall and uh finally uh she had    Parkinson's disease and it got so much that she could not take care of her house        Then she lived in an apartment and uh that was even harder actually Because it was you know it was just a change of change of location and it was very disturbing for her because she had been so used to traveling I mean she tr-         she had she had children all across the United States and you know she spent nine months out of the year just visiting her children And um that was pretty heart-rending for her I think when she finally came to the realization that you know no I can    not I can    not take care of myself Yeah I mean for somebody who is you know for most of their life has has uh not just merely had a farm but had ten children had a farm ran everything because her husband was away in the coal mines And you know facing that situation it's it's quite a dilemma I think Yeah Well my uh my uh probably one of the biggest decisions I think that was very strengthening for our family was rather than have one child make that decision than just delegate it I think that they they had a great deal of um all the brothers and sisters got together and they actually had a conference And I mean it was just it was probably one of the most strengthening things for our family getting down together and doing that And and just the children were involved in the decision because it involved just them And you know making that decision and then finding a place and everybody had duties to perform You know whether it was just you know giving money or whether it was actually taking part    in a lot of the decision making you know like finding   a proper nursing home And they I know They and well they had well they had they had seen it coming So so I mean it I mean I I I I har-      I I truly wish that if something like that were to happen that my children would do something like that for me Yeah Yeah Well we we Yeah Uh-huh Yeah Uh-huh Um Yeah Yeah Well with my with my grandmother I think it was it was such that uh that she did not have the problem with she was very
# timing:     okay uh first um i need to know uh h[ow]- how do you feel about uh about sending um an elderly uh family member to a nursing home yes yeah um-hum yes  yeah yeah um-hum                    yeah probably the hardest thing in in my family uh my grandmother she had to be put in   nursing home and um she had used a   walker for for quite sometime      probably about six to nine months and um she had a fall and uh finally uh she had uh Parkinson's Disease and it got so much that she could not take care of her house sh[e]- then she lived in an apartment and um that was even harder actually because it was you know it was just a change of change of location and it was very disturbing for her because she had been so used to traveling i mean she tr[aveled]- she had she had children all across the United States and you know she spent nine months out of the year just visiting her children and um that was pretty heartrending  for her i think when she finally came to the realization that you know no i cannot     i cannot     take care of myself yeah i mean for somebody who is you know for most of their life has has uh not just merely had a farm but had ten children had a farm ran everything because her husband was away in the coal mines and you know facing that situation it   it's quite a dilemma i think yeah well my uh my uh probably one of the biggest decisions i think that was very strengthened  for our family was rather than have one child make that decision than just delegate it i think that they they had a great deal of um all the brothers and sisters got together and they actually had a conference and i mean it was just it was probably one of the most strengthening things for our family getting down together and doing that and and just the children were involved in the decision because it involved just them and you know making that decision and then finding a place and everybody had duties to perform you know whether it was just you know giving money or whether it was actually taking part in in a lot of the decision making you know like finding a a proper nursing home and they i know they and well they had well they had they had seen it coming so so i mean it i mean i i i i hard[ly]- i i truly wish that if something like that were to happen that my children would do something like that for me yeah yeah well we we yeah um-hum yeah um-hum    yeah yeah well with my with my grandmother i think it was it was such that uh that she did not have the problem with she was very
# result:     Okay Uh first um I need to know uh        how do you feel about uh about sending uh an elderly uh family member to a nursing home Yes Yeah Uh-huh Yeah Yeah Yeah                           Yeah Probably the hardest thing in in my family uh my grandmother she had to be put in   nursing home and um she had used the walker for for quite sometime      probably about six to nine months And um she had a fall and uh finally uh she had    Parkinson's disease and it got so much that she could not take care of her house        Then she lived in an apartment and uh that was even harder actually Because it was you know it was just a change of change of location and it was very disturbing for her because she had been so used to traveling I mean she tr-         she had she had children all across the United States and you know she spent nine months out of the year just visiting her children And um that was pretty heart-rending for her I think when she finally came to the realization that you know no I cannot     I cannot     take care of myself Yeah I mean for somebody who is you know for most of their life has has uh not just merely had a farm but had ten children had a farm ran everything because her husband was away in the coal mines And you know facing that situation it's it's quite a dilemma I think Yeah Well my uh my uh probably one of the biggest decisions I think that was very strengthening for our family was rather than have one child make that decision than just delegate it I think that they they had a great deal of um all the brothers and sisters got together and they actually had a conference And I mean it was just it was probably one of the most strengthening things for our family getting down together and doing that And and just the children were involved in the decision because it involved just them And you know making that decision and then finding a place and everybody had duties to perform You know whether it was just you know giving money or whether it was actually taking part    in a lot of the decision making you know like finding   a proper nursing home And they I know They and well they had well they had they had seen it coming So so I mean it I mean I I I I har-      I I truly wish that if something like that were to happen that my children would do something like that for me Yeah Yeah Well we we Yeah Uh-huh Yeah           Yeah Yeah Well with my with my grandmother I think it was it was such that uh that she did not have the problem with she was very