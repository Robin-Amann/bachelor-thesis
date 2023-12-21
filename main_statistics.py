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
# visual.plot_alignment_examples(['manual', 'whisper\nwhisper', 'whisper v3'])
# # # # general # # #
# stat.statistic_dataset_complete(min_len=[1, 5])
# stat.plot_hesitation_transcription_comparison(retranscribe_dirs, labels)
# stat.plot_wer_comparison(retranscribe_dirs, labels)
stat.alignment_comparison([c.data_base / 'automatic' / 'aligned', c.data_base / 'automatic' / 'version3', c.data_base / 'automatic' / 'aligned_new'], ['ctc old', 'whisper v3', 'ctc new'], -1)

# success_rate, result = data.hesitation_gaps(c.manual_seg_dir, c.automatic_align_dir, c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations_new' )
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


total_hesitations = 54968
success_rate = [[33027, 29276, 27940], 
                [33913, 37664, 39000]] 
# partial       49.34 %
# partial 50    43.73 %
# total         41.74 %

result = [
    [
        [[21020, 9335, 6627], 
         [30757, 12134, 8482], 
         [30219, 41904, 44612]], 
         [28101, 12093, 8482]], 
    [
        [[17209, 8550, 6448], 
         [25771, 11317, 8296], 
         [19126, 27785, 29887]], 
         [24235, 11284, 8296]], 
    [
        [[14733, 7550, 5961], 
         [22187, 10162, 7778], 
         [14913, 22096, 23685]], 
         [21126, 10136, 7778]], 
    [
        [[12519, 6482, 5236], 
         [18835, 8809, 6934], 
         [11837, 17874, 19120]], 
         [18114, 8790, 6934]], 
    [
        [[10634, 5682, 4672], 
         [16099, 7782, 6250], 
         [9514, 14466, 15476]], 
         [15590, 7770, 6250]], 
    [
        [[8989, 4965, 4143], 
         [13731, 6872, 5614], 
         [7514, 11538, 12360]], 
         [13354, 6865, 5614]], 
    [
        [[7527, 4332, 3650], 
         [11612, 6035, 4977], 
         [5962, 9157, 9839]], 
         [11340, 6030, 4977]], 
    [
        [[6230, 3761, 3216], 
         [9766, 5304, 4436], 
         [4787, 7256, 7801]], 
         [9575, 5301, 4436]], 
    [
        [[5141, 3222, 2801], 
         [8208, 4597, 3905], 
         [3867, 5786, 6207]], 
         [8068, 4595, 3905]], 
    [
        [[4252, 2724, 2394], 
         [6878, 3954, 3393], 
         [3134, 4662, 4992]], 
         [6776, 3954, 3393]]
]