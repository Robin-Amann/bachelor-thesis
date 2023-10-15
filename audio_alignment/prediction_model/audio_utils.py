THRESHOLD = 0.25 #minimum legth of audio to be considered a gap in seconds


def get_untranscribed_audio(waveform, words, speech_timestamps, sample_rate) :
    minimum_gap = THRESHOLD * sample_rate
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