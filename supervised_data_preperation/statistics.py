import utils.statistics as stats
import utils.constants as constants
import matplotlib.pyplot as plt
import numpy as np

s = 4

def plot_hesitation_translation(with_rep, no_rep) :
    species = ("With Repetitions", "Without Repetitions")
    penguin_means = {
        'word': (with_rep[0], no_rep[0]),
        'hesitation': (with_rep[1], no_rep[1]),
        'silence': (with_rep[2], no_rep[2]),
    }

    x = np.arange(len(species))  # the label locations
    width = 0.2  # the width of the bars
    fig, ax = plt.subplots(layout='constrained', figsize=(2*s, 2*s))
    fig.tight_layout()
    for multiplier, (attribute, measurement) in enumerate(penguin_means.items()):
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)

    ax.set_title('Hesitations translated as')
    ax.set_xticks(x + width, species)
    ax.legend(loc='upper right', ncols=3)
    # ax.set_ylim(0, 1)
    plt.show()


def plot_all(ax00, ax01, ax02, ax03, ax04, n=100) :
    fig, axs = plt.subplots(2, 3, figsize=(3 * s, 2 *s))
    for y, row in enumerate([[ax00, ax01, ax02], [ax03, ax04]]) :
        for x, ax  in enumerate(row) :
            axs[y][x].hist(ax[0], bins=n)
            axs[y][x].set_title(ax[1])

    axs[1][2].axis('off')
    plt.show()

    
def print_full_statistics(min_len=[], retranscribe_dirs=None) :
    for retranscribe_dir in retranscribe_dirs :
        for minimum_length in min_len :
            translation_no_rep, translation_with_rep = stats.sb_hesitation_translation(constants.manual_seg_dir, constants.automatic_align_dir, constants.transcript_align_dir, retranscribe_dir=retranscribe_dir, min_len=minimum_length)
            
            print('calculate lengths')
            lengths, total_length = stats.segment_length(constants.manual_seg_dir, min_len=minimum_length)
            lengths_word, lengths_time = list(map(list, zip(*lengths)))
            print('calculate wer')
            wer_dist, wer = stats.wer(constants.manual_seg_dir, constants.automatic_align_dir, retranscribe_dir=retranscribe_dir, min_len=minimum_length)
            print('calculate alignments')
            alignments, gaps = stats.transcript_alignment(constants.manual_seg_dir, constants.automatic_align_dir, constants.transcript_align_dir, min_len=minimum_length)
            filled_pauses_per, repetitions_per, r_and_fp_per, hesitations_per = stats.percentage(constants.manual_seg_dir, min_len=minimum_length)

            plot_hesitation_translation(translation_with_rep, translation_no_rep)
            plot_all(
                [lengths_word, 'segment length (word)'],
                [lengths_time, 'segment length (time)'],
                [alignments, 'word alignments'],
                [wer_dist, 'wer all'],
                [gaps, 'gaps']
            )

            print('# minimum length =', minimum_length)
            print('# wer:', round(wer, 4))
            print('# total length:', round(total_length / 3600, 2), 'hours')
            print('# percentage of')
            print('# - repetitions:                  ', round(repetitions_per, 2), '%')
            print('# - filled pauses:                ', round(filled_pauses_per, 2), '%')
            print('# - repetitions and filled pauses:', round(r_and_fp_per, 2), '%')
            print('# - hesitations (R or FP):        ', round(hesitations_per, 2), '%')