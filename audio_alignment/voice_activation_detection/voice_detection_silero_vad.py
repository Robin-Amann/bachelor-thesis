import torch
import torchaudio

USE_ONNX = False # change this to True if you want to test onnx model

def voice_activation_detection(file_path, desired_sample_rate) :
    sampling_rate = torchaudio.info(file_path).sample_rate
    torch.set_num_threads(1)
    # load model  
    # UserWarning: You are about to download and run code from an untrusted repository. In a future release, this won't be allowed. 
    # To add the repository to your trusted list, change the command to {calling_fn}(..., trust_repo=False) and a command prompt will appear asking for an explicit confirmation of trust, or load(..., trust_repo=True), 
    # which will assume that the prompt is to be answered with 'yes'. You can also use load(..., trust_repo='check') which will only prompt for confirmation if the repo is not already trusted. This will eventually be the default behaviour
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True, onnx=USE_ONNX)
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
    wav = read_audio(file_path, sampling_rate=sampling_rate)   # tensor with timestampe

    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate)
    ratio = desired_sample_rate / torchaudio.info(file_path).sample_rate
    speech_timestamps = [{"start": int(ratio*s["start"]), "end" : int(ratio*s["end"])} for s in speech_timestamps]
    return speech_timestamps
    # return list of (start, end)


# merge all speech chunks to one audio
# save_audio('voice_activation_detection\\only_speech.wav', collect_chunks(speech_timestamps, wav), sampling_rate=SAMPLING_RATE) 
