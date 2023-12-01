import utils.file as utils
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

def plot_alignments(manual, automatic) :    
    if not automatic :
        return
    
    start = 0
    end = max(manual[-1]['end'], automatic[-1]['end']) + 0.5
    y_manual = 0.7
    y_automatic = 0.3
    height = 0.2
    font_size = 12
    my_cmap = matplotlib.colormaps['RdYlGn']

    matplotlib.rcParams["figure.figsize"] = [18, 6]

    fig, ax = plt.subplots()
    fig.tight_layout()
    ax.set_xlim((start, end))
    ax.set_ylim((0, 1))

    ax.plot([start, end], [y_manual, y_manual], color="red", zorder=0)
    for w in manual :
        width = w['end'] - w['start']
        if w['pause_type'] :
            c = 'orange'
        elif w['is_restart'] :
            c = 'yellow'
        else :
            c = 'c'
        ax.add_patch(Rectangle((w['start'], y_manual - height / 2), width, height, color= c))
        ax.annotate(w['word'], (w['start'] + width / 2, y_manual), color='black', fontsize=font_size, ha='center', va='center')

    ax.plot([start, end], [y_automatic, y_automatic], color="red", zorder=0)
    for w in automatic :
        width = w['end'] - w['start']
        ax.add_patch(Rectangle((w['start'], y_automatic - height / 2), width, height, color= my_cmap(w['score']) if w['original'] else 'red'))
        ax.annotate(w['word'] + (('\n' + str(w['score'])) if w['original'] else ''), (w['start'] + width / 2, y_automatic), color='black', fontsize=font_size, ha='center', va='center')

    plt.show()
    

def show_alignments(manual_dir, automatic_dir, hesitation_dir, n=10) :
    files = [ f for f in utils.get_directory_files(manual_dir, 'txt') if not 'Speech' in f.stem ]
    files = [ (f, utils.repath(f, manual_dir, automatic_dir), utils.repath(f, manual_dir, hesitation_dir)) for f in files ]
    alignments = []
    for manual_f, automatic_f, hesitation_f in files :
        if not (os.path.isfile(automatic_f) and os.path.isfile(hesitation_f)) :
            continue
        manual = utils.read_label_timings_from_file(manual_f)
        automatic = [ w | {'original' : True} for w in utils.read_words_from_file(automatic_f) ] + [ w | {'original' : False} for w in utils.read_complementary_words_from_file(hesitation_f) ]
        automatic = sorted(automatic, key=lambda w : w['start'])

        alignments.append( (manual, automatic))
        print(automatic_f.stem)
        if len(alignments) >= n :
            break

    for manual, automatic in alignments :
        plot_alignments(manual, automatic)

# alignments = []
# for retranscribed_f, automatic_f, manual_f in files[:50] :
#     manual = utils.read_label_timings_from_file(manual_f)
#     automatic = [ w | {'original' : True} for w in utils.read_words_from_file(automatic_f) ]
#     retranscribed = utils.read_file(retranscribed_f)
    
#     ### bring automatic and retranscribed together
#     # align
#     _, auto = cleanup.process(' '.join([w['word'] for w in automatic]))
#     _, re = cleanup.process(retranscribed)
#     auto, re = align.full_align(auto.split(), re.split())

#     # get indices of gaps
#     spots = list(zip([ i for i, (sec, first) in enumerate(zip(auto + ['placeholder'], ['placeholder'] + auto)) if (not sec) and first], [ i for i, (sec, first) in enumerate(zip(auto + ['placeholder'], ['placeholder'] + auto)) if sec and (not first)]))
#     additional_words = [{ 'word' : ' '.join(re[s:e]), 'original' : False } for s, e in spots]
#     for s, e in spots[::-1] :
#         auto[s : e] = ['']

#     # merge    
#     complete = [ {'word' : 'start', 'original' : True, 'end' : 0} ]
#     for w in auto :
#         complete.append( automatic.pop(0) if w else additional_words.pop(0))
#     complete.append( {'word' : 'start', 'original' : True, 'start' : manual[-1]['end']} )
#     complete = [ w if w['original'] or i == 0 or i == len(complete)-1 else w | { 'start' : complete[i-1]['end'], 'end' : complete[i+1]['start'] } for i, w in enumerate(complete)]
    
#     # insert large gaps with no transcript
#     for i in reversed(range(1, len(complete))) :
#         if complete[i]['start'] - complete[i-1]['end'] > 0.1 :
#             complete.insert(i, { 'word' : '', 'original' : False, 'start' : complete[i-1]['end'], 'end' : complete[i]['start']})
#     complete = complete[1 : -1]
#     alignments.append( (manual, complete) )


