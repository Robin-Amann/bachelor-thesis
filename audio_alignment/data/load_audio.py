import torch
import torchaudio
import os

def load(file_path, sample_rate) :
    if not os.path.isfile(file_path) :
        return []
    
    with torch.inference_mode():
        waveform, _ = torchaudio.load(file_path)                      
        waveform = torchaudio.functional.resample(
            orig_freq=torchaudio.info(file_path).sample_rate, 
            new_freq=sample_rate, 
            waveform=waveform)
        return waveform