import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import utils.file as utils
import utils.constants as c
import statistics_complete.data_gatering as data

# length of automatic and manual
def plot_manual_automatic_word_lengths(manual_dir, automatic_dir, filter_condition, hesitation_dir=None) :
    matplotlib.rcParams["figure.figsize"] = [10, 10]
    p = -25
    b = 8
    plt.xlim((0, 150))
    plt.ylim((0, 150))
    len_data, _ = data.segment_length(manual_dir, automatic_dir, hesitation_dir, 1, filter_condition=filter_condition)
    len_data = [ x for x, _ in len_data]
    len_data_out = [ (x, y) for x, y in len_data if y > (p-b) / p * x + b or x > (p-b) / p * y + b ]
    len_data_in = [ p for p in len_data if not p in len_data_out ]
    x, y = list(zip(*len_data_in))
    plt.scatter(x,y)
    x, y = list(zip(*len_data_out))
    plt.scatter(x,y, color='red')
    plt.xlabel('Manual (Ground Truth)')
    plt.ylabel('Automatic (Whisper)')

    # plt.plot([0, 150], [b,  (p-b) / p * 150 + b], color='red')
    # plt.plot([0, 150], [-p / (p-b) * b ,  p / (p-b) * 150 - p / (p-b) * b], color='red')
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
def plot_word_positions(transcripts : list[list[dict]], title, labels, start=0, default_color = 'cornflowerblue', hesitation_color = 'orange', retranscribe_color = 'tomato', border = 'black') :    
    # setup
    matplotlib.rcParams["figure.figsize"] = [18, 6]        
    end = max( transcript[-1]['end'] for transcript in transcripts if transcript )
 
    font_size = 12
    n = len(transcripts) + 1
    y_offsets = [ x / n for x in range(1, n) ]
    height = min( y_offsets[0] * 0.75, 0.2)
 
    fig, ax = plt.subplots(num=title)
    ax.set_xlim((start, end))
    ax.set_ylim((0, 1))
    ax.set_xlabel('time (s)')
    plt.tick_params(left = False, right = False , labelleft = False) 

    # time axes
    for y_offset in y_offsets :
        ax.plot([start, end], [y_offset, y_offset], color="red", zorder=0)
    
    # plot words
    for transcrpt, y_offset, label in zip(transcripts, reversed(y_offsets), labels) :
        for w in transcrpt :
            width = w['end'] - w['start']
            if 'pause_type' in w : c = hesitation_color if w['pause_type'] or w['is_restart'] else default_color
            if 'original' in w : c = default_color if w['original'] else retranscribe_color
            ax.add_patch(Rectangle((w['start'], y_offset - height / 2), width, height, facecolor= c, edgecolor = border, linewidth=1))
            ax.text(w['start'] + width / 2, y_offset, w['word'], color='black', fontsize=font_size, ha='center', va='center', clip_on=True)
        ax.text(-0.01, y_offset, label, rotation = 90, ha='center', va='center', transform=ax.get_yaxis_transform())

    fig.tight_layout()
    plt.show()


# go throught examples
def plot_alignment_examples(labels, base = c.data_base / 'examples') :
    all_files = utils.get_dir_files(base, 'txt')
    for title in set( [ f.stem[:10] for f in all_files ] ) :
        manual = utils.read_dict( next ( f for f in all_files if (title + '_manual') in f.stem ) )
        automatic_files = [ f for f in all_files if (title + '_automatic') in f.stem ]
        automatic_files.sort()
        transcripts = [ manual ] + [ utils.read_dict(f) for f in automatic_files ]
        plot_word_positions(transcripts, title, labels)


def plot_gaps(hes_gaps, hes_gaps_not_trans) :
    fig, axs = plt.subplots(1, 1, figsize=(8, 8), tight_layout=True)
    axs.hist(hes_gaps, bins=100, label='all hesitation gaps')
    axs.hist(hes_gaps_not_trans, bins=100, label='not translated hesitation gaps')
    axs.legend(loc='upper right')
    plt.show()



import decimal

