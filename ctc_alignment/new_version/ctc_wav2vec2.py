import torch
import torchaudio

# -- changed from original --
def get_trellis_original(emission, tokens, blank_id=0):
    num_frame = emission.size(0)
    num_tokens = len(tokens)

    # Trellis has extra diemsions for both time axis and tokens.
    # The extra dim for tokens represents <SoS> (start-of-sentence)
    # The extra dim for time axis is for simplification of the code.
    trellis = torch.empty((num_frame + 1, num_tokens + 1))
    trellis[0, 0] = 0
    trellis[1:, 0] = emission[:, 0]                                             # ignore starting audio
    trellis[0, -num_tokens:] = -float("inf")
    trellis[-num_tokens:, 0] = float("inf")

    for t in range(num_frame):
        trellis[t + 1, 1:] = torch.maximum(
            # Score for staying at the same token
            trellis[t, 1:] + emission[t, blank_id],
            # Score for changing to the next token
            trellis[t, :-1] + emission[t, tokens],
        )
    return trellis

def get_emission(SPEECH_FILE, device) :
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
    model = bundle.get_model().to(device)
    labels = bundle.get_labels()                                        
    with torch.inference_mode():
        waveform, _ = torchaudio.load(SPEECH_FILE)                      
        waveform = torchaudio.functional.resample(
            orig_freq=torchaudio.info(SPEECH_FILE).sample_rate, 
            new_freq=bundle.sample_rate, 
            waveform=waveform)
        emissions, _ = model(waveform.to(device))                       
        emissions = torch.log_softmax(emissions, dim=-1)                

    emission = emissions[0].cpu().detach()
    return labels, emission, waveform

# -- additional --
from original import ctc_wav2vec2 as ctc_original
from original import visualization as visual

def get_metadata(audio_file) :
    # Estimate the frame-wise label probability from audio waveform
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    labels, emission, waveform = get_emission(audio_file, device)
    return labels, emission, waveform

def ctc(emission, transcript, labels) :
    # Get trellis
    trellis, tokens = get_trellis(emission, transcript, labels)
    # visual.plot_trellis(trellis)
    # Find the most likely path
    if len(trellis[0, :]) >= len(trellis[:, 0]) :
        return [], float("inf") 
    path = ctc_original.backtrack(trellis, emission, tokens)
    # x = list(range(len(path)))
    # y = [trellis[p.time_index, p.token_index] for p in path]
    # plt.plot(x, y)
    # plt.legend([transcript])
    # plt.show()
    segments = ctc_original.merge_repeats(path, transcript)
    words = ctc_original.merge_words(segments)
    # Get Score
    score = - torch.max(trellis[:, -1]).item() / len(transcript)
    return words, score

def get_trellis(emission, transcript, labels) :
    tokens = ctc_original.get_tokens(transcript, labels)
    trellis = get_trellis_original(emission, tokens)
    return trellis, tokens

import matplotlib.pyplot as plt 

def get_peak(trellis, transcript) :
    # needs to be changed
    height = 30 # (max - min) / 2 aber maximal 50 und minimal 20
    slope = 1.5   
    distance = 3
    probabilities = torch.clone(trellis[:, -1])
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
    
    # print("peak ", transcript, ":", peaks)
    # plt.plot([i for i in range(len(probabilities))],probabilities)
    # plt.plot(peaks, [probabilities[i] for i in peaks])
    # plt.axhline(y = max_probability - height, color="r")
    # plt.legend([transcript])
    # plt.show()

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
    tokens = ctc_original.get_tokens(transcript, labels)
    path = ctc_original.backtrack(trellis, emission, tokens)
    segments = ctc_original.merge_repeats(path, transcript)
    words = ctc_original.merge_words(segments) 
    return emission[: path[0].time_index, :], emission[path[-1].time_index + 1 : ], words

def offset_alignment_inplace(words, offset) :
    for w in words :
        w.start += offset
        w.end += offset
    print(words)
    return

from original.ctc_wav2vec2 import Segment

def alignment(labels, emission, transcript, offset) :
    print("align:", transcript)
    if len(transcript) == 0 :
        return []
    
    if len(transcript) == 1 :
        words, score = ctc(emission, transcript[0], labels)     # maybe if score > 4 --> mark as not properly aligned
        if score == float("inf") :
            words = [Segment(transcript[0], 0, len(emission[:, 0]), 0)]
        offset_alignment_inplace(words, offset)
        return words
    
    trellis = []
    peaks = []
    for temp_transcript in transcript :
        temp_trellis, _ = get_trellis(emission, temp_transcript, labels)
        temp_peak = get_peak(temp_trellis, temp_transcript)
        trellis.append(temp_trellis)
        peaks.append(temp_peak)
    i = best_peak(peaks)
    # print(peaks)
    if i < 0 :
        transcript = "|".join(transcript)
        words, score = ctc(emission, transcript, labels)
        if score == float("inf") :
            words = [Segment(transcript, 0, len(emission[:, 0]), 0)]
        offset_alignment_inplace(words, offset)
        return words
         
    emission_one, emission_two, emission_words = divide_emissions(emission, trellis[i], labels, transcript[i])
    
    words_one = []
    if len(transcript[: i]) > 0 :
        temp_transcript = "|".join(transcript[: i])
        temp_words_one, score_one = ctc(emission_one, temp_transcript, labels)
        print(temp_transcript, score_one)
        if score_one <= 4 :
            words_one = temp_words_one
        else :
            words_one = alignment(labels, emission_one, transcript[: i], offset)
    words_two = []
    if len(transcript[i+1:]) > 0 :
        temp_transcript = "|".join(transcript[i+1:])
        temp_words_two, score_two = ctc(emission_two, temp_transcript, labels)
        print(temp_transcript, score_two)
        if score_two <= 4 :
            words_two = temp_words_two
            offset_alignment_inplace(words_two, offset+ emission_words[-1].end)
        else :
            words_two = alignment(labels, emission_two, transcript[i+1:], offset+ emission_words[-1].end)
    
    offset_alignment_inplace(emission_words, offset)
    return words_one + emission_words + words_two


def full_alignment(audio_file, transcript) :
    labels, emission, waveform = get_metadata(audio_file)
    words, score = ctc(emission, transcript, labels)
    print(score)
    if score <= 4 :
        trellis, _ = get_trellis(emission, transcript, labels)
        visual.plot_alignments(trellis, words, waveform[0])
        return words
    
    transcript = transcript.split("|")

    words = alignment(labels, emission, transcript, 0)
    transcript = "|".join(transcript)
    trellis, _ = get_trellis(emission, transcript, labels)
    visual.plot_alignments(trellis, words, waveform[0])
    return words