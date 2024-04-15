import statistics_complete.data_gatering as data
import statistics_complete.visualization as visual
import utils.constants as c
import utils.file as utils
import utils.console as console

import matplotlib.pyplot as plt
import os

# # #   after preprocessing    # # #
manual_dir_p = c.manual_seg_dir

def dataset_statistic(min_len=[1], manual_dir=manual_dir_p) :
    for minimum_length in min_len :
        lengths = data.manual_segment_length(manual_dir, min_len=minimum_length)
        lengths_by_word, lengths_by_time = list(map(list, zip(*lengths)))
        filled_pauses_per, repetitions_per, r_and_fp_per, hesitations_per = data.hesitation_percentages(manual_dir, min_len=minimum_length)
        
        print('# minimum length =', minimum_length)
        print('# total length:', round(sum(lengths_by_time) / 3600, 2), 'hours')
        print('# percentage of')
        print('# - repetitions:                  ', str(round(repetitions_per, 2)).ljust(4, '0'), '%')
        print('# - filled pauses:                ', str(round(filled_pauses_per, 2)).ljust(4, '0'), '%')
        print('# - repetitions and filled pauses:', str(round(r_and_fp_per, 2)).ljust(4, '0'), '%')
        print('# - hesitations (R or FP):        ', str(round(hesitations_per, 2)).ljust(4, '0'), '%')
        print()

        fig, axs = plt.subplots(1, 2, figsize=(8, 4), num='Segment lengths for minimum length =' + str(minimum_length))
        for i, ax in enumerate([(lengths_by_word, 'segment length (word)'), (lengths_by_time, 'segment length (time)')]) :
            axs[i].hist(ax[0], bins=100)
            axs[i].set_title(ax[1])
        plt.show()


# # #   after transcription    # # #
automatic_dir_p = c.automatic_dir

def manual_automatic_segment_length_by_word_comparison(manual_dir=manual_dir_p, automatic_dir=automatic_dir_p, hesitation_dir=None, min_len=1, filter_condition=lambda f: True) :
    len_data = data.segment_length(manual_dir, automatic_dir, hesitation_dir=hesitation_dir, min_len=min_len, filter_condition=filter_condition)
    len_data = [ x for x, _ in len_data]
    visual.plot_manual_automatic_word_lengths(len_data)


# number of words:                                 1,214,987
# number of not transcribed words:                   121,730   10.02 %
# - in percent to number of words:                   
# number of not transcribed disfluencies:             89,799   7.39 %    73.77 %
# - in percent to number of words:                    
# - in percent to number of not transcribed words:   
    
def percentage_not_transcribed_speech(manual_dir=manual_dir_p, automatic_dir=automatic_dir_p) :
    words, disf = data.untranscribed_speech_disfluencies_percentage(manual_dir, automatic_dir, min_len=1)
    c_transcribed_words, inc_transcribed_words, untranscribed_words = words
    c_transcribed_disf, inc_transcribed_disf, untranscribed_disf = disf
    console.print_table([
        ['', 'correct transcribed', 'incorrect transcribed',  'untranscribed'],
        ['fluent', console.format_number(c_transcribed_words), console.format_number(inc_transcribed_words), console.format_number(untranscribed_words)],
        ['not fluent', console.format_number(c_transcribed_disf), console.format_number(inc_transcribed_disf), console.format_number(untranscribed_disf)],
    ])


def wer_per_segment(manual_dir=manual_dir_p, automatic_dir=automatic_dir_p, min_lens=[1]) :
    for min_len in min_lens :
        wer_and_ops, wer = data.calculate_wer(manual_dir, automatic_dir, min_len=min_len)
        wers, ops = list(map(list, zip(*wer_and_ops)))
        i = sum( [ op.count('i') for op in ops ] )
        d = sum( [ op.count('d') for op in ops ] )
        r = sum( [ op.count('r') for op in ops ] )
        n = sum( [ op.count('n') for op in ops ] )
        print('# WER =', round(wer, 4), 'for minimum length', min_len)
        print('# - insert: ', console.format_number(i, length=10))
        print('# - delete: ', console.format_number(d, length=10))
        print('# - replace:', console.format_number(r, length=10))
        print('# - nothing:', console.format_number(n, length=10))
        print('# - all:    ', console.format_number(i+d+r+n, length=10))
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), num='WER per Segment for minimum length ' + str(min_len))
        ax.hist(wers, bins=100)
        ax.set_title('WER')
        plt.show()
 

