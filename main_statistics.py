import supervised_data_preperation.statistics as stat
import hesitation_prediction.statistics as hes_stat
import utils.constants as c

# None, c.retranscibed_dir / 'wav2vec2', c.retranscibed_dir / 'wav2vec2_LM',
stat.print_full_statistics(min_len=[1, 5], retranscribe_dirs=[ c.retranscibed_dir / 'wav2vec2_custom_LM', c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations'])


# hes_stat.show_alignments(c.manual_seg_dir, c.automatic_align_dir, c.retranscibed_dir, n = 10)



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

# None
# 1 wer: 0.225
# 5 wer: 0.2178

# wav2vec2
# 1 wer: 0.2714
# 5 wer: 0.2594

# wav2vec2_LM
# 1 wer: 0.2611
# 5 wer: 0.251

# wav2vec2_custom_LM (20 .. 23)
# 1 wer: 0.3218
# 5 wer: 0.3072

# wav2vec2_custom_LM_hesitations

