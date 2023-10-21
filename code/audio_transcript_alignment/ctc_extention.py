import torch
from . import ctc_base as base
from .ctc_base import Segment
from . import visualization as visual

SCORE_LIMIT = 3


def get_peak(trellis) :
    # needs to be changed
    height = 30 # (max - min) / 2 aber maximal 50 und minimal 20
    slope = 1.5   
    distance = 3
    probabilities = torch.clone(trellis[:, -1])
#    visual.plot_alignment_probabilities(probabilities, "")
    max_index = torch.argmax(probabilities).item()
    max_probability = probabilities[max_index].item()

    # even are valleys [::2]
    # odd are peaks [1::2]
    peaks = list(range(len(probabilities)))
    j = len(peaks) - 2
    while j >= 0 :
        if probabilities[peaks[j]] == probabilities[peaks[j+1]] :
            peaks = peaks[:j] + peaks[j+1:]
        j -= 1
    j = len(peaks) - 2
    while j > 0 :
        if probabilities[peaks[j-1]] < probabilities[peaks[j]] and probabilities[peaks[j]] < probabilities[peaks[j+1]] :
            peaks = peaks[:j] + peaks[j+1:]
        if probabilities[peaks[j-1]] > probabilities[peaks[j]] and probabilities[peaks[j]] > probabilities[peaks[j+1]] :
            peaks = peaks[:j] + peaks[j+1:]
        j -= 1
    
    if probabilities[peaks[-2]] > probabilities[peaks[-1]] :
        peaks = peaks[:-1]
    peak = []
    second = []
    for i in peaks :
        p = probabilities[i].item()
        if i == max_index :
            peak.append(i)
            continue
        if abs(i - max_index) > distance and abs( (p - max_probability) / ( i - max_index ) ) < slope :
            second.append(i)
            if p >= max_probability - height :
                peak.append(i) 
    
    if len(peak) >  1 :
        return (-1, 0)
    if len(second) == 0:
        return (max_index, float("inf"))
    return (max_index, max_probability - probabilities[max(second)].item())


def best_peak(peaks) :
    max = 0
    for i in range(len(peaks)) :
        if peaks[i][1] > peaks[max][1] :
            max = i
    if peaks[max][0] == -1 :
        return -1
    return max


def divide_emissions(emission, trellis, labels, transcript) :
    tokens = base.get_tokens(transcript, labels)
    path = base.backtrack(trellis, emission, tokens)
    segments = base.merge_repeats(path, transcript)
    words = base.merge_words(segments) 
    return emission[: path[0].time_index, :], emission[path[-1].time_index + 1 : ], words


def offset_alignment_inplace(words, offset) :
    for w in words :
        w.start += offset
        w.end += offset
    return


def alignment(labels, emission, transcript, offset) :
    if len(transcript) == 0 :
        return []
    
    if len(transcript) == 1 :
        words, score, _ = base.ctc(emission, transcript[0], labels)     # maybe if score > 4 --> mark as not properly aligned
        if score == float("inf") :
            words = [Segment(transcript[0], 0, len(emission[:, 0]), 0)]
        offset_alignment_inplace(words, offset)
        return words
    
    trellis = []
    peaks = []
    for temp_transcript in transcript :
        temp_trellis, _ = base.get_trellis(emission, temp_transcript, labels)
        temp_peak = get_peak(temp_trellis)
        trellis.append(temp_trellis)
        peaks.append(temp_peak)
    i = best_peak(peaks)
    if i < 0 :
        transcript = "|".join(transcript)
        words, score, _ = base.ctc(emission, transcript, labels)
        if score == float("inf") :
            words = [Segment(transcript, 0, len(emission[:, 0]), 0)]
        offset_alignment_inplace(words, offset)
        return words
         
    emission_one, emission_two, emission_words = divide_emissions(emission, trellis[i], labels, transcript[i])
    
    words_one = []
    if len(transcript[: i]) > 0 :
        temp_transcript = "|".join(transcript[: i])
        temp_words_one, score_one, _ = base.ctc(emission_one, temp_transcript, labels)
        if score_one <= SCORE_LIMIT :
            words_one = temp_words_one
        else :
            words_one = alignment(labels, emission_one, transcript[: i], offset)
    words_two = []
    if len(transcript[i+1:]) > 0 :
        temp_transcript = "|".join(transcript[i+1:])
        temp_words_two, score_two, _ = base.ctc(emission_two, temp_transcript, labels)
        if score_two <= SCORE_LIMIT :
            words_two = temp_words_two
            offset_alignment_inplace(words_two, offset+ emission_words[-1].end)
        else :
            words_two = alignment(labels, emission_two, transcript[i+1:], offset+ emission_words[-1].end)
    
    offset_alignment_inplace(emission_words, offset)
    return words_one + emission_words + words_two


def transform_result(ratio, words) :
    result = []
    decimals = 3
    for w in words :
        result.append( {
            "transcript": w.label, 
            "start": int(w.start * ratio), 
            "end": int(w.end * ratio), 
            "score": int(w.score * 10**decimals) / (10**decimals) 
            } )
    return result
    
def full_alignment(waveform, transcript, device) :
    # return list of transcript and indices to audio (transcript, start, end)
    labels, emission = base.get_emission(waveform, device)
    words, score, trellis_width = base.ctc(emission, transcript, labels)
    ratio = waveform[0].size(0) / trellis_width
    print(score)
    if score <= SCORE_LIMIT :
        return transform_result(ratio, words)
    
    transcript = transcript.split("|")
    words = alignment(labels, emission, transcript, 0)
    transcript = "|".join(transcript)
    return transform_result(ratio, words)


def base_ctc(waveform, transcript, device) :
    labels, emission = base.get_emission(waveform, device)
    words, _, trellis_width = base.ctc(emission, transcript, labels)
    ratio = waveform[0].size(0) / trellis_width
    return transform_result(ratio, words)