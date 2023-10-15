import torch
import torchaudio
import os


def load_audio(file_path, sample_rate) :
    if not os.path.isfile(file_path) :
        return []
    
    with torch.inference_mode():
        waveform, _ = torchaudio.load(file_path)                      
        waveform = torchaudio.functional.resample(
            orig_freq=torchaudio.info(file_path).sample_rate, 
            new_freq=sample_rate, 
            waveform=waveform)
        waveform = torch.mean(waveform, 0) # make to mono channel
        waveform = waveform[None, : ]
        return waveform
    
    
def read_file(path) :
    content = ""
    with open(path, "r", encoding="utf8") as file :
        content = file.read()
    return content
