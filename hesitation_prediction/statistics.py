import utils.file as utils
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import random
import utils.constants as c 


def plot_alignments(manual, automatic, title, start=0, default_color = 'cornflowerblue', hesitation_color = 'orange', retranscribe_color = 'tomato', border = 'black') :    
    if not automatic or not manual:
        return

    # setup
    matplotlib.rcParams["figure.figsize"] = [18, 6]        
    end = max(manual[-1]['end'], automatic[-1]['end']) + 0.5
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


def show_alignments(manual_dir, automatic_dir, hesitation_dir, audio_dir = c.audio_dir, n=10) :
    files = utils.get_dir_tuples([ (manual_dir, None, lambda f : not 'Speech' in f.stem), automatic_dir, hesitation_dir])
    random.shuffle(files)    
    alignments = []

    segment_files = [ f for f in utils.get_dir_files(manual_dir, 'txt') if 'Speech' in f.stem ]
    audio_files = [ f for f in utils.get_dir_files(audio_dir, 'wav') if f.stem[3:8] in [ f.stem[2:7] for f in segment_files] ]

    for manual_f, automatic_f, hesitation_f in files :
        if not (os.path.isfile(automatic_f) and os.path.isfile(hesitation_f)) :
            continue
        segment = utils.read_dict( next( f for f in segment_files if manual_f.stem[2:7] in f.stem ) )[int(manual_f.stem[7:10])]
        audio = utils.read_audio( next( f for f in audio_files if manual_f.stem[2:7] in f.stem), c.sample_rate)[0]
        audio = audio[int(c.sample_rate*segment['start']) : int(c.sample_rate*segment['end'])]
        
        manual = utils.read_dict(manual_f)
        automatic = [ w | {'original' : True} for w in utils.read_dict(automatic_f) ] + [ w | {'original' : False} for w in utils.read_dict(hesitation_f) ]
        automatic = [ dict( (k, w[k]) for k in ('word', 'original', 'start', 'end')) for w in automatic ]

        automatic = sorted(automatic, key=lambda w : w['start'])
        alignments.append( (manual, automatic, manual_f.stem, audio))
        if len(alignments) >= n :
            break

    base = c.data_base / 'example'
    for manual, automatic, title, audio in alignments :
        utils.write_dict( base / (title + '_manual.txt'), manual)
        utils.write_dict( base / (title + '_automatic.txt'), automatic)
        utils.write_audio( base / (title + '_audio.wav'), audio, c.sample_rate)


import tasks.transcript_alignment as align

def a(base = c.data_base / 'example') :
    files = [ f.stem[:10] for f in utils.get_dir_files(base, 'txt') if 'manual' in f.stem]
    for file in files :
        manual = utils.read_dict(base / ( file + '_manual.txt'))
        automatic = utils.read_dict(base / ( file + '_automatic.txt'))
        plot_alignments(manual, automatic, file)
