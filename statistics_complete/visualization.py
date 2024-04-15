import utils.file as utils
import utils.constants as c
import utils.console as console

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle



# # #   after preprocessing    # # #


# # #   after transcription    # # #
# length of automatic and manual
def plot_manual_automatic_word_lengths(len_data) :
    fig, ax = plt.subplots(1, 1, figsize=(6, 6), tight_layout=True, num='Manual Automatic Segment Length Comparison by Word')
    p, b = -25, 8
    ax.set_xlim((0, 150))
    ax.set_ylim((0, 150))
    len_data_out = [ (x, y) for x, y in len_data if y > (p-b) / p * x + b or x > (p-b) / p * y + b ]
    len_data_in = [ p for p in len_data if not p in len_data_out ]
    x, y = list(zip(*len_data_in))
    ax.scatter(x,y)
    x, y = list(zip(*len_data_out))
    ax.scatter(x,y, color='red')
    ax.set_xlabel('Manual (Ground Truth)', fontsize=16)
    ax.set_ylabel('Automatic (Whisper)', fontsize=16)

    # plt.plot([0, 150], [b,  (p-b) / p * 150 + b], color='red')
    # plt.plot([0, 150], [-p / (p-b) * b ,  p / (p-b) * 150 - p / (p-b) * b], color='red')
    plt.show()

from matplotlib.lines import Line2D
# # #     after alignment      # # #
def plot_ctc_default_probability_comparison(around_dists, full_dists, labels, all_data) :
    print('# CTC default probability comparison around untranscribed speech')
    for dist, label in zip(around_dists, labels) :
        print('#', label + ':', console.format_number(sum(dist) / len(dist), 4))
#    visual.plot_ctc_comparison(dists, labels)
    print()
    print('# CTC default probability comparison')
    for dist, label in zip(full_dists, labels) :
        print('#', label + ':', console.format_number(sum(dist) / len(dist), 4))

    for speech_t, speech_u, disf_u in all_data :
        for i in reversed(range(len(speech_t[0]) -1 )) :
            speech_t[0][i] += speech_t[0][i+1]
            speech_u[0][i] += speech_u[0][i+1]
            disf_u[0][i] += disf_u[0][i+1]
    print(all_data)

    plt.figure(figsize=(6, 6), tight_layout=True)
    handles = []
    line = Line2D([0,1],[0,1],linestyle='solid', color='black')
    line1 = Line2D([0,1],[0,1],linestyle='dotted', color='black')
    line2 = Line2D([0,1],[0,1],linestyle='dashdot', color='black')
    for (speech_t, speech_u, _), color in zip(all_data, ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'cyan']) :
        plt.plot([ i / 10 for i in range(1, 11)], speech_u[0], color=color, linestyle='solid')
        plt.plot([ i / 10 for i in range(1, 11)], speech_t[0], color=color, linestyle='dotted')
        handles.append(Line2D([0,1],[0,1],ls='', marker='o', color=color))
    plt.axhline(y=all_data[0][1][1], color='black', linestyle='dashdot')
    plt.legend(handles + [line, line1, line2], c.custom_ctc_labels + ['untranscribed words', 'transcribe words', 'total \nuntranscribed words'])
    plt.xlabel('minimum length for gap in sec.', fontsize=16)
    plt.ylabel('words reachable', fontsize=16)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(6, 6), tight_layout=True)
    handles = []
    line2 = Line2D([0,1],[0,1],linestyle='dashdot', color='black')
    for (_, _, disf_u), color in zip(all_data, ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'cyan']) :
        plt.plot([ j / 10 for j in range(1, 11)], disf_u[0])
        handles.append(Line2D([0,1],[0,1],ls='', marker='o', color=color))
    plt.axhline(y=all_data[0][2][1], color='black', linestyle='dashdot')
    plt.legend(handles + [line], c.custom_ctc_labels + ['total untranscribed \ndisfluencies'])
    plt.xlabel('minimum length for gap in sec.', fontsize=16)
    plt.ylabel('untranscribed disfluencies reachable', fontsize=16)
    plt.tight_layout()
    plt.show()


def plot_ctc_comparison(dists, labels) :
    fig, ax= plt.subplots(1, 1, figsize=(8, 8), tight_layout=True, num='ctc comparison')
    ax.hist(dists, bins=100, label=labels)
    ax.legend(loc='best')
    plt.show()


