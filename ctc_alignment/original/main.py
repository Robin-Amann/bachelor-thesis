import torch
import torchaudio
import ctc_wav2vec2 as ctc
import visualization as visual
import matplotlib.pyplot as plt

# Preparation
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.random.manual_seed(0)                             # results are reproducable

transcript = ""
SPEECH_FILE = ""

# Example 1
SPEECH_FILE = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript = "I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT"
# transcript = "AT|THIS|MOMENT"

# Example 10 sec
# SPEECH_FILE = "ctc_alignment\\data\\10\\10s.wav"
# transcript = "THEY|MIGHT|CANCEL|MY|INSURANCE|WELL|I|THINK|THAT'S|A|DISTINCT|POSSIBILITY|ALTHOUGH|AH|AH|SOME|TIME|AGO|GEICO|AH"    # Hand
# transcript = "THEY|MIGHT|CANCEL|MY|INSURANCE|WELL|I|THINK|THAT'S|THE|BEST|THING|POSSIBILITY|ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"     # Machine

# Example 4 sec
# SPEECH_FILE = "ctc_alignment\\data\\4\\4s.wav"
# transcript = "ALTHOUGH|AH|SOME|TIME|AGO|GEICO|AH"    # Hand
# transcript = "ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"         # Machine


# Estimate the frame-wise label probability from audio waveform
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                # Wav2Vec2 model
model = bundle.get_model().to(device)
labels = bundle.get_labels()                                        # len = 29
with torch.inference_mode():
    waveform, _ = torchaudio.load(SPEECH_FILE)                      # tensor( [ [...] ] )
    waveform = torchaudio.functional.resample(
        orig_freq=torchaudio.info(SPEECH_FILE).sample_rate, 
        new_freq=bundle.sample_rate, 
        waveform=waveform)
    emissions, _ = model(waveform.to(device))                       # tensor( [ [...], ..., [...] ] )   --> [1, 169, 29]
    emissions = torch.log_softmax(emissions, dim=-1)                # normalize for numerical stability 

emission = emissions[0].cpu().detach()                              # tensor( [ [...] ] )               --> [169, 29] (timeframes x labels)

# visual.plot_framewise_label_probability(emission[:, 1:])


# Generate the trellis matrix
tokens = ctc.get_tokens(transcript, labels)                         # label indices over transcript : [7, 1, ..., 2, 6, 3] 
trellis = ctc.get_trellis(emission, tokens)                            # --> [170, 46] (timeframes+1 x transcript+1)

visual.plot_trellis(trellis)


# Find the most likely path
path = ctc.backtrack(trellis, emission, tokens)
print(path)
y = [trellis[p.time_index, p.token_index].item() for p in path]
x = list(range(len(y)))
plt.plot(x, y)
plt.show()
segments = ctc.merge_repeats(path, transcript)                      # [ [char, propability], ...]
word_segments = ctc.merge_words(segments)                           # [ [word, propability, start, end], ...]


for word in word_segments :
    print(word.label, ":", " " * (13 - len(word.label)), f"{word.score:.2f}")


# visual.plot_trellis_with_path(trellis, path)
# visual.plot_trellis_with_segments(trellis, segments, transcript, path)
visual.plot_alignments(trellis, word_segments, waveform[0], bundle.sample_rate)
