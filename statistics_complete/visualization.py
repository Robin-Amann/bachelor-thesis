import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import utils.file as utils
import utils.constants as c
import statistics_complete.data_gatering as data

# length of automatic and manual
def plot_manual_automatic_word_lengths(manual_dir, automatic_dir, hesitation_dir=None) :
    matplotlib.rcParams["figure.figsize"] = [10, 10]
    plt.xlim((0, 150))
    plt.ylim((0, 150))
    len_data, _ = data.segment_length(manual_dir, automatic_dir, hesitation_dir, 1)
    len_data = [ x for x, _ in len_data]
    x, y = list(zip(*len_data))
    plt.scatter(x,y)
    plt.xlabel('Manual (Ground Truth)')
    plt.ylabel('Automatic (Whisper)')

    p = -25
    b = 8
    plt.plot([0, 150], [b,  (p-b) / p * 150 + b], color='red')
    plt.plot([0, 150], [-p / (p-b) * b ,  p / (p-b) * 150 - p / (p-b) * b], color='red')
    plt.tight_layout()
    plt.show()


def plot_alignments(no_rep, rep, labels) :
    n = len(no_rep)
    n_no_rep = sum(no_rep[0])
    n_rep = sum(rep[0])
    
    series = [
        { 'word': tuple( x[0] for x in no_rep), 'hesitation': tuple( x[1] for x in no_rep), 'silence': tuple( x[2] for x in no_rep) },
        { 'word': tuple( x[0] for x in rep), 'hesitation': tuple( x[1] for x in rep), 'silence': tuple( x[2] for x in rep) }
    ]

    x = np.arange(n)  # the label locations
    width = 0.2  # the width of the bars
    fig, axs= plt.subplots(2, 1, figsize=(16, 8))
    # fig.tight_layout()
    for ax, serie, title, total in zip(axs, series, ['Filled Pauses', 'Filled Pauses and Repetitions'], [n_no_rep, n_rep]) :
        for multiplier, (attribute, measurement) in enumerate(serie.items()):
            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, label=attribute)
            ax.bar_label(rects, padding=3, labels=[ round(x / total, 2) for x in measurement])

        ax.set_title(title)
        ax.set_xticks(x + width, labels)
        # ax.legend(loc='upper right', ncols=3)
        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
        ax.set_ylim( (0, int(1.05*total)) )
        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.3, hspace=0.3)
    plt.show()


def plot_wer_comparison(wers, labels) :
    fig, ax = plt.subplots()
    ax.bar(labels, wers)
    ax.set_ylim( (0, 1) )
    ax.set_title('WER')
    plt.show()


# show examples
def plot_word_positions(manual, automatic, title, start=0, default_color = 'cornflowerblue', hesitation_color = 'orange', retranscribe_color = 'tomato', border = 'black') :    
    if not automatic or not manual:
        return

    # setup
    matplotlib.rcParams["figure.figsize"] = [18, 6]        
    end = max(manual[-1]['end'], automatic[-1]['end'])
    y_offset = 0.2
    height = 0.2
    font_size = 12

    fig, ax = plt.subplots(num=title)
    ax.set_xlim((start, end))
    ax.set_ylim((0, 1))
    ax.set_xlabel('time (s)')
    plt.tick_params(left = False, right = False , labelleft = False) 
    
    # time axes
    ax.plot([start, end], [0.5 + y_offset, 0.5 + y_offset], color="red", zorder=0)
    ax.plot([start, end], [0.5 - y_offset, 0.5 - y_offset], color="red", zorder=0)
    
    # plot words
    for w in manual :
        width = w['end'] - w['start']
        c = hesitation_color if w['pause_type'] or w['is_restart'] else default_color
        ax.add_patch(Rectangle((w['start'], 0.5 + y_offset - height / 2), width, height, facecolor= c, edgecolor = border, linewidth=1))
        ax.annotate(w['word'], (w['start'] + width / 2, 0.5 + y_offset), color='black', fontsize=font_size, ha='center', va='center')

    for w in automatic :
        width = w['end'] - w['start']
        c = default_color if w['original'] else retranscribe_color
        ax.add_patch(Rectangle((w['start'], 0.5 - y_offset - height / 2), width, height, facecolor= c, edgecolor = border, linewidth=1))
        ax.annotate(w['word'], (w['start'] + width / 2, 0.5 - y_offset), color='black', fontsize=font_size, ha='center', va='center')

    ax.text(-0.01, 0.5 + y_offset, 'manual', rotation = 90, ha='center', va='center', transform=ax.get_yaxis_transform())
    ax.text(-0.01, 0.5 - y_offset, 'automatic', rotation = 90, ha='center', va='center', transform=ax.get_yaxis_transform())

    fig.tight_layout()    
    plt.show()


# go throught examples
def plot_alignment_examples(base = c.data_base / 'example') :
    files = [ f.stem[:10] for f in utils.get_dir_files(base, 'txt') if 'manual' in f.stem]
    for file in files :
        manual = utils.read_dict(base / ( file + '_manual.txt'))
        automatic = utils.read_dict(base / ( file + '_automatic.txt'))
        plot_word_positions(manual, automatic, file)