def show_hesitation_gaps(all_data, model) :
    tables = []
    print('# percentage of')
    print('# transcribed speech reachable, gaps containing transcribed speech, untranscribed speech reachable, gaps containing untranscribed speech, untranscribed hesitations reachable, gaps containing untranscribed hesitaions')
    print('# for', model)
    for data_containing, data_reachable, total in all_data :
        # sum up over gaps to get total
        for i in reversed(range(9)) :
            for j in range(3) :
                for k in range(2) :
                    data_containing[i][j][k] += data_containing[i+1][j][k]        
                data_reachable[i][j] += data_reachable[i+1][j]

        tables.append([
                ['len', 'part', '50', 'total']] + [
                [ (i+1)/10 ] + [ to_5d(data_reachable[i][j] / total * 100) for j in range(3) ] for i in range(10)
            ])
        tables.append([
                ['len', 'part', '50', 'total']] + [
                [ (i+1)/10 ] + [ to_5d(data_containing[i][j][0] / ( data_containing[i][j][0] + data_containing[i][j][1]) * 100) for j in range(3) ] for i in range(10)
            ])

    console.print_tables(tables)
    print('# data 50 speech')
    data_containing, data_reachable, total = all_data[1]
    print('# containing =', [ x[1][0] / (x[1][0] + x[1][1]) for x in data_containing ])
    print('# reachable =', [ x[1] / total for x in data_reachable ])


def plot_methods_reachable_comparison(gap_sizes, all_data, labels) :
    plt.figure(figsize=(6, 6), tight_layout=True)
    handles = []
    line = Line2D([0,1],[0,1],linestyle='solid', color='black')     # untranscribed speech
    line1 = Line2D([0,1],[0,1],linestyle='dotted', color='black')   # transcribed speech
    line2 = Line2D([0,1],[0,1],linestyle='dashdot', color='black')  # total untranscribed
    print(all_data[0])
    for ((transcribed, t_total), (untranscribed, ut_total)), color in zip(all_data, ['blue', 'orange', 'green']) :
        plt.plot(gap_sizes, untranscribed, color=color, linestyle='solid')
        plt.plot(gap_sizes, transcribed, color=color, linestyle='dotted')
        handles.append(Line2D([0,1],[0,1],ls='', marker='o', color=color))
    plt.axhline(y=all_data[0][1][1], color='black', linestyle='dashdot')
    plt.legend(handles + [line, line1, line2], labels + ['untranscribed words', 'transcribed words', 'total untranscribed words'])
    plt.xlabel('minimum length for gap in sec.', fontsize=16)
    plt.ylabel('speech reachable', fontsize=16)
    plt.show()


def plot_alignment_metric(all_data, labels) :
    fig, axs = plt.subplots(2, 3, figsize=(18, 12), tight_layout=True, num='alignment metric comparison')

    hists = [[[],[],[]],[[],[],[]]]
    for all_position, all_length, radius_psition, radius_length in all_data :
        hists[0][0].append(all_position)
        hists[0][1].append(all_length)
        hists[0][2].append([ a * b for a, b in zip(all_position, all_length)])
        hists[1][0].append(radius_psition)
        hists[1][1].append(radius_length)
        hists[1][2].append([ a * b for a, b in zip(radius_psition, radius_length)])

    table_all = []
    table_all.append(['all'] + labels)
    for i, label in enumerate(['position', 'length', 'position and length']) :
        table_all.append([label] + [ console.format_number(sum(d) / len(d), 4) for d in hists[0][i] ])
    
    table_around = []
    table_around.append(['around untranscribed'] + labels)
    for i, label in enumerate(['position', 'length', 'position and length']) :
        table_around.append([label] + [ console.format_number(sum(d) / len(d), 4) for d in hists[1][i] ])
    
    console.print_tables([table_all, table_around])

    for j, t1 in enumerate(['all: ', 'around untranscribed: ']) :
        for i, t2 in enumerate(['position', 'length', 'position and length']) :
            axs[j][i].hist(hists[j][i], bins=50, label=labels)
            axs[j][i].legend(loc='best')
            axs[j][i].title.set_text(t1 + t2)
    plt.show()


# # # after gap classification # # #


