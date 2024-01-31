# # #   after preprocessing    # # #

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


# # #   after transcription    # # #

#                                 │       total   per words   per untranscribed
#   ──────────────────────────────┼────────────────────────────────────────────
#   number of words words         │   1,214,987
#   not transcribed words         │     121,730     10.02 %                      WER --> 0.10
#   nottranscribed disfluencies   │      89,799      7.39 %             73.77 %  WER --> 0.12

# WER = 0.2097 for minimum length 1 
# - insert:      91,127
# - delete:     121,730
# - replace:     61,065
# - nothing:  1,032,192
# - all:      1,306,114

# WER = 0.2 for minimum length 5 
# - insert:      80,837
# - delete:     121,071
# - replace:     54,083
# - nothing:  1,023,776
# - all:      1,279,767


# # #     after alignment      # # #

# CTC default probability comparison
# c = -1:  0.8666
# c = -2:  0.8669
# c = -3:  0.8668
# c = -4:  0.8663
# c = -5:  0.8655
# c = -6:  0.8646
# c = -7:  0.8636
# c = -8:  0.8627
# c = -9:  0.8619
# c = -10: 0.8612

# percentage of hesitations reachable / gaps containing hesitations for whisper-large cross attention:
#   len   │    part      50   total          len   │    part      50   total
#   ──────┼────────────────────────          ──────┼────────────────────────
#   0.1   │   16.30   12.48    9.18          0.1   │   12.55    9.23    6.07
#   0.2   │   14.72   11.88    9.05          0.2   │   13.76   10.76    7.43
#   0.3   │   13.58   11.24    8.87          0.3   │   14.58   11.69    8.45
#   0.4   │   12.68   10.66    8.65          0.4   │   15.37   12.49    9.35
#   0.5   │   12.03   10.23    8.46          0.5   │   16.53   13.57   10.42
#   0.6   │   11.23    9.76    8.27          0.6   │   20.22   17.03   13.53
#   0.7   │   10.54    9.33    8.09          0.7   │   25.93   22.35   18.34
#   0.8   │    9.78    8.77    7.77          0.8   │   30.24   26.46   22.40
#   0.9   │    8.93    8.13    7.32          0.9   │   32.78   29.12   25.15
#   1.0   │    8.22    7.57    6.91          1.0   │   34.41   31.00   27.24

# percentage of hesitations reachable / gaps containing hesitations for wav2vec2 ctc:
#   len   │    part      50   total          len   │    part      50   total
#   ──────┼────────────────────────          ──────┼────────────────────────
#   0.1   │   67.01   47.54   36.47          0.1   │   19.27   13.46   10.27
#   0.2   │   62.01   46.10   36.30          0.2   │   23.90   17.66   13.95
#   0.3   │   57.17   43.64   35.43          0.3   │   25.20   19.19   15.74
#   0.4   │   52.07   40.45   33.84          0.4   │   25.72   19.97   16.96
#   0.5   │   47.28   37.21   31.80          0.5   │   27.50   21.66   18.87
#   0.6   │   41.78   34.23   29.78          0.6   │   33.96   28.22   25.08
#   0.7   │   37.24   31.23   27.64          0.7   │   39.63   33.93   30.77
#   0.8   │   33.27   28.31   25.41          0.8   │   42.58   37.15   34.26
#   0.9   │   29.45   25.34   23.02          0.9   │   44.56   39.38   36.86
#   1.0   │   26.06   22.64   20.77          1.0   │   46.12   41.28   39.01

# percentage of hesitations reachable / gaps containing hesitations for wav2vec2 custom ctc (c = -10):
#   len   │    part      50   total          len   │    part      50   total
#   ──────┼────────────────────────          ──────┼────────────────────────
#   0.1   │   70.22   50.69   39.33          0.1   │   19.27   13.60   10.43
#   0.2   │   65.11   49.18   39.15          0.2   │   24.12   17.99   14.30
#   0.3   │   60.25   46.68   38.25          0.3   │   25.49   19.58   16.15
#   0.4   │   55.07   43.41   36.57          0.4   │   26.04   20.39   17.39
#   0.5   │   50.14   40.05   34.43          0.5   │   27.77   22.05   19.29
#   0.6   │   44.63   36.97   32.31          0.6   │   34.21   28.56   25.45
#   0.7   │   40.06   33.93   30.13          0.7   │   40.01   34.38   31.23
#   0.8   │   36.01   30.92   27.82          0.8   │   43.06   37.67   34.78
#   0.9   │   32.07   27.84   25.33          0.9   │   45.14   39.99   37.46
#   1.0   │   28.54   25.03   22.98          1.0   │   46.73   41.92   39.65

