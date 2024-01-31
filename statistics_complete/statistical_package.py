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
    words, untranscribed_words, untranscribed_hesitations = data.untranscribed_speech_disfluencies_percentage(manual_dir, automatic_dir, min_len=1)
    table = [
        ['',                            'total',                                          'per words',                                                          'per untranscribed'],
        ['number of words words',       console.format_number(words),                     '',                                                                   ''],
        ['not transcribed words',       console.format_number(untranscribed_words),       console.format_number(untranscribed_words / words * 100) + ' %',      ''],
        ['nottranscribed disfluencies', console.format_number(untranscribed_hesitations), console.format_number(untranscribed_hesitations / words * 100)+ ' %', console.format_number(untranscribed_hesitations / untranscribed_words * 100) + ' %']
    ]
    console.print_table(table)


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
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), num='Gaps Containing Speech (manual time)')
    ax.hist(gaps, bins=100)
    ax.set_title('gaps containing not transcribed speech (by manual alignment)')
    plt.show()
    

# # #     after alignment      # # #
automatic_align_dir_p = c.automatic_align_dir / '0'

def gaps_containing_speech_automatic_time_distribution(manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p) :
    gaps = data.gaps_containing_speech_automatic_time(manual_dir, automatic_dir)
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), num='gaps containing not transcribed speech (by automatic alignment)')
    ax.hist(gaps, bins=100)
    ax.set_title('gaps containing not transcribed speech (by automatic alignment)')
    plt.show()


def ctc_default_probability_comparison(automatic_dirs, labels, manual_dir=manual_dir_p) :
    dists = []
    for automatic_dir in automatic_dirs :
        dists.append(data.transcript_alignment(manual_dir, automatic_dir))
    print('# CTC default probability comparison')
    for dist, label in zip(dists, labels) :
        print('#', label + ':', console.format_number(sum(dist) / len(dist), 4))
    visual.plot_ctc_comparison(dists, labels)


def alignment_method_comparison(automatic_dirs, labels, manual_dir=manual_dir_p) :
    for automatic_dir, label in zip(automatic_dirs, labels) :
        data_containing, data_reachable, number_of_hesitations = data.untranscribed_speech_reachable(manual_dir, automatic_dir)
        visual.show_hesitation_gaps(number_of_hesitations, data_containing, data_reachable, label)
 
    all_data = [[[], [], []], [[], [], []]]
    for i, dir in enumerate(automatic_dirs) :
        dist = data.transcript_alignment_full_package(manual_dir, dir)
        all_data[0][i] = dist[0]
        all_data[1][i] = dist[1]
    visual.plot_alignment_metric(all_data, labels)
 

def best_case_scenario(min_lens, manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p) :
    all_data = data.best_case_scenario(manual_dir, automatic_dir, min_lens)
    for min_len, len_data in zip(min_lens, all_data) :
        print('# minimum gap size =', min_len)
        table = []
        table.append([
            '', 'insert', 'delete', 'replace', 'nothing', 'all', 'WER'
        ])
        base = len_data[0]
        table.append(
            ['base'] + [ console.format_number(x, force_sign=True) for x in base] + [ console.format_number(sum(base[:3]) / base[4], 4, length=6) ]
        )
        for label, row in zip(['partial', '50', 'total'], len_data[1:]) :
            table.append(
                [label] + [ console.format_number(x, force_sign=True) for x in row] + [ console.format_number((sum(row[:3]) + sum(base[:3])) / (row[4] + base[4]), 4, length=6) ]
            )
        console.print_table(table)
        print()


# # # after gap classification # # #
classification_dir_p = c.classification_dir

DATA_SPLIT = 3916
def classification_model_statistics(manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p, classification_dir=classification_dir_p) :
    TP, FP, TN, FN = data.classification_metrics(manual_dir, automatic_dir, classification_dir)
    print(TP, FP, TN, FN)
    accuracy = ( TP + TN ) / ( TP + FP + TN + FN )
    precision = ( TP ) / ( TP + FP )
    recall = ( TP ) / ( TP + FN )
    f_score = ( 2 * TP ) / ( 2 * TP + FP + FN )
    
    print('# classificatin model metrics')
    console.print_table( [['metric', 'score']] + [ [label, console.format_number(metric, decimal_places=4, length=6) ] for metric, label in [(accuracy, 'accuracy'), (precision, 'precision'), (recall, 'recall'), (f_score, 'f score')] ])


def not_transcribed_speech_labelling_statistics(manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p, classification_dir=classification_dir_p) :
    (untranscribed_words, missed_words), (correct_labels, incorrect_labls) = data.untranscribed_speech_labelling(manual_dir, automatic_dir, classification_dir)
    print('# labeling statistics:')
    print('# untranscribed words:', console.format_number(untranscribed_words, length=6))
    print('# - captured words    ', console.format_number(untranscribed_words - missed_words, length=6), '(', round(100 * (untranscribed_words - missed_words) / untranscribed_words, 2), '% )')
    print('# - missed words:     ', console.format_number(missed_words, length=6), '(', round(100 * missed_words / untranscribed_words, 2), '% )')
    print('# correct labels:     ', console.format_number(correct_labels, length=6), '(', round(100 * correct_labels / (correct_labels + incorrect_labls), 2), '% )')
    print('# incorrect labls:    ', console.format_number(incorrect_labls, length=6), '(', round(100 * incorrect_labls / (correct_labels + incorrect_labls), 2), '% )')


# # #  after retranscription   # # #
def retranscription_models_comparison(retranscribe_dirs, labels, manual_dir=manual_dir_p, automatic_dir=automatic_align_dir_p) :
    tables = []
    for retranscibe_dir, label in zip(retranscribe_dirs, labels) :
        x = data.percentage_of_captured_words(manual_dir, automatic_dir, retranscibe_dir)
        table = []
        table.append([label, 'empty', 'new', 'not new'])
        table.append(['empty'] + [ console.format_number(a) for a in x[0]])
        table.append(['transcribed'] + [ console.format_number(a) for a in x[1]])
        table.append(['not trans.'] + [ console.format_number(a) for a in x[2]])
        tables.append(table)
    console.print_tables(tables)


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
