import torch
import torchaudio
import pathlib
import os

def get_directory_files(directory, filetype) :
    files = [f for f in pathlib.Path(directory).glob("**\*." + filetype)]    
    return files

def read_audio(file_path, sample_rate) :
    if not os.path.isfile(file_path) :
        return []
    waveform, _ = torchaudio.load(file_path)                      
    waveform = torchaudio.functional.resample(
        orig_freq=torchaudio.info(file_path).sample_rate, 
        new_freq=sample_rate, 
        waveform=waveform)
    return waveform
    
    # with torch.inference_mode():
    #     waveform, _ = torchaudio.load(file_path)                      
    #     waveform = torchaudio.functional.resample(
    #         orig_freq=torchaudio.info(file_path).sample_rate, 
    #         new_freq=sample_rate, 
    #         waveform=waveform)
    #     # waveform = torch.sum(waveform, 0) # make to mono channel    (mean)
    #     # waveform = waveform[None, : ]
    #     return waveform
    
def write_audio(file_path, waveform, sample_rate) :
    if waveform.dim() == 1 :
        waveform = waveform[None, :]
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    torchaudio.save(file_path, waveform, sample_rate)

def read_file(path) :
    content = ""
    with open(path, "r", encoding="utf8") as file :
        content = file.read()
    return content

def write_file(path, content) :
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding='utf8') as file :
        file.write(content)


