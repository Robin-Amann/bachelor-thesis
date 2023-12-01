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



def get_untranscribed_audio(waveform, words, speech_timestamps, sample_rate) :
    minimum_gap = 0.25 * sample_rate
    untranscribed_audio = []
    if words[0]["start"] > 0 :
        untranscribed_audio.append({"start": 0, "end": words[0]["start"] - 1})
    for word, last_word in zip(words[1:], words[:-1]) :
        untranscribed_audio.append({"start": last_word["end"] + 1, "end": word["start"] - 1})
    if words[-1]["end"] < len(waveform[0]) :
        untranscribed_audio.append({"start": words[-1]["end"] + 1, "end": len(waveform[0]) - 1})
    
    untranscribed_audio = [audio for audio in untranscribed_audio if audio["end"] - audio["start"] > minimum_gap]
    untranscribed_speech = []
    for audio in untranscribed_audio :
        speech = [ s for s in speech_timestamps if s["start"] < audio["end"] and s["end"] > audio["start"] ]
        untranscribed_speech.append([{"start": max(s["start"], audio["start"]), "end": min(s["end"], audio["end"])} for s in speech])
    
    result = []
    for audio, speech in zip(untranscribed_audio, untranscribed_speech) :
        start = audio["start"]
        end = audio["end"]
        result.append({
            "start" : start,
            "end" : end,
            "audio" : waveform[ : , start: end + 1],
            "speech" : [{ "start" : s["start"] - start, "end" : s["end"] - start } for s in speech]
        })
    return result