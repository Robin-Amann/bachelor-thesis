import torch
import torchaudio
import ctc_wav2vec2 as ctc


# Preparation
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.random.manual_seed(0) # results are reproducable
SPEECH_FILE = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript = "I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT"

# Estimate the frame-wise label probability from audio waveform
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H    # Wav2Vec2 model
model = bundle.get_model().to(device)
labels = bundle.get_labels()
with torch.inference_mode():
    waveform, _ = torchaudio.load(SPEECH_FILE)
    emissions, _ = model(waveform.to(device))
    emissions = torch.log_softmax(emissions, dim=-1)    # normalize for numerical stability

emission = emissions[0].cpu().detach()

# Generate the trellis matrix
tokens = ctc.get_tokens(transcript, labels)
trellis = ctc.generate_alignment_probability(tokens, emission)

# Find the most likely path
path = ctc.backtrack(trellis, emission, tokens)
segments = ctc.merge_repeats(path)
word_segments = ctc.merge_words(segments)