# minimum gap size = 0.1                                                            deletions down and nothing or replace up
#             │     insert     delete   replace      nothing          all      WER
#   ──────────┼───────────────────────────────────────────────────────────────────
#   base      │    +91,124   +121,738   +61,057   +1,032,192   +1,306,111   0.2097
#   partial   │   +358,038    -83,416    -9,040      +92,456     +358,038   0.3242
#   50        │    +69,147    -62,806      +483      +62,323      +69,147   0.2041
#   total     │    +10,600    -44,604      -127      +44,731      +10,600   0.1821
# minimum gap size = 0.2
#             │     insert     delete   replace      nothing          all      WER
#   ──────────┼───────────────────────────────────────────────────────────────────
#   base      │    +91,124   +121,738   +61,057   +1,032,192   +1,306,111   0.2097
#   partial   │   +251,947    -75,662    -7,333      +82,995     +251,947   0.2842
#   50        │    +53,512    -59,385      +134      +59,251      +53,512   0.1972
#   total     │     +9,886    -44,210      -184      +44,394       +9,886   0.1819
# minimum gap size = 0.5
#             │     insert     delete   replace      nothing          all      WER
#   ──────────┼───────────────────────────────────────────────────────────────────
#   base      │    +91,124   +121,738   +61,057   +1,032,192   +1,306,111   0.2097
#   partial   │   +145,362    -55,415    -2,875      +58,290     +145,362   0.2487
#   50        │    +31,488    -43,388       -57      +43,445      +31,488   0.1958
#   total     │     +6,804    -35,330      -682      +36,012       +6,804   0.1864
# minimum gap size = 1
#             │    insert     delete   replace      nothing          all      WER
#   ──────────┼──────────────────────────────────────────────────────────────────
#   base      │   +91,124   +121,738   +61,057   +1,032,192   +1,306,111   0.2097
#   partial   │   +56,094    -28,935    -1,451      +30,386      +56,094   0.2200
#   50        │   +12,682    -23,319      -208      +23,527      +12,682   0.1995
#   total     │    +3,171    -20,286      -500      +20,786       +3,171   0.1958


# # # after gap classification # # #

# classificatin model metrics
#   metric      │    score
#   ────────────┼─────────
#   accuracy    │   0.7459
#   precision   │   0.8996
#   recall      │   0.6411
#   f score     │   0.7486

# labeling statistics:
# untranscribed words: 20,880
# - captured words     11,390 ( 54.55 % )
# - missed words:       9,490 ( 45.45 % )
# correct labels:      12,004 ( 60.26 % )
# incorrect labls:      7,916 ( 39.74 % )


# # #  after retranscription   # # #

#   whisper       │   empty      new   not new          wav2vec2      │    empty     new   not new          libriSpeech LM   │    empty     new   not new          Switchboard LM   │    empty     new   not new          sb-hesitation LM   │    empty     new   not new
#   ──────────────┼───────────────────────────          ──────────────┼───────────────────────────          ─────────────────┼───────────────────────────          ─────────────────┼───────────────────────────          ───────────────────┼───────────────────────────
#   empty         │       0   18,733    10,988          empty         │        0   4,744     9,263          empty            │        0   1,748     8,827          empty            │        0   6,688     9,621          empty              │        0   6,908     9,636
#   transcribed   │     427    4,634   163,196          transcribed   │      334   1,773   166,150          transcribed      │      488     834   166,935          transcribed      │      613   2,191   165,453          transcribed        │      623   2,231   165,403
#   not trans.    │   8,357    9,851     2,672          not trans.    │   11,583   7,854     1,443          not trans.       │   15,576   4,210     1,094          not trans.       │   12,151   6,947     1,782          not trans.         │   12,054   7,009     1,817

# initially untranscribed: 20,880

#                               │      WER
#   ────────────────────────────┼─────────
#   whisper                     │   0.2425
#   wav2vec2                    │   0.2049
#   wav2vec2 libriSpeech LM     │   0.2392
#   wav2vec2 Switchboard LM     │   0.2362
#   wav2vec2 sb-hesitation LM   │   0.2359


# # #         general          # # #

