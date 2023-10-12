import torch
import torchaudio
import ctc_wav2vec2 as ctc

# Preparation
torch.random.manual_seed(0)                                     # results are reproducable


SPEECH_FILE = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript = "I|HAD|THAT|CURIOSITY|AT|THIS|MOMENT"

# Example 10 sec
SPEECH_FILE = "ctc_alignment\\data\\10\\10s.wav"
# transcript = "THEY|MIGHT|CANCEL|MY|INSURANCE|WELL|I|THINK|THAT'S|A|DISTINCT|POSSIBILITY|ALTHOUGH|AH|AH|SOME|TIME|AGO|GEICO|AH"    # Hand
transcript = "THEY|MIGHT|CANCEL|MY|INSURANCE|WELL|I|THINK|THAT'S|THE|BEST|THING|POSSIBILITY|ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"     # Machine

words = ctc.full_alignment(SPEECH_FILE, transcript)
