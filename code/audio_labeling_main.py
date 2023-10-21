import audio_labeling.labeling as labeling


words = [
    {'transcript': 'AND', 'start': 5760, 'end': 6720, 'score': 0.0}, 
    {'transcript': 'I', 'start': 10560, 'end': 11520, 'score': 0.967}, 
    {'transcript': 'GENERALLY', 'start': 12160, 'end': 19200, 'score': 0.83}, 
    {'transcript': 'UM', 'start': 19840, 'end': 26560, 'score': 0.749}, 
    {'transcript': 'EATING', 'start': 33920, 'end': 37760, 'score': 0.837}, 
    {'transcript': 'AT', 'start': 38080, 'end': 39040, 'score': 0.736}, 
    {'transcript': 'HOME', 'start': 39680, 'end': 41920, 'score': 0.947}
    ]
sample_rate = 16000
audio_len = 43520
labels = labeling.label(words, audio_len, sample_rate)
for label in labels :
    print(label["label"].name, 'start:', label["start"], 'end:', label["end"])

# SILENCE    start: 0     end: 5759
# SPEECH     start: 5760  end: 19200
# SILENCE    start: 19201 end: 19839
# HESITATION start: 19840 end: 26560
# SILENCE    start: 26561 end: 33919
# SPEECH     start: 33920 end: 43519