def gaps_containing_speech_manual_time_distribution(manual_dir=manual_dir_p, automatic_dir=automatic_dir_p) :
    gaps = data.gaps_containing_speech_manual_time(manual_dir, automatic_dir)
    fig, ax = plt.subplots(1, 1, figsize=(5, 5), num='Gaps Containing Speech (manual time)', tight_layout=True)
    ax.hist(gaps, bins=100)
    ax.set_xlabel('gap length in seconds')
    ax.set_ylabel('number of gaps')
#    ax.set_title('gaps containing not transcribed speech (by manual alignment)')
    ax.set_title('gaps containing not transcribed speech')
    plt.show()
    

# # #     after alignment      # # #
automatic_align_dir_p = c.automatic_align_dir / 'custom ctc' / '0_01'

def gaps_containing_speech_automatic_time_distribution(manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p) :
    gaps = data.gaps_containing_speech_automatic_time(manual_dir, automatic_dir)
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), num='gaps containing not transcribed speech (by automatic alignment)')
    ax.hist(gaps, bins=100)
    ax.set_title('gaps containing not transcribed speech (by automatic alignment)')
    plt.show()


def ctc_default_probability_comparison(automatic_dirs, labels, manual_dir=manual_dir_p) :
    around_dists = []
    full_dists = []
    for automatic_dir in automatic_dirs :
        around_dists.append(data.transcript_alignment(manual_dir, automatic_dir, hesitation_radius=1))    
        full_dists.append(data.transcript_alignment(manual_dir, automatic_dir))

    all_data = []
    for automatic_dir in automatic_dirs :
        speech_t, speech_u, disf_u = data.untranscribed_speech_reachable(manual_dir, automatic_dir)
        all_data.append((
            ([ x[1] for x in speech_t[1]], speech_t[2]), ([ x[1] for x in speech_u[1]], speech_u[2]), ([ x[1] for x in disf_u[1]], disf_u[2])
        ))

    visual.plot_ctc_default_probability_comparison(around_dists, full_dists, labels, all_data)


def alignment_method_comparison(automatic_dirs, labels, manual_dir=manual_dir_p) :
    reachable = []
    for automatic_dir, label in zip(automatic_dirs, labels) :
        all_data = data.untranscribed_speech_reachable(manual_dir, automatic_dir) 
        visual.show_hesitation_gaps(all_data, label) # all_data is altered
        reachable.append( ( ( [ x[1] for x in all_data[0][1] ], all_data[0][2]), ( [ x[1] for x in all_data[1][1] ], all_data[1][2])  ) )
    print(reachable)
    visual.plot_methods_reachable_comparison([ i / 10 for i in range(1, 11)], reachable, labels)

    all_data = []
    for dir in automatic_dirs :
        all_position, all_length, radius_psition, radius_length = data.transcript_alignment_full_package(manual_dir, dir)
        all_data.append( (all_position, all_length, radius_psition, radius_length) )
    visual.plot_alignment_metric(all_data, labels)
 

def best_case_scenario(min_lens, manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p) :
    all_data = data.best_case_scenario(manual_dir, automatic_dir, min_lens)
    for min_len, len_data in zip(min_lens, all_data) :
        print('# minimum gap size =', min_len)
        table = []
        # transcript = i, d, r, n, all, disf. trans., disf. untrans. 
        table.append([
            '', 'insert', 'delete', 'replace', 'nothing', 'all', 'WER', 'disf. trans.', 'disf. untrans.', 'disf. trans. %' 
        ])
        base = len_data[0]
        table.append(
            ['base'] + 
            [ console.format_number(x) for x in base[:5] ] + 
            [ console.format_number(sum(base[:3]) / base[4], 4, length=6) ] + 
            [ console.format_number(x) for x in base[5:7] ] + [ console.format_number(100 * base[5] / sum(base[5:7]), length=5) ]
        )
        for label, row in zip(['partial', '50', 'total'], len_data[1:]) :
            table.append(
                [label] + 
                [ console.format_number(x, force_sign=True) for x in row[:5] ] + 
                [ console.format_number((sum(row[:3] + base[:3])) / (row[4] + base[4]), 4, length=6) ] + 
                [ console.format_number(x, force_sign=True) for x in row[5:7] ] + [ console.format_number( 100 * (base[5] + row[5]) / sum(base[5:7] + row[5:7]), length=5) ]
            )
        console.print_table(table)
        print()


# # # after gap classification # # #
classification_dir_p = c.classification_dir / 'custom ctc'
def classification_model_statistics(manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p, classification_dir=classification_dir_p, threashold=0.5, min_gap=c.MIN_GAP) :
    TP, FP, TN, FN = data.classification_metrics(manual_dir, automatic_dir, classification_dir, threashold, min_gap)
    print('# TP, FP, TN, FN =', TP, FP, TN, FN)
    accuracy = ( TP + TN ) / ( TP + FP + TN + FN )
    precision = ( TP ) / ( TP + FP )
    recall = ( TP ) / ( TP + FN )
    f_score = ( 2 * TP ) / ( 2 * TP + FP + FN )
    
    print('# classificatin model metrics')
    console.print_table( 
        [['metric', 'score']] + 
        [ [label, console.format_number(metric, decimal_places=4, length=6) ] for metric, label in [(accuracy, 'accuracy'), (precision, 'precision'), (recall, 'recall'), (f_score, 'f score')] ]
    )


