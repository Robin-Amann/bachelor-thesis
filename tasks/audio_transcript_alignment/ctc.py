import torch
import torchaudio
from dataclasses import dataclass
import tasks.audio_transcript_alignment.visualization as visual
import utils.constants as constants

model_args = {'model_dir' : str(constants.model_dir / 'wav2vec2')}

def get_emission(waveform, device, wav2vec2_model=None) :
    if wav2vec2_model == None :
        bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
        model = bundle.get_model(dl_kwargs=model_args).to(device)
    else :
        bundle, model = wav2vec2_model
    labels = bundle.get_labels()                   
    with torch.inference_mode():
        emissions, _ = model(waveform.to(device))   
        emissions = torch.log_softmax(emissions, dim=-1)
    emission = emissions[0].cpu().detach()
    return labels, emission


def get_tokens(transcript, labels) :
    dictionary = {c: i for i, c in enumerate(labels)}
    tokens = [dictionary[c] for c in transcript]
    return tokens


def get_trellis(emission, transcript, labels, blank_id=0, whitespace_stay_default_value=0) :
    tokens = get_tokens(transcript, labels)
    num_frame = emission.size(0)
    num_tokens = len(tokens)

    whitespace_token = tokens[0]
    trellis = torch.zeros((num_frame, num_tokens))
    if whitespace_stay_default_value != 0 :
        trellis[1:, 0] = torch.cumsum(torch.maximum(emission[1:, blank_id], torch.Tensor( [ whitespace_stay_default_value for _ in range(num_frame-1) ] )), 0)
    else :
        trellis[1:, 0] = torch.cumsum(emission[1:, blank_id], 0)
    trellis[0, 1:] = -float("inf")
    trellis[-num_tokens + 1 :, 0] = float("inf")

    if whitespace_stay_default_value != 0 :
        mask = torch.Tensor( [ whitespace_stay_default_value if tokens[i] == whitespace_token else -float('inf') for i in range(1, len(transcript))] )
    for t in range(num_frame - 1):
        if whitespace_stay_default_value != 0 :
            stay = torch.maximum(emission[t, blank_id], mask)
        else :
            stay = emission[t, blank_id]
        trellis[t + 1, 1:] = torch.maximum(
            trellis[t, 1:] + stay, 
            trellis[t, :-1] + emission[t, tokens[1:]]
        )          
    return trellis, tokens


@dataclass
class Point:
    token_index: int
    time_index: int
    score: float


def backtrack(trellis, emission, tokens, blank_id=0, whitespace_stay_default_value=0):
    t, j = trellis.size(0) - 1, trellis.size(1) - 1
    whitespace_token = tokens[0]
    path = [Point(j, t, emission[t, blank_id].exp().item())]
        
    while j > 0:
        # Should not happen but just in case
        assert t > 0

        if whitespace_stay_default_value != 0 and tokens[j] == whitespace_token :
            p_stay = torch.tensor(max(emission[t-1, blank_id], whitespace_stay_default_value))
        else :
            p_stay = emission[t - 1, blank_id]
        p_change = emission[t - 1, tokens[j]]

        stayed = trellis[t - 1, j] + p_stay
        changed = trellis[t - 1, j - 1] + p_change
        
        t -= 1
        if changed > stayed:
            j -= 1
            
        prob = (p_change if changed > stayed else p_stay).exp().item()
        path.append(Point(j, t, prob))

    while t > 0:
        prob = emission[t - 1, blank_id].exp().item()
        path.append(Point(j, t - 1, prob))
        t -= 1

    return path[::-1]


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


# the higher the score the worse
def ctc(emission, transcript, labels, whitespace_stay_default_value=0) :
    # visual.plot_framewise_label_probability(emission)
    trellis, tokens = get_trellis(emission, transcript, labels, whitespace_stay_default_value=whitespace_stay_default_value)
    # visual.plot_trellis(trellis)
    # Find the most likely path
    if len(trellis[0, :]) >= len(trellis[:, 0]) :
        return [], trellis.size(0)
    path = backtrack(trellis, emission, tokens, whitespace_stay_default_value=whitespace_stay_default_value)
    segments = merge_repeats(path, transcript)
    words = merge_words(segments)
    visual.plot_trellis_with_path(trellis, path)
    visual.plot_trellis_path_probabilities(trellis, path)
    return words, trellis.size(0)


