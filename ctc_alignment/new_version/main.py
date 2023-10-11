import torch
from dataclasses import dataclass
import ctc_alignment.original.ctc_wav2vec2 as ctc
import ctc_alignment.new_version.ctc_wav2vec2 as ctc2

def get_emission(audio_file) :
    # Estimate the frame-wise label probability from audio waveform
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    labels, emission = ctc2.get_emission(audio_file, device)
    return labels, emission

def ctc(emission, transcript, labels) :
    # Get trellis
    trellis, tokens = get_trellis(emission, transcript, labels)
    # Find the most likely path
    path = ctc.backtrack(trellis, emission, tokens)
    segments = ctc.merge_repeats(path, transcript)
    word_segments = ctc.merge_words(segments)
    # Get Score
    score = torch.max(trellis[:, -1]) / len(transcript)
    return word_segments, score

def get_trellis(emission, transcript, labels) :
    tokens = ctc.get_tokens(transcript, labels)
    trellis = ctc2.get_trellis(emission, tokens)
    return trellis, tokens

def get_peak(trellis) :
    probabilities = trellis[:, -1]
    max_index = torch.argmax(probabilities)
    height = 50                                             # needs to be changed
    slope = 1.5
    peaks = []
    for i in range(probabilities.size(0)) :
        if probabilities[i] >= probabilities[max_index] - height:
            peaks.append(i) 
    if len(peaks) == 1 :
        return peaks

    # remove all preaks that fall under one mountain
    # i = 0
    # while i < len(peaks) :
    #     x = peaks[i]
    #     peaks = [ p for p in peaks if  p != x and abs( (probabilities[p] - probabilities[x]) / ( p - x ) ) < slope  ]
    #     i = peaks.index(x) + 1

    # remove all preaks that fall under the mountain
    peaks = [ p for p in peaks if  p != max_index and abs( (probabilities[p] - probabilities[max_index]) / ( p - max_index ) ) < slope  ]
    

    if len(peaks) == 1 :
        trimmed = [0]
        for i, p in enumerate(probabilities) :
            if i != max_index and abs( (p - probabilities[max_index]) / ( i - max_index ) ) < slope :
                trimmed.append[p]
        return (max_index, probabilities[max_index]- max(trimmed))
    else :
        return (-1, 0)




def best_peak(peaks) :
    max = 0
    for i in range(len(peaks)) :
        if peaks[i][1] > peaks[max][1] :
            max = i
    return max

def divide_emissions(emission, trellis, peaks, labels, transcript) :
    tokens = ctc.get_tokens(transcript, labels)
    path = ctc.backtrack(trellis, emission, tokens)

    return emission[: path[0].time_index, :], emission[path[-1].time_index + 1 : ]

def alignment(labels, emission, transcript) :

    if len(transcript) == 0 :
        return []
    
    if len(transcript) == 1 :
        words, _ = ctc(emission, transcript[0], labels)     # maybe if score > 4 --> mark as not properly aligned
        return words
    
    trellis = []
    peaks = []
    for temp_transcript in transcript :
        temp_trellis, _ = get_trellis(emission, temp_transcript, labels)
        temp_peak = get_peak(temp_trellis)
        trellis.append(temp_trellis)
        peaks.append(temp_peak)

    i = best_peak(peaks)

    if i < 0 :
        transcript = "|".join(transcript)
        words, _ = ctc(emission, transcript, labels)
        return words
         
    emission_one, emission_two = divide_emissions(emission, trellis[i], peaks[i], labels, transcript[i])

    words_one = alignment(labels, emission_one, transcript[: i])
    words_two = alignment(labels, emission_two, transcript[i+1:])
    
    return words_one + words_two


def full_alignment(audio_file, transcript) :
    labels, emission = get_emission(audio_file)
    words, score = ctc(emission, transcript, labels)
    if score <= 3 :
        return words
    
    transcript = transcript.split("|")

    words = alignment(labels, emission, transcript)
    return words


# Preparation
torch.random.manual_seed(0)                                     # results are reproducable
SPEECH_FILE = "ctc_alignment\\data\\10\\10s.wav"
transcript = ""

words = full_alignment(SPEECH_FILE, transcript)




# for trel in trellis :
    # visual.plot_trellis(trel)
# visual.plot_framewise_label_probability(emission[:, 1:])
# visual.plot_trellis_with_path(trellis, path)
# visual.plot_trellis_with_segments(trellis, segments, transcript, path)
# visual.plot_alignments(trellis[0], words, waveform[0])