def not_transcribed_speech_labelling_statistics(manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p, classification_dir=classification_dir_p, threashold=0.5, min_gap=c.MIN_GAP) :
    data_labels, data_gaps, data_hesitations = data.untranscribed_speech_labelling(manual_dir, automatic_dir, classification_dir, threashold, min_gap)
    console.print_tables([
        [
            ['', 'transcribed', 'not transcribed', 'sum'],
            ['predicted', console.format_number( data_labels[1][1][1] ), console.format_number( data_labels[1][1][0] ), console.format_number( sum(data_labels[1][1])) ],
            ['not predicted', console.format_number( data_labels[1][0][1] ), console.format_number( data_labels[1][0][0] ), console.format_number( sum(data_labels[1][0])) ],
            ['not in gap', console.format_number( data_labels[0][1] ), console.format_number( data_labels[0][0] ), console.format_number( sum(data_labels[0]) ) ],
            ['sum', console.format_number( data_labels[1][1][1] + data_labels[1][0][1] + data_labels[0][1] ), console.format_number( data_labels[1][1][0] + data_labels[1][0][0] + data_labels[0][0]), '' ]
        ],
        [
            ['not predicted', 'no untrans.', 'untrans.'],
            ['no trans,'] + [ console.format_number(x) for x in data_gaps[0][0] ],  
            ['trans.'] + [ console.format_number(x) for x in data_gaps[0][1] ]
        ],
        [
            ['predicted', 'no untrans.', 'untrans.'],
            ['no trans.'] + [ console.format_number(x) for x in data_gaps[1][0] ],  
            ['trans.'] + [ console.format_number(x) for x in data_gaps[1][1] ]
        ]
    ])
    console.print_tables([
        [
            ['gaps', 'amount'],
            ['total', console.format_number( sum(data_gaps[1][0] + data_gaps[1][1] + data_gaps[0][0] + data_gaps[0][1]))],
            ['predicted', console.format_number( sum(data_gaps[1][0] + data_gaps[1][1]))],
            ['not predicted', console.format_number( sum(data_gaps[0][0] + data_gaps[0][1]))]
        ],
        [
            ['words', 'amount'],
            ['total', console.format_number( sum(data_labels[1][1] + data_labels[1][0]) + sum(data_labels[0]))],
            ['in gaps', console.format_number( sum(data_labels[1][1] + data_labels[1][0]))]
        ],
        [
            ['hesitations', 'not transcribed', 'transcribed'],
            ['not labelled'] + [ console.format_number(x) for x in data_hesitations[0] ],
            ['labelled'] + [ console.format_number(x) for x in data_hesitations[1] ]
        ]  
    ])    

# # #  after retranscription   # # #
def retranscription_models_comparison(retranscribe_dirs, labels, manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p, threshold=0.5) :
    tables = []
    for retranscibe_dir, label in zip(retranscribe_dirs, labels) :
        x = data.percentage_of_captured_words(manual_dir, automatic_dir, retranscibe_dir, threshold=threshold)
        table = []
        table.append([label, 'empty', 'new', 'not new'])
        table.append(['empty'] + [ console.format_number(a) for a in x[0]])
        table.append(['transcribed'] + [ console.format_number(a) for a in x[1]])
        table.append(['not trans.'] + [ console.format_number(a) for a in x[2]])
        tables.append(table)
    console.print_tables(tables)


from matplotlib.lines import Line2D