def to_5d(x) :
    x = decimal.Decimal(x).quantize(decimal.Decimal('0.00'))
    x = str(x).rjust(5)
    return x

def show_hesitation_gaps_and_success_rate(number_of_hesitations, data_containing, data_reachable, success_rate=None) :
    # sum up over gaps to get total
    for i in reversed(range(9)) :
        for j in range(3) :
            for k in range(2) :
                data_containing[i][j][k] += data_containing[i+1][j][k]        
            data_reachable[i][j] += data_reachable[i+1][j]

    width = 10
    print('# percentage of hesitations reachable:')
    print('# len'.ljust(width), 'part'.ljust(width), '50'.ljust(width), 'total'.ljust(width), sep='')
    for i in range(10) :
        print(('# ' + str((i+1)/10)).ljust(width), sep='', end='')
        for j in range(3) :
            x = data_reachable[i][j] / number_of_hesitations * 100
            print( to_5d(x).ljust(width), sep='', end='')
        print()
    print()

    print('# percentage of gaps containing hesitations:')
    print('# len'.ljust(width), 'part'.ljust(width), '50'.ljust(width), 'total'.ljust(width), sep='')
    for i in range(10) :
        print(('# ' + str((i+1)/10)).ljust(width), sep='', end='')
        for j in range(3) :
            x = data_containing[i][j][0] / ( data_containing[i][j][0] + data_containing[i][j][1]) * 100
            print( to_5d(x).ljust(width), sep='', end='')
        print()
    print()

    if not success_rate :
        return
    
    print('# success rate')
    print('# type'.ljust(width), 'part'.ljust(width), '50'.ljust(width), 'total'.ljust(width), sep='')
    for label, x in zip(['TP', 'FP', 'TN', 'FN'], success_rate) :
        print(('# ' + label).ljust(width), end='')
        for i in range(3) :
            print( str(x[i]).rjust(5).ljust(width) , end='')
        print()
    print()

    print('# hesitation prediction')
    print('# metric'.ljust(14), 'part'.ljust(width), '50'.ljust(width), 'total'.ljust(width), sep='')
    print('# accuracy'.ljust(14), end='')
    for i in range(3) :
        x = ( success_rate[0][i] + success_rate[2][i] ) / ( success_rate[0][i] + success_rate[1][i] + success_rate[2][i] + success_rate[3][i] )
        print( to_5d(x).ljust(width), end='')
    print()
    print('# precision'.ljust(14), end='')
    for i in range(3) :
        x = ( success_rate[0][i]) / ( success_rate[0][i] + success_rate[1][i])
        print( to_5d(x).ljust(width), end='')
    print()
    print('# recall'.ljust(14), end='')
    for i in range(3) :
        x = ( success_rate[0][i]) / ( success_rate[0][i] + success_rate[3][i] )
        print( to_5d(x).ljust(width), end='')
    print()
    print('# f-score'.ljust(14), end='')
    for i in range(3) :
        x = ( 2* success_rate[0][i] ) / ( 2* success_rate[0][i] + success_rate[1][i] + success_rate[3][i] )
        print( to_5d(x).ljust(width), end='')


def plot_alignment_metric(all_data) :
    fig, axs = plt.subplots(2, 3, figsize=(18, 12), tight_layout=True)

    for j, row in enumerate(all_data) :
        for dist, label in zip(row, ['wav2vec2 ctc', 'wav2vec2 custom ctc', 'whisper-large cross attention']) :
            for i, d in enumerate([dist[0], dist[1], [ a * b for a, b in zip(dist[0], dist[1])]]) :
                axs[j][i].hist(d, bins=100, label=label) 

    for j, t1 in enumerate(['all: ', 'around hesitations: ']) :
        for i, t2 in enumerate(['position', 'length', 'position and length']) :
            axs[j][i].legend(loc='upper left')
            axs[j][i].title.set_text(t1 + t2)
    plt.show()


def plot_ctc_comparison(dists, labels) :
    fig, ax= plt.subplots(1, 1, figsize=(8, 8), tight_layout=True, num='ctc comparison')
    ax.hist(dists, bins=100, label=labels)
    ax.legend(loc='best')
    plt.show()
