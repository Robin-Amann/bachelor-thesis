# # Speech Recognition
# import torch
# import torchaudio
# from torchaudio.utils import download_asset

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(device)

# SPEECH_FILE = download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
# bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
# model = bundle.get_model().to(device)

# waveform, sample_rate = torchaudio.load(SPEECH_FILE)
# waveform = waveform.to(device)

# if sample_rate != bundle.sample_rate:
#     waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)

# with torch.inference_mode():
#     features, _ = model.extract_features(waveform)

# with torch.inference_mode():
#     emission, _ = model(waveform)

# class GreedyCTCDecoder(torch.nn.Module):
#     def __init__(self, labels, blank=0):
#         super().__init__()
#         self.labels = labels
#         self.blank = blank

#     def forward(self, emission: torch.Tensor) -> str:
#         indices = torch.argmax(emission, dim=-1)  # [num_seq,]
#         indices = torch.unique_consecutive(indices, dim=-1)
#         indices = [i for i in indices if i != self.blank]
#         return "".join([self.labels[i] for i in indices])
    
# decoder = GreedyCTCDecoder(labels=bundle.get_labels())
# transcript = decoder(emission[0])

# print(transcript)


import torchaudio
from torchaudio.models.decoder import ctc_decoder
from torchaudio.utils import download_asset
from torchaudio.models.decoder import download_pretrained_files

# load model
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_10M
acoustic_model = bundle.get_model()
tokens = [label.lower() for label in bundle.get_labels()]

# load speech file
speech_file = download_asset("tutorial-assets/ctc-decoding/1688-142285-0007.wav")
waveform, sample_rate = torchaudio.load(speech_file)
if sample_rate != bundle.sample_rate:
    waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)

# language model
files = download_pretrained_files("librispeech-4-gram")

# decoder
LM_WEIGHT = 3.23
WORD_SCORE = -0.26

beam_search_decoder = ctc_decoder(
    lexicon=files.lexicon,
    tokens=files.tokens,
    lm=files.lm,
    nbest=3,
    beam_size=1500,
    lm_weight=LM_WEIGHT,
    word_score=WORD_SCORE,
)


emission, _ = acoustic_model(waveform)

beam_search_result = beam_search_decoder(emission)
beam_search_transcript = " ".join(beam_search_result[0][0].words).strip()
predicted_tokens = beam_search_decoder.idxs_to_tokens(beam_search_result[0][0].tokens)

print(f"Transcript: {beam_search_transcript}")

tokens_str = "".join(predicted_tokens)
transcript = " ".join(tokens_str.split("|"))


timesteps = beam_search_result[0][0].timesteps

print(predicted_tokens, len(predicted_tokens))
print(timesteps, timesteps.shape[0])
