import utils.statistics as stats
import utils.constants as constants
import matplotlib.pyplot as plt
import numpy as np
import supervised_data_preperation.visualization.visualize as visual

def round(number) :
    return int(number * 1000) / 1000


def plot_hesitation_translation(with_rep, no_rep) :
    species = ("With Repetitions", "Without Repetitions")
    penguin_means = {
        'word': (with_rep[1][0], no_rep[1][0]),
        'hesitation': (with_rep[1][1], no_rep[1][1]),
        'silence': (with_rep[1][2], no_rep[1][2]),
    }

    x = np.arange(len(species))  # the label locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots(layout='constrained')
    for multiplier, (attribute, measurement) in enumerate(penguin_means.items()):
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)

    ax.set_title('Hesitations translated as')
    ax.set_xticks(x + width, species)
    ax.legend(loc='upper left', ncols=3)
    # ax.set_ylim(0, 1)

    plt.show()

def plot_lengths_wer_alignment(lengths_word, lengths_time, wer, wer_no_rep, wer_clean, alignments) :
    n_bins = 50
    dist = list( zip( [lengths_word, lengths_time, wer, wer_no_rep, wer_clean, alignments], ['lengths (word)', 'lengths (time)', 'wer (all)', 'wer (no repetitions)', 'wer (clean)', 'transcript alignment (metric)'] ) )
    fig, axs = plt.subplots(1, len(dist), tight_layout=True)
    for index, distribution, title in dist :
        axs[index].hist(distribution, bins=n_bins)
        axs[index].set_title(title)
    plt.show()

def to_bins(dist, n_bins = 100, lower_bound = None, upper_bound = None) :
    if lower_bound == None :
        lower_bound = int(min(dist)) - 0.1
    if upper_bound == None :
        upper_bound = int(max(dist)) + 0.1
        if max(dist) >= upper_bound :
            upper_bound = int(upper_bound + 1)
    
    bins = [0] * n_bins
    l = upper_bound - lower_bound

    for d in dist :
        pos = int((d - lower_bound) / l * n_bins)
        bins[pos] += 1
    return [[lower_bound + i / n_bins * (upper_bound - lower_bound) for i in range(n_bins)], bins]

    
def print_full_statistics(min_len=[]) :
    for minimum_length in min_len :
        translation_with_rep = stats.sb_hesitation_translation(constants.manual_seg_dir, constants.audio_automatic_align_dir, constants.transcript_align_dir, min_len=minimum_length)
        translation_no_rep = stats.sb_hesitation_translation(constants.manual_seg_dir, constants.audio_automatic_align_dir, constants.transcript_align_dir, with_repetitions=False, min_len=minimum_length)

        lengths, total_length = stats.segment_length(constants.manual_seg_dir, min_len=minimum_length)
        lengths_word, lengths_time = list(map(list, zip(*lengths)))
        wers, wers_whole = stats.wer(constants.manual_seg_dir, constants.transcript_align_dir, min_len=minimum_length)
        wer_all, wer_speech, wer_rep, wer_pauses, wer_rep_and_pauses, wer_hesitations = list(map(list, zip(*wers)))

        alignments, gaps = stats.transcript_alignment(constants.manual_seg_dir, constants.audio_automatic_align_dir, constants.transcript_align_dir, min_len=minimum_length)
        filled_pauses_per, repetitions_per, r_and_fp_per, hesitations_per = stats.percentage(constants.manual_seg_dir, min_len=minimum_length)

        visual.plot_hesitation_translation(translation_with_rep, translation_no_rep)
        # * --> (bins, distribution)
        visual.plot_all(
            [*to_bins(lengths_word), 'segment length (word)'],
            [*to_bins(lengths_time), 'segment length (time)'],
            [*to_bins(alignments), 'word alignments'],
            [*to_bins(wer_all), 'wer all'],
            [*to_bins(wer_speech), 'wer speech'],
            [*to_bins(wer_rep), 'wer repetitions'],
            [*to_bins(wer_pauses), 'wer filled pauses'],
            [*to_bins(wer_rep_and_pauses), 'wer repetitions and filled pauses'],
            [*to_bins(wer_hesitations), 'wer hesitations'],
            [*to_bins(gaps), 'gaps']
        )
        print('# minimum length =', minimum_length)
        # print('# hesitation translation')
        # print('translation_of_repetitions =')
        # print('translation_of_filled pauses =')
        # print('translation_of_repetitions_and_filled_pauses =')
        # print('translation_of_hesitations_R_or_FP =')
        # print('translation_with_rep =              ', translation_with_rep)
        # print('translation_no_rep =                ', translation_no_rep)
        # print()
        # print('# segments length')
        # print('segments_word_lengths =             ', to_bins(lengths_word))
        # print('segments_time_lengths =             ', to_bins(lengths_time))
        # print()
        # print('# WER')
        # print('wer_all =                           ', to_bins(wer_all))
        # print('wer_speech =                        ', to_bins(wer_speech))
        # print('wer_repetitions =                   ', to_bins(wer_rep))
        # print('wer_filled_pauses =                 ', to_bins(wer_pauses))
        # print('wer_repetitions_and_filled_pauses = ', to_bins(wer_rep_and_pauses))
        # print('wer_hesitations_R_or_FP =           ', to_bins(wer_hesitations))
        print('# wer (all, speech, repetitions, filled pauses, repetitions and filled pauses, hesitations)', [round(x) for x in wers_whole])
        # print()
        # print('# rest')
        # print('word_alignments =                   ', to_bins(alignments))
        # print('gaps =                              ', to_bins(gaps))
        print('# total length (hours):', round(total_length / 3600))
        print('# percentage of repetitions:', round(repetitions_per))
        print('# percentage of filled pauses:', round(filled_pauses_per))
        print('# percentage of repetitions and filled pauses:', round(r_and_fp_per))
        print('# percentage of hesitations (R or FP):', round(hesitations_per))