def final_statistic(retranscribe_dirs, labels, manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p, min_lens=[ i / 10 for i in range(1, 11) ], threshold=0.5) :
    # (wer_data_base, disf_data_base), (wer_data, disf_data) = data.final_statistic(manual_dir, automatic_dir, retranscribe_dirs, min_lens, threshold=threshold)
    # ('#', 'wer_data_base =', wer_data_base)
    # ('#', 'disf_data_base =', disf_data_base)
    # ('#', 'wer_data =', wer_data)
    # ('#', 'disf_data =', disf_data)
    wer_data_base = [8599, 20880, 7807, 160450]
    disf_data_base = [23458, 16660]
    wer_data = [[[22000, 9139, 15962, 164036], [16184, 9468, 15755, 163914], [14195, 10129, 15322, 163686], [13025, 11139, 14670, 163328], [12237, 12149, 14026, 162962], [11421, 13006, 13473, 162658], [10438, 13888, 12866, 162383], [9843, 14710, 12322, 162105], [9506, 15467, 11838, 161832], [9279, 16168, 11372, 161597]], 
                [[22106, 9245, 18886, 161006], [16257, 9541, 18589, 161007], [14262, 10196, 17950, 160991], [13087, 11201, 16998, 160938], [12303, 12215, 16054, 160868], [11486, 13071, 15261, 160805], [10481, 13931, 14454, 160752], [9879, 14746, 13684, 160707], [9532, 15493, 12987, 160657], [9303, 16192, 12336, 160609]], 
                [[22108, 9247, 18462, 161428], [16256, 9540, 18167, 161430], [14261, 10195, 17547, 161395], [13085, 11199, 16643, 161295], [12299, 12211, 15761, 161165], [11486, 13071, 15013, 161053], [10482, 13932, 14242, 160963], [9879, 14746, 13504, 160887], [9534, 15495, 12832, 160810], [9303, 16192, 12226, 160719]], 
                [[22082, 9221, 18293, 161623], [16227, 9511, 18036, 161590], [14236, 10170, 17479, 161488], [13073, 11187, 16603, 161347], [12293, 12205, 15705, 161227], [11484, 13069, 14910, 161158], [10480, 13930, 14133, 161074], [9876, 14743, 13412, 160982], [9528, 15489, 12749, 160899], [9296, 16185, 12140, 160812]], 
                [[22076, 9215, 18223, 161699], [16221, 9505, 17969, 161663], [14232, 10166, 17410, 161561], [13070, 11184, 16541, 161412], [12287, 12199, 15646, 161292], [11478, 13063, 14860, 161214], [10476, 13926, 14095, 161116], [9872, 14739, 13379, 161019], [9527, 15488, 12715, 160934], [9295, 16184, 12109, 160844]]]
    disf_data = [[[33733, 6385], [33531, 6587], [32977, 7141], [32095, 8023], [31194, 8924], [30424, 9694], [29628, 10490], [28891, 11227], [28205, 11913], [27581, 12537]], 
                    [[31833, 8285], [31952, 8166], [31790, 8328], [31256, 8862], [30580, 9538], [29940, 10178], [29287, 10831], [28664, 11454], [28030, 12088], [27453, 12665]], 
                    [[31497, 8621], [31598, 8520], [31478, 8640], [31008, 9110], [30381, 9737], [29771, 10347], [29142, 10976], [28547, 11571], [27935, 12183], [27373, 12745]], 
                    [[32893, 7225], [32909, 7209], [32458, 7660], [31639, 8479], [30784, 9334], [30053, 10065], [29339, 10779], [28669, 11449], [28022, 12096], [27442, 12676]], 
                    [[32998, 7120], [32997, 7121], [32516, 7602], [31679, 8439], [30818, 9300], [30081, 10037], [29360, 10758], [28682, 11436], [28035, 12083], [27453, 12665]]]
    visual.final_statistics(labels, min_lens, wer_data_base, disf_data_base, wer_data, disf_data)


import utils.wer_alignment as alignment

def transcript_comparison(retranscribe_dirs, labels, manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p, min_len=0.3, threshold=0.9, number_of_examples=30) :
    all_data = []
    for retranscribe_dir in retranscribe_dirs :
        all_data.append( data.transcript_comparison(retranscribe_dir, manual_dir, automatic_dir, min_len, threshold, number_of_examples) )
    
    for examples, model in zip(all_data, labels) :
        print(model)
        for manual, automatic in examples :
            print(' '.join([ w['word'] for w in manual ]).ljust(40), '&', ' '.join([ w['word'] if not w['word'] or w['original'] else  '\\textbf{' + w['word'] + '}' for w in automatic ]), '\\\\')
#            alignment.print_words([ w['word'] for w in manual ], [ w['word'] if not w['word'] or w['original'] else  '>' + w['word'] + '<' for w in automatic ])            
    
# # #         general          # # #
example_dir_p = c.data_base / 'examples'
audio_dir_p = c.audio_dir

def alignment_visualisation(dirs, number_of_examples, manual_dir=manual_dir_p, example_dir=example_dir_p) :
    'dirs = [(dir, hesitation_dir (optional), label)]'

    if example_dir.is_dir() :
        for file in [ f for f in example_dir.iterdir() if f.is_file() ] :
            os.remove(file)
    data.collect_alignment_examples(manual_dir, dirs, audio_dir_p, number_of_examples, example_dir)
    visual.plot_alignment_examples( ['manual'] + [ dir[2] for dir in dirs ], example_dir)
