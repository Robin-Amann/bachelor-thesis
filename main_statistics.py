import statistics_complete.data_gatering as data
import statistics_complete.visualization as visual
import statistics_complete.statistical_package as stat
import utils.constants as c

retranscribe_dirs = [c.retranscibed_dir / 'whisper_large', c.retranscibed_dir / 'wav2vec2', c.retranscibed_dir / 'wav2vec2_LM', c.retranscibed_dir / 'wav2vec2_custom_LM', c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations']
labels = ['whisper', 'wav2vec2', 'wav2vec2\nlibriSpeech LM', 'wav2vec2\nSwitchboard LM', 'wav2vec2\nsb-hesitation LM']
# # #   after preprocessing    # # #
# stat.dataset_statistic(min_len=[1, 5])

# # #   after transcription    # # #
# stat.manual_automatic_segment_length_by_word_comparison()
# stat.percentage_not_transcribed_speech()
# stat.wer_per_segment(min_lens=[1, 5])
# stat.gaps_containing_speech_manual_time_distribution()

# # #     after alignment      # # #
# stat.gaps_containing_speech_automatic_time_distribution()
# stat.ctc_default_probability_comparison([ c.automatic_align_dir / str(i) for i in range(1, 11) ], [ 'c = ' + str(-i) for i in range(1, 11) ])
# stat.alignment_method_comparison([c.automatic_v3_dir, c.automatic_align_dir / '0', c.automatic_align_dir / '10'], ['whisper-large cross attention', 'wav2vec2 ctc', 'wav2vec2 custom ctc (c = -10)'])
# stat.best_case_scenario(min_lens=[0.1, 0.2, 0.5, 1])

# # # # after gap classification # # #
# stat.classification_model_statistics()
# stat.not_transcribed_speech_labelling_statistics()

# # # #  after retranscription   # # #
# stat.retranscription_models_comparison(retranscribe_dirs, labels)

# # # #         general          # # #
# stat.alignment_visualisation([(c.automatic_align_dir / '0', c.retranscibed_dir / 'wav2vec2', 'automatic ctc'), (c.automatic_v3_dir, None, 'automatic\ncross attention')], 5)
# visual.plot_alignment_examples( ['manual', 'automatic ctc', 'automatic\ncross attention' ] )


### Results ###

# no_rep = [[84286, 5625, 48722], [114138, 7999, 16494], [106551, 11576, 20506], [102337, 7745, 28551], [111298, 10887, 16446], [111877, 11413, 15341]]
# rep = [[152056, 5715, 85151], [204584, 8279, 30057], [189684, 12356, 40882], [181512, 9173, 52237], [199282, 11810, 31828], [201632, 12471, 28818]]
# wers = [0.22501259674842097, 0.41134835556515637, 0.27140468203379886, 0.26109359316670827, 0.3217505825144362, 0.34412229079948325]

# no_rep = [[17551, 1112, 4576], [17861, 1940, 3437], [15970, 1154, 6113], [17427, 1598, 4214], [17342, 1925, 3971]]
# rep = [[31136, 1156, 8578], [31913, 2078, 6878], [28308, 1360, 11200], [30887, 1735, 8248], [30918, 2277, 7673]]
# wers = [0.22501348290367815, 0.339073597844722, 0.27140428132357963, 0.3389603517750908, 0.33952660683875163, 0.33989085122596263]


# cross attention alignment
# percentage of hesitations reachable:
# len     part      50        total
# 0.1      7.93      3.24      1.17
# 0.2      5.60      2.80      1.09
# 0.3      4.46      2.38      1.00
# 0.4      3.70      2.00      0.90
# 0.5      3.13      1.72      0.81
# 0.6      2.55      1.46      0.72
# 0.7      2.09      1.24      0.65
# 0.8      1.72      1.05      0.57
# 0.9      1.37      0.87      0.48
# 1.0      1.10      0.72      0.42

# percentage of gaps containing hesitations:
# len     part      50        total
# 0.1     21.25      8.89      3.14
# 0.2     20.23     10.38      4.01
# 0.3     20.50     11.16      4.67
# 0.4     21.26     11.68      5.21
# 0.5     21.99     12.27      5.71
# 0.6     22.69     13.20      6.45
# 0.7     23.06     13.96      7.16
# 0.8     23.05     14.34      7.71
# 0.9     22.38     14.37      7.94
# 1.0     21.27     14.21      8.20


# minimum length = 1
# total length: 132.47 hours
# percentage of
# - repetitions:                   0.10 %
# - filled pauses:                 0.11 %
# - repetitions and filled pauses: 0.01 %
# - hesitations (R or FP):         0.20 %

# minimum length = 5
# total length: 126.44 hours
# percentage of
# - repetitions:                   0.10 %
# - filled pauses:                 0.11 %
# - repetitions and filled pauses: 0.01 %
# - hesitations (R or FP):         0.20 %


# percentage of hesitations reachable:
# (percentage of hesitations total. Therefore 35% should be maximum)
# len     part      50        total
# 0.1     55.29     22.04     15.43
# 0.2     46.45     20.56     15.09
# 0.3     40.02     18.47     14.15
# 0.4     33.97     16.01     12.61
# 0.5     29.04     14.16     11.37
# 0.6     24.74     12.5      10.21
# 0.7     20.9      10.98      9.05
# 0.8     17.56      9.65      8.07
# 0.9     14.74      8.36      7.1
# 1.0     12.33      7.19      6.17

# percentage of gaps containing hesitations:
# len     part      50        total
# 0.1     41.02     18.22     12.93
# 0.2     47.36     23.53     17.75
# 0.3     49.7      25.47     20.11
# 0.4     51.4      26.61     21.5
# 0.5     52.78     28.19     23.18
# 0.6     54.47     30.09     25.1
# 0.7     55.8      32.12     27.06
# 0.8     56.55     34.14     29.19
# 0.9     57.07     35.77     31.09
# 1.0     57.54     36.87     32.4

# success rate
# type    part      50        total
# TP      18571     10143      7861
# FP       6255      1578       632
# TN      14456     19133     20079
# FN      27658     36086     38368

# hesitation prediction
# metric      part      50        total
# accuracy    0.49      0.44      0.42
# precision   0.75      0.87      0.93
# recall      0.4       0.22      0.17
# f-score     0.52      0.35      0.29
# --> often predicts words where there are none

# accuracy    ( TP + TN ) / ( TP + TN + FP + FN ) 
# precision   ( TP ) / ( TP + FP )
# recall      ( TP ) / ( TP + FN )
# f-score     ( 2 * precision * recall ) / (precision + recall ) = ( 2 * TP ) / ( 2 * TP + FP + FN )