# # #  after retranscription   # # #
def final_statistics(labels, min_lens, wer_data_base, disf_data_base, wer_data, disf_data) :
    # for label, wer_lens, disf_lens in zip(labels, wer_data, disf_data) : 
    #     table = [[label, 'insert', 'delete', 'replace', 'nothing', 'all', 'WER', 'disf. trans.', 'disf. untrans.', 'disf. trans. %']]
    #     table.append(
    #         [ 'base' ] + 
    #         [ console.format_number(x) for x in wer_data_base ] + 
    #         [ console.format_number( sum(wer_data_base) ), console.format_number( sum(wer_data_base[:3]) / sum(wer_data_base), 4 ) ] + 
    #         [ console.format_number(x) for x in disf_data_base ] +
    #         [ console.format_number( disf_data_base[0] / sum(disf_data_base), 4)]
    #     )
    #     for min_len, wer, disf in zip(min_lens, wer_lens, disf_lens) :
    #         table.append(
    #             [ min_len ] + 
    #             [ console.format_number(x-y, force_sign=True) for x, y in zip(wer, wer_data_base) ] + 
    #             [ console.format_number( sum(wer) - sum(wer_data_base), force_sign=True), console.format_number( sum(wer[:3])  / sum(wer), 4 ) ] + 
    #             [ console.format_number(x-y, force_sign=True) for x, y in zip(disf, disf_data_base) ] +
    #             [ console.format_number( disf[0] / sum(disf), 4)]
    #         )
    #     console.print_table(table)
    #     print()

    #show insertions vs deletions
    plt.figure(figsize=(6, 6), tight_layout=True)
    handles = []
    line = Line2D([0,1],[0,1],linestyle='solid', color='black')     # untranscribed speech
    line1 = Line2D([0,1],[0,1],linestyle='dotted', color='black')   # transcribed speech
    line2 = Line2D([0,1],[0,1],linestyle='dashdot', color='black')  # total untranscribed
    for wer_dir, color in zip(wer_data, ['b', 'g', 'r', 'm', 'y']) :
        insert = [ (x[0] - wer_data_base[0]) for x in wer_dir ]
        delete = [ -(x[1] - wer_data_base[1]) for x in wer_dir ]
        plt.plot(min_lens, insert, color=color)
        plt.plot(min_lens, delete, color=color, linestyle='dotted')
        handles.append(Line2D([0,1],[0,1],ls='', marker='o', color=color))
    plt.axhline(y=wer_data_base[1], color='black', linestyle='dashdot')
    plt.legend(handles + [line, line1, line2], labels + ['double transcribed words', 'retranscribed words', 'total untranscribed words'])
    plt.xlabel('minimum length for gap in sec.', fontsize=16)
    plt.ylabel('words retranscribed', fontsize=16)
    plt.show()


    plt.figure(figsize=(6, 6), tight_layout=True)
    handles = []
    line1 = Line2D([0,1],[0,1],linestyle='dotted', color='black')  # total untranscribed
    line2 = Line2D([0,1],[0,1],linestyle='dashdot', color='black')  # total untranscribed
    base_trans = disf_data_base[0] # all untranscribed disf
    for disf_dir, color in zip(disf_data, ['b', 'g', 'r', 'm', 'y']) :
        disfluencies = [ trans for trans, untrans in disf_dir ]
        plt.plot(min_lens, disfluencies, color=color)        
        handles.append(Line2D([0,1],[0,1],ls='', marker='o', color=color))
    plt.axhline(y=sum(disf_data_base), color='black', linestyle='dotted')
    plt.axhline(y=base_trans, color='black', linestyle='dashdot')
    plt.legend(handles + [line1, line2], labels + ['disfluencies total', 'already transcribed disfluencies'])
    plt.xlabel('minimum length for gap in sec.', fontsize=16)
    plt.ylabel('transcribed disfluencies', fontsize=16)
    plt.ylim(bottom=0)
    plt.show()


# # #         general          # # #
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



# deprecated but might be usefull later
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


import decimal

def to_5d(x) :
    x = decimal.Decimal(x).quantize(decimal.Decimal('0.00'))
    x = str(x).rjust(5)
    return x


def show_success_rate(success_rate) :
    width = 10
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


def show_hesitation_gaps_and_success_rate(number_of_hesitations, data_containing, data_reachable, success_rate) :
    show_hesitation_gaps(number_of_hesitations, data_containing, data_reachable)
    show_success_rate(success_rate)    



