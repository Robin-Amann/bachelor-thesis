import utils.file as utils
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import utils.constants as c

print(len(c.controversial_files))

print('manual                               ', len(utils.get_directory_files(c.manual_dir, 'txt')))
print('manual segmented                     ', len([ f for f in utils.get_directory_files(c.manual_seg_dir, 'txt') if not 'Speech' in f.stem]))
print('automatic segmented                  ', len(utils.get_directory_files(c.automatic_seg_dir, 'txt')))
print('audio whisper aligned                ', len(utils.get_directory_files(c.audio_automatic_align_dir, 'txt')))
print('automatic segmented retranscribed    ', len(utils.get_directory_files(c.hesitation_dir, 'txt')))
print('manual automatic aligned             ', len(utils.get_directory_files(c.transcript_align_dir, 'txt')))

# def plot_alignments(manual, automatic) :    
#     if not automatic :
#         return
    
#     start = 0
#     end = max(manual[-1]['end'], automatic[-1]['end']) + 0.5
#     y_manual = 0.7
#     y_automatic = 0.3
#     height = 0.2
#     font_size = 12

#     matplotlib.rcParams["figure.figsize"] = [18, 6]

#     fig, ax = plt.subplots()
#     fig.tight_layout()
#     ax.set_xlim((start, end))
#     ax.set_ylim((0, 1))

#     ax.plot([start, end], [y_manual, y_manual], color="red", zorder=0)
#     for w in manual :
#         width = w['end'] - w['start']
#         ax.add_patch(Rectangle((w['start'], y_manual - height / 2), width, height))
#         ax.annotate(w['word'], (w['start'] + width / 2, y_manual), color='black', fontsize=font_size, ha='center', va='center')

#     ax.plot([start, end], [y_automatic, y_automatic], color="red", zorder=0)
#     for w in automatic :
#         width = w['end'] - w['start']
#         ax.add_patch(Rectangle((w['start'], y_automatic - height / 2), width, height, color= 'blue' if w['original'] else 'red'))
#         ax.annotate(w['word'], (w['start'] + width / 2, y_automatic), color='black', fontsize=font_size, ha='center', va='center')

#     plt.show()
    
# # picture gaps
# manual_f = "D:\\Robin_dataset\\Switchboard Computed\\Manual_Segmented\\20\\2008\\A\\sw2008A003.txt"
# automatic_f = "D:\\Robin_dataset\\Switchboard Computed\\Audio_Whisper_Alignment\\20\\2008\\A\\sw2008A003.txt"
# retranscribed_f = "D:\\Robin_dataset\\Switchboard Computed\\Automatic_Segmented_Retranscribed\\20\\2022\\A\\sw2022A005.txt"

# manual = utils.read_label_timings_from_file(manual_f)
# automatic = [ w | {'original' : True} for w in utils.read_words_from_file(automatic_f) ]

# plot_alignments(manual, automatic)
