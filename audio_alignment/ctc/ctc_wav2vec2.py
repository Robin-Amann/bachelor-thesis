import torch
import torchaudio
from dataclasses import dataclass

@dataclass
class Point:
    token_index: int
    time_index: int
    score: float

def backtrack(trellis, emission, tokens, blank_id=0):
    # Note:
    # j and t are indices for trellis, which has extra dimensions for time and tokens at the beginning.
    # When referring to time frame index `T` in trellis, the corresponding index in emission is `T-1`.
    # Similarly, when referring to token index `J` in trellis, the corresponding index in transcript is `J-1`.
    j = trellis.size(1) - 1
    t_start = torch.argmax(trellis[:, j]).item()

    path = []
    for t in range(t_start, 0, -1):
        # 1. Figure out if the current position was stay or change
        # Note (again):
        # `emission[J-1]` is the emission at time frame `J` of trellis dimension.
        # Score for token staying the same from time frame J-1 to T.
        stayed = trellis[t - 1, j] + emission[t - 1, blank_id]
        # Score for token changing from C-1 at T-1 to J at T.
        changed = trellis[t - 1, j - 1] + emission[t - 1, tokens[j - 1]]

        # 2. Store the path with frame-wise probability.
        prob = emission[t - 1, tokens[j - 1] if changed > stayed else 0].exp().item()
        # Return token index and time index in non-trellis coordinate.
        path.append(Point(j - 1, t - 1, prob))

        # 3. Update the token
        if changed > stayed:
            j -= 1
            if j == 0:
                break
    else:
        raise ValueError("Failed to align")
    return path[::-1]   # in reverse order


@dataclass
class Segment:
    label: str
    start: int
    end: int
    score: float

    def __repr__(self):
        return f"{self.label}\t({self.score:4.2f}): [{self.start:5d}, {self.end:5d})"

    @property
    def length(self):
        return self.end - self.start


def merge_repeats(path, transcript):
    i1, i2 = 0, 0
    segments = []
    while i1 < len(path):
        while i2 < len(path) and path[i1].token_index == path[i2].token_index:
            i2 += 1
        score = sum(path[k].score for k in range(i1, i2)) / (i2 - i1) # score is average
        segments.append(
            Segment(
                transcript[path[i1].token_index],
                path[i1].time_index,
                path[i2 - 1].time_index + 1,
                score,
            )
        )
        i1 = i2
    return segments


def merge_words(segments, separator="|"):
    words = []
    i1, i2 = 0, 0
    while i1 < len(segments):
        if i2 >= len(segments) or segments[i2].label == separator:
            if i1 != i2:
                segs = segments[i1:i2]
                word = "".join([seg.label for seg in segs])
                score = sum(seg.score * seg.length for seg in segs) / sum(seg.length for seg in segs)  # score is average
                words.append(Segment(word, segments[i1].start, segments[i2 - 1].end, score))
            i1 = i2 + 1
            i2 = i1
        else:
            i2 += 1
    return words


def get_tokens(transcript, labels) :
    dictionary = {c: i for i, c in enumerate(labels)}
    tokens = [dictionary[c] for c in transcript]
    return tokens


def get_trellis(emission, transcript, labels, blank_id=0) :
    tokens = get_tokens(transcript, labels)
    num_frame = emission.size(0)
    num_tokens = len(tokens)

    # Trellis has extra diemsions for both time axis and tokens.
    # The extra dim for tokens represents <SoS> (start-of-sentence)
    # The extra dim for time axis is for simplification of the code.
    trellis = torch.empty((num_frame + 1, num_tokens + 1))
    trellis[0, 0] = 0
    trellis[1:, 0] = emission[:, 0]           # ignore starting audio
    trellis[0, -num_tokens:] = -float("inf")
    trellis[-num_tokens:, 0] = float("inf")

    for t in range(num_frame):
        trellis[t + 1, 1:] = torch.maximum(
            # Score for staying at the same token
            trellis[t, 1:] + emission[t, blank_id],
            # Score for changing to the next token
            trellis[t, :-1] + emission[t, tokens],
        )
    return trellis, tokens


def ctc(emission, transcript, labels) :
    trellis, tokens = get_trellis(emission, transcript, labels)
    # Find the most likely path
    if len(trellis[0, :]) >= len(trellis[:, 0]) :
        return [], float("inf") 
    path = backtrack(trellis, emission, tokens)
    segments = merge_repeats(path, transcript)
    words = merge_words(segments)
    score = - torch.max(trellis[:, -1]).item() / len(transcript)
    return words, score


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
    tokens = get_tokens(transcript, labels)
    path = backtrack(trellis, emission, tokens)
    segments = merge_repeats(path, transcript)
    words = merge_words(segments) 
    return emission[: path[0].time_index, :], emission[path[-1].time_index + 1 : ], words

def offset_alignment_inplace(words, offset) :
    for w in words :
        w.start += offset
        w.end += offset
    print(words)
    return


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


def get_emission(waveform, device) :
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
    model = bundle.get_model().to(device)
    labels = bundle.get_labels()                                        
    with torch.inference_mode():
        emissions, _ = model(waveform.to(device))                       
        emissions = torch.log_softmax(emissions, dim=-1)                
    emission = emissions[0].cpu().detach()
    return labels, emission, waveform


def full_alignment(waveform, transcript, device) :
    # return list of transcript and indices to audio (transcript, start, end)

    labels, emission, waveform = get_emission(waveform, device)
    words, score = ctc(emission, transcript, labels)
    print(score)
    if score <= 4 :
        return words
    
    transcript = transcript.split("|")

    words = alignment(labels, emission, transcript, 0)
    transcript = "|".join(transcript)
    return words