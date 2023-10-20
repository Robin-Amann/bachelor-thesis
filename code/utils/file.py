import torch
import torchaudio
import os
import wave
import struct

def read_audio(file_path, sample_rate) :
    if not os.path.isfile(file_path) :
        return []
    
    with torch.inference_mode():
        waveform, _ = torchaudio.load(file_path)                      
        waveform = torchaudio.functional.resample(
            orig_freq=torchaudio.info(file_path).sample_rate, 
            new_freq=sample_rate, 
            waveform=waveform)
        # waveform = torch.sum(waveform, 0) # make to mono channel    (mean)
        # waveform = waveform[None, : ]
        return waveform
    
def write_audio(file_path, waveform, sample_rate) :
    if waveform.dim() == 1 :
        waveform = waveform[None, :]
    torchaudio.save(file_path, waveform, sample_rate)

def read_file(path) :
    content = ""
    with open(path, "r", encoding="utf8") as file :
        content = file.read()
    return content

def write_file(path, content) :
    with open(path, "w") as file :
        print(content)
        file.write(content)

