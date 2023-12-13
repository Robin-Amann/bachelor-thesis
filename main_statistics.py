import supervised_data_preperation.statistics as stat
import hesitation_prediction.statistics as hes_stat
import utils.constants as c
import utils.file as utils


labels = ['base', 'whisper', 'wav2vec2', 'wav2vec2\nlibriSpeech LM', 'wav2vec2\nSwitchboard LM', 'wav2vec2\nsb-hesitation LM']
# stat.statistic_complete(
#     min_len=[1, 5], 
#     retranscribe_dirs=[None, c.retranscibed_dir / 'whisper', c.retranscibed_dir / 'wav2vec2', c.retranscibed_dir / 'wav2vec2_LM', c.retranscibed_dir / 'wav2vec2_custom_LM', c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations_new'], 
#     labels=labels
#     )

# hes_stat.show_alignments(c.manual_seg_dir, c.automatic_align_dir, c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations_new', n = 5)

# hes_stat.a()
no_rep = [[84286, 5625, 48722], [114138, 7999, 16494], [106551, 11576, 20506], [102337, 7745, 28551], [111298, 10887, 16446], [111877, 11413, 15341]]
rep = [[152056, 5715, 85151], [204584, 8279, 30057], [189684, 12356, 40882], [181512, 9173, 52237], [199282, 11810, 31828], [201632, 12471, 28818]]
# [0.22501259674842097, 0.41134835556515637, 0.27140468203379886, 0.26109359316670827, 0.3217505825144362, 0.34412229079948325]
stat.plot_alignments(no_rep, rep, labels)
# minimum length = 1
# total length: 128.18 hours
# percentage of
# - repetitions:                   0.10 %
# - filled pauses:                 0.11 %
# - repetitions and filled pauses: 0.01 %
# - hesitations (R or FP):         0.20 %

# minimum length = 5
# total length: 123.68 hours
# percentage of
# - repetitions:                   0.10 %
# - filled pauses:                 0.11 %
# - repetitions and filled pauses: 0.01 %
# - hesitations (R or FP):         0.20 %


## length of automatic and manual
# import utils.file as utils
# import matplotlib
# import matplotlib.pyplot as plt
# import os
# import utils.constants as c

# files = utils.dir_tuples_simple([c.manual_seg_dir, c.automatic_dir], filter=lambda f : True )
# data = [(1, 1)]
# matplotlib.rcParams["figure.figsize"] = [10, 10]
# plt.xlim((0, 150))
# plt.ylim((0, 150))
# for manual_f, automatic_F in files :
#     manual = utils.read_label_timings_from_file(manual_f)
#     automatic = utils.read_file(automatic_F).split()
#     data .append ( (len(manual), len(automatic)) )

# x, y = zip(*data)
# plt.scatter(x,y)
# plt.xlabel('Manual (Ground Truth)')
# plt.ylabel('Automatic (Whisper)')


# p = -25
# b = 8

# plt.plot([0, 150], [b,  (p-b) / p * 150 + b], color='red')
# plt.plot([0, 150], [-p / (p-b) * b ,  p / (p-b) * 150 - p / (p-b) * b], color='red')
# plt.tight_layout()
# plt.show()