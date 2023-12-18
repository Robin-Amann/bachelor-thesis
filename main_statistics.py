import statistics_complete.data_gatering as data
import statistics_complete.visualization as visual
import statistics_complete.statistical_package as stat
import utils.constants as c

retranscribe_dirs = [None, c.retranscibed_dir / 'whisper', c.retranscibed_dir / 'wav2vec2', c.retranscibed_dir / 'wav2vec2_LM', c.retranscibed_dir / 'wav2vec2_custom_LM', c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations_new']
labels = ['no model', 'whisper', 'wav2vec2', 'wav2vec2\nlibriSpeech LM', 'wav2vec2\nSwitchboard LM', 'wav2vec2\nsb-hesitation LM']

# # # # data preperation # # #
# visual.plot_manual_automatic_word_lengths(c.manual_seg_dir, c.automatic_align_dir)
# visual.plot_manual_automatic_word_lengths(c.manual_seg_dir, c.automatic_v3_dir)

# # # hesitation prediction # # #
# stat.plot_alignment_examples(c.manual_seg_dir, [(c.automatic_align_dir, c.retranscibed_dir / 'whisper'), (c.automatic_v3_dir, None)], ['manual', 'whisper + whisper', 'whisper v3'], c.audio_dir, n = 2)
visual.plot_alignment_examples(['manual', 'whisper\nwhisper', 'whisper v3'])
# # # # general # # #
# stat.statistic_dataset_complete(min_len=[1, 5])
# stat.plot_hesitation_transcription_comparison(retranscribe_dirs, labels)
# stat.plot_wer_comparison(retranscribe_dirs, labels)


# no_rep = [[84286, 5625, 48722], [114138, 7999, 16494], [106551, 11576, 20506], [102337, 7745, 28551], [111298, 10887, 16446], [111877, 11413, 15341]]
# rep = [[152056, 5715, 85151], [204584, 8279, 30057], [189684, 12356, 40882], [181512, 9173, 52237], [199282, 11810, 31828], [201632, 12471, 28818]]
# wers = [0.22501259674842097, 0.41134835556515637, 0.27140468203379886, 0.26109359316670827, 0.3217505825144362, 0.34412229079948325]

# no_rep = [[17551, 1112, 4576], [17861, 1940, 3437], [15970, 1154, 6113], [17427, 1598, 4214], [17342, 1925, 3971]]
# rep = [[31136, 1156, 8578], [31913, 2078, 6878], [28308, 1360, 11200], [30887, 1735, 8248], [30918, 2277, 7673]]
# wers = [0.22501348290367815, 0.339073597844722, 0.27140428132357963, 0.3389603517750908, 0.33952660683875163, 0.33989085122596263]

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

# import matplotlib.pyplot as plt

# alignments0 = data.transcript_alignment(c.manual_seg_dir, c.automatic_align_dir, hesitation_radius=0, min_len=5)
# alignments1 = data.transcript_alignment(c.manual_seg_dir, c.automatic_v3_dir, hesitation_radius=0, min_len=5)


# fig, axs = plt.subplots(1, 1, figsize=(8, 8))
# axs.hist(alignments0, bins=100)
# axs.hist(alignments1, bins=100)
# # axs[0].hist(alignments0, bins=100)
# # axs[0].set_title('ctc') 

# # axs[1].hist(alignments1, bins=100)
# # axs[1].set_title('whisper')

# plt.show()