import statistics_complete.data_gatering as data
import statistics_complete.visualization as visual
import matplotlib.pyplot as plt
import utils.constants as c


# wer comparisons
def plot_wer_comparison(retranscribe_dirs=[None], labels=['no model']) :
    wers = []
    for retranscribe_dir in retranscribe_dirs :
        _, wer = data.calculate_wer(c.manual_seg_dir, c.automatic_align_dir, hesitation_dir=retranscribe_dir)
        wers.append(wer)
    print('# wers =', wers)
    visual.plot_wer_comparison(wers, labels)


# segment lengths and alignment
def statistic_dataset_complete(min_len=[1], manual_dir = c.manual_seg_dir, automatic_dir = c.automatic_align_dir) :
    for minimum_length in min_len :
        lengths, total_length = data.segment_length(manual_dir, automatic_dir, min_len=minimum_length)
        lengths = [ (x[0], y) for x, y in lengths ]
        lengths_word, lengths_time = list(map(list, zip(*lengths)))
        alignments = data.transcript_alignment(manual_dir, automatic_dir, min_len=minimum_length)
        wer, _ = data.calculate_wer(manual_dir, automatic_dir, min_len=minimum_length)
        filled_pauses_per, repetitions_per, r_and_fp_per, hesitations_per = data.percentage(manual_dir, min_len=minimum_length)
        print('# minimum length =', minimum_length)
        print('# total length:', round(total_length / 3600, 2), 'hours')
        print('# percentage of')
        print('# - repetitions:                  ', str(round(repetitions_per, 2)).ljust(4, '0'), '%')
        print('# - filled pauses:                ', str(round(filled_pauses_per, 2)).ljust(4, '0'), '%')
        print('# - repetitions and filled pauses:', str(round(r_and_fp_per, 2)).ljust(4, '0'), '%')
        print('# - hesitations (R or FP):        ', str(round(hesitations_per, 2)).ljust(4, '0'), '%')
        print()
        fig, axs = plt.subplots(2, 2, figsize=(8, 8))
        for y, row in enumerate([[[lengths_word, 'segment length (word)'], [lengths_time, 'segment length (time)']], [[alignments, 'word alignments'], [wer, 'WER']]]) :
            for x, ax  in enumerate(row) :
                axs[y][x].hist(ax[0], bins=100)
                axs[y][x].set_title(ax[1])
        plt.show()


# hesitation transcription
def plot_hesitation_transcription_comparison(retranscribe_dirs=[None], labels=['no model'], manual_dir=c.manual_seg_dir, automatic_dir=c.automatic_align_dir) :
    no_rep = []
    rep = []
    for retranscribe_dir in retranscribe_dirs :
        translation_no_rep, translation_with_rep = data.hesitation_translation(manual_dir, automatic_dir, hesitation_dir=retranscribe_dir)
        no_rep.append(translation_no_rep)
        rep.append(translation_with_rep)

    # optional
    no_rep_total = sum(no_rep[0])
    rep_total = sum(rep[0])
    for nr, r in zip(no_rep, rep) :
        if sum(nr) != no_rep_total : nr[:] = [ int(x * no_rep_total / sum(nr)) for x in nr]
        if sum(r) != rep_total : r[:] = [ int(x * rep_total / sum(r)) for x in r]
    print('# no_rep =', no_rep)
    print('# rep =', rep)

    visual.plot_alignments(no_rep, rep, labels)

from pathlib import Path
import os
def plot_alignment_examples(manual_dir : Path, automatic_dirs : list[tuple[Path, Path | None]], labels : list[str], audio_dir, n, save_dir = c.data_base / 'examples') :
    for file in [ f for f in save_dir.iterdir() if f.is_file() ] :
        os.remove(file)
    data.collect_alignment_examples(manual_dir, automatic_dirs, audio_dir, n, save_dir)
    visual.plot_alignment_examples(labels, save_dir)



def alignment_comparison(dirs : list, labels : list, radius = -1, position=True, length=True) :
    import matplotlib.pyplot as plt
    alignments = []
    for dir in dirs  :
        a = data.transcript_alignment(c.manual_seg_dir, dir, hesitation_radius=radius, min_len=5, position=position, length=length)
        alignments.append(a)

    fig, axs = plt.subplots(1, 1, figsize=(8, 8))
    axs.hist(alignments, bins=100, label=labels)
    axs.legend(loc='upper right')
    plt.show()


def manual_hesitation_gaps(manual_dir, automatic_dir) :
    data_all, data_not_trans = data.manual_hesitation_gaps(manual_dir, automatic_dir)
    visual.plot_gaps(data_all, data_not_trans)


def alignment_metric_comparison(manual_dir, ctc_dir, custom_ctc_dir, cross_attention_dir) :
    all_data = [[[], [], []], [[], [], []]]
    for i, dir in enumerate([ctc_dir, custom_ctc_dir, cross_attention_dir]) :
        dist = data.transcript_alignment_full_package(manual_dir, dir)
        all_data[0][i] = dist[0]
        all_data[1][i] = dist[1]
    visual.plot_alignment_metric(all_data)


def plot_ctc_comparison(manual_dir, automatic_dirs, labels) :
    dists = []
    for automatic_dir in automatic_dirs :
        dists.append(data.transcript_alignment(manual_dir, automatic_dir))
    for dist in dists :
        print( sum(dist) / len(dist))
    visual.plot_ctc_comparison(dists, labels)