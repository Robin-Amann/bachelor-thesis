import statistics_complete.data_gatering as data
import statistics_complete.visualization as visual
import statistics_complete.statistical_package as stat
import utils.constants as c

retranscribe_dir = c.retranscibed_dir / 'custom ctc'
retranscribe_dirs = [ retranscribe_dir / 'whisper_large', retranscribe_dir / 'wav2vec2', retranscribe_dir / 'wav2vec2_LM', retranscribe_dir / 'wav2vec2_custom_LM', retranscribe_dir / 'wav2vec2_custom_LM_hesitations']
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
# stat.alignment_method_co mparison([c.automatic_v3_dir, c.automatic_align_dir / '0', c.automatic_align_dir / '1'], ['cross attention', 'ctc', 'ctc (c = -1)'])
# stat.best_case_scenario(min_lens=[0.1, 0.2, 0.5, 1])

# # # after gap classification # # #
# stat.classification_model_statistics()
stat.not_transcribed_speech_labelling_statistics()

# # #  after retranscription   # # #
# stat.retranscription_models_comparison(retranscribe_dirs, labels)

# # #         general          # # #
# stat.alignment_visualisation([(c.automatic_align_dir / '0', c.retranscibed_dir / 'wav2vec2', 'automatic ctc'), (c.automatic_align_dir / '1', None, 'automatic ctc'), (c.automatic_align_dir / '10', None, 'automatic ctc')], 10)
# visual.plot_alignment_examples( ['manual', 'automatic ctc', 'automatic\ncross attention' ] )





### Results ###

# no_rep = [[84286, 5625, 48722], [114138, 7999, 16494], [106551, 11576, 20506], [102337, 7745, 28551], [111298, 10887, 16446], [111877, 11413, 15341]]
# rep = [[152056, 5715, 85151], [204584, 8279, 30057], [189684, 12356, 40882], [181512, 9173, 52237], [199282, 11810, 31828], [201632, 12471, 28818]]
# wers = [0.22501259674842097, 0.41134835556515637, 0.27140468203379886, 0.26109359316670827, 0.3217505825144362, 0.34412229079948325]

# no_rep = [[17551, 1112, 4576], [17861, 1940, 3437], [15970, 1154, 6113], [17427, 1598, 4214], [17342, 1925, 3971]]
# rep = [[31136, 1156, 8578], [31913, 2078, 6878], [28308, 1360, 11200], [30887, 1735, 8248], [30918, 2277, 7673]]
# wers = [0.22501348290367815, 0.339073597844722, 0.27140428132357963, 0.3389603517750908, 0.33952660683875163, 0.33989085122596263]

# accuracy    ( TP + TN ) / ( TP + TN + FP + FN ) 
# precision   ( TP ) / ( TP + FP )
# recall      ( TP ) / ( TP + FN )
# f-score     ( 2 * precision * recall ) / (precision + recall ) = ( 2 * TP ) / ( 2 * TP + FP + FN )




