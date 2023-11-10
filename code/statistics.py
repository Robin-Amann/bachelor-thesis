import utils.statistics as stats
import utils.constants as constants


# vocabulary statistic
# stats.vocabulary_set_statistic(constants.vocabulary_manual_dir)
# stats.vocabulary_set_statistic(constants.vocabulary_manual_000_dir)
# stats.vocabulary_set_statistic(constants.vocabulary_whisper_000_dir)

# vocabulary:           63,529   21,944,978
# common:                5,269   21,428,213  97.65 %
# hesitations:              99      833,575   3.80 %
# interruptions:         6,752      153,172   0.70 %
# commentary:               15      559,618   2.55 %
# [laughter], [noise], [sigh], [mn], [lipsmack], [cough], [laugh], [breath], [pause], [[skip]], [mn]-, [sigh]-, s[laughter], [laughter]-, [sneeze]
# [laughter], [noise], [sigh], [lipsmack], [cough], [laugh], [breath], [pause], [[skip]], [sigh]-,  [laughter]-, [sneeze] --> '' 
#                                                                                                                    [mn] --> 'mn'
#                                                                                                                  [mn]-, --> 'mn-'
#                                                                                                            s[laughter], --> 's'

# vocabulary:            7,057      174,554
# common:                  219      134,801  77.23 %
# hesitations:              30        6,636   3.80 %
# interruptions:           359        1,059   0.61 %
# commentary:               10        1,880   1.08 %
# [laughter], [mn], [noise], [laugh], [breath], [cough], [sigh], [lipsmack], [[skip]], [sneeze]
# [laughter], [noise], [laugh], [breath], [cough], [sigh], [lipsmack], [[skip]], [sneeze] --> ''
#                                                                                    [mn] --> 'mn'

# vocabulary:            7,425      162,113
# common:                  219      123,986  76.48 %
# hesitations:              49        2,808   1.73 %
# interruptions:            12           12   0.01 %
# commentary:                0            0   0.00 %



# hesitation statistic
# stats.hesitation_translation(constants.segmented_transcript_dir, constants.whisper_dir, constants.transcript_alignment_dir)
#       w   h+i      n  c
# [152074,  139, 12292, 0]
# [  1499, 2431,  3632, 0]
# [  5367,  188,     0, 0]
# [   418,   63,  1399, 0]

# Conclusion:
# 4.5 % of the transcript are hesitations
# 20 % are beeing transcribed as words
# 32 % are beeing transcribed as hesitations and
# 48 % are not beeing transcribed

manual_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Transcripts_Segmented"
automatic_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Whisper_Segmented"
alignment_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Transcript_Alignment"

stats.sb_hesitation_translation(manual_dir, automatic_dir, alignment_dir)
