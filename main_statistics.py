import supervised_data_preperation.statistics as stat

stat.print_full_statistics(min_len=[5, 10])



# controversial_files                   2484    
# manual                                2230    
# manual segmented                      39321   new ignore files
# automatic segmented                   0       
# audio whisper aligned                 43418   old ignore files
# automatic segmented retranscribed     36837   no controversial files and new ignore files
# manual automatic aligned              43418   old ignore files


import utils.file as utils
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import utils.constants as c
import tasks.transcript_alignment as align
import tasks.transcript_cleanup as cleanup
from tasks.hesitation_predition import MIN_GAP


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
        ax.annotate(w['word'] + ('\n' + str(w['score'])) if w['original'] else '', (w['start'] + width / 2, y_automatic), color='black', fontsize=font_size, ha='center', va='center')

    plt.show()
    

files = [ f for f in utils.get_directory_files(c.hesitation_dir, 'txt') if not 'Speech' in f.stem ]
files = [ (f, utils.repath(f, c.hesitation_dir, c.audio_automatic_align_dir), utils.repath(f, c.hesitation_dir, c.manual_seg_dir)) for f in files ]

alignments = []
for retranscribed_f, automatic_f, manual_f in files[:50] :
    manual = utils.read_label_timings_from_file(manual_f)
    automatic = [ w | {'original' : True} for w in utils.read_words_from_file(automatic_f) ]
    retranscribed = utils.read_file(retranscribed_f)
    
    ### bring automatic and retranscribed together
    # align
    _, auto = cleanup.process(' '.join([w['word'] for w in automatic]))
    _, re = cleanup.process(retranscribed)
    auto, re = align.full_align(auto.split(), re.split())

    # get indices of gaps
    spots = list(zip([ i for i, (sec, first) in enumerate(zip(auto + ['placeholder'], ['placeholder'] + auto)) if (not sec) and first], [ i for i, (sec, first) in enumerate(zip(auto + ['placeholder'], ['placeholder'] + auto)) if sec and (not first)]))
    additional_words = [{ 'word' : ' '.join(re[s:e]), 'original' : False } for s, e in spots]
    for s, e in spots[::-1] :
        auto[s : e] = ['']

    # merge    
    complete = [ {'word' : 'start', 'original' : True, 'end' : 0} ]
    for w in auto :
        complete.append( automatic.pop(0) if w else additional_words.pop(0))
    complete.append( {'word' : 'start', 'original' : True, 'start' : manual[-1]['end']} )
    complete = [ w if w['original'] or i == 0 or i == len(complete)-1 else w | { 'start' : complete[i-1]['end'], 'end' : complete[i+1]['start'] } for i, w in enumerate(complete)]
    
    # insert large gaps with no transcript
    for i in reversed(range(1, len(complete))) :
        if complete[i]['start'] - complete[i-1]['end'] > 0.1 :
            complete.insert(i, { 'word' : '', 'original' : False, 'start' : complete[i-1]['end'], 'end' : complete[i]['start']})
    complete = complete[1 : -1]
    alignments.append( (manual, complete) )


for manual, complete in alignments[:10] :
    plot_alignments(manual, complete)