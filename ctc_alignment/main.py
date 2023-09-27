import torch
import torchaudio
import ctc_wav2vec2 as ctc
import visualization as visual

# Preparation
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.random.manual_seed(0)                             # results are reproducable
SPEECH_FILE = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript = "I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT"

# Estimate the frame-wise label probability from audio waveform
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H    # Wav2Vec2 model
model = bundle.get_model().to(device)
labels = bundle.get_labels()                            # len = 29
with torch.inference_mode():
    waveform, _ = torchaudio.load(SPEECH_FILE)          # tensor( [ [...] ] )
    emissions, _ = model(waveform.to(device))           # tensor( [ [...], ..., [...] ] )   --> [1, 169, 29]
    emissions = torch.log_softmax(emissions, dim=-1)    # normalize for numerical stability 

emission = emissions[0].cpu().detach()                  # tensor( [ [...] ] )               --> [169, 29] (timeframes x labels)

# visual.plot_framewise_label_probability(labels, emission)

# Generate the trellis matrix
tokens = ctc.get_tokens(transcript, labels)             # label indices over transcript : [7, 1, ..., 2, 6, 3] 
trellis = ctc.generate_alignment_probability(tokens, emission)                            # --> [170, 46] (timeframes+1 x transcript+1)

# visual.plot_trellis(trellis)

# Find the most likely path
path = ctc.backtrack(trellis, emission, tokens)
segments = ctc.merge_repeats(path, transcript)          # [ [char, propability], ...]
word_segments = ctc.merge_words(segments)               # [ [word, propability, start, end], ...]

# visual.plot_trellis_with_path(trellis, path)
# visual.plot_trellis_with_segments(trellis, segments, transcript, path)
# visual.plot_alignments(trellis, segments, word_segments, waveform[0], bundle)
