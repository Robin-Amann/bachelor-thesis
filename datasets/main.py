import torch
import torchaudio

with torch.inference_mode():
    waveform, _ = torchaudio.load("datasets\\fe_03_05851.sph")

    