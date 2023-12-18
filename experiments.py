import torch
import torchaudio
import matplotlib
from dataclasses import dataclass
import matplotlib.pyplot as plt
import utils.file as utils

matplotlib.rcParams["figure.figsize"] = [16, 8]
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# SPEECH_FILE = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
# transcript = "|I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT|"
# transcript = "|I|HAD|THAT|BESIDE|ME|MOMENT|"

waveform = utils.read_audio('D:\\Robin_dataset\\Switchboard\\LDC97S62 Switchboard-1 Release 2\\02\\SWB1\\sw02220A.wav', 16000)
waveform = waveform[:, int(49.36*16000) : int(66.36*16000) ]
transcript = "|MY|TRUCK|IS|BROKEN|YEAH|THERE|THERE'S|A|GUY|HAVE|YOU|EVER|HEARD|OF|GEORGE|MINSTON|HE|PLAYS|PIANO|I|THINK|HE'S|DEAD|NOW|BUT|HE|PLAYS|WONDERFULLY|I|LIKE|THAT|"
# 0.8425   my version
# 0.8177   tutorial
# transcript = "|MY|TRUCK|IS|BROKEN|THERE|A|GUY|HAVE|YOU|EVER|HEARD|OF|GEORGE|MINSTON|HE|PLAYS|PIANO|I|THINK|HE'S|DEAD|NOW|BUT|HE|PLAYS|WONDERFULLY|I|LIKE|THAT|"
# 0.8345   my version   -5
# 0.8437   my version   -2
# 0.8750                -1
# 0.8034    tutorial

bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model().to(device)
labels = bundle.get_labels()
with torch.inference_mode():
    # waveform, _ = torchaudio.load(SPEECH_FILE)
    emissions, _ = model(waveform.to(device))
    emissions = torch.log_softmax(emissions, dim=-1)

emission = emissions[0].cpu().detach()

dictionary = {c: i for i, c in enumerate(labels)}
tokens = [dictionary[c] for c in transcript]

def get_trellis(emission, tokens, blank_id=0):
    num_frame = emission.size(0)
    num_tokens = len(tokens)

    trellis = torch.zeros((num_frame, num_tokens))
    trellis[1:, 0] = torch.cumsum(emission[1:, blank_id], 0)
    trellis[0, 1:] = -float("inf")
    trellis[-num_tokens + 1 :, 0] = float("inf")

    blank_token = dictionary['|']
    for t in range(num_frame - 1):
        for i in range(1, len(transcript)) :
            if tokens[i] == blank_token :
                trellis[t + 1, i] = max(trellis[t, i] + max(emission[t, blank_id], -1), trellis[t, i-1] + emission[t, tokens[i]])
            else :
                trellis[t + 1, i] = max(trellis[t, i] + emission[t, blank_id], trellis[t, i-1] + emission[t, tokens[i]])
        # trellis[t + 1, 1:] = torch.maximum(
        #     # Score for staying at the same token
        #     trellis[t, 1:] + emission[t, blank_id],
        #     # Score for changing to the next token
        #     trellis[t, :-1] + emission[t, tokens[1:]],
        # )
    return trellis
trellis = get_trellis(emission, tokens)

@dataclass
class Point:
    token_index: int
    time_index: int
    score: float

def backtrack(trellis, emission, tokens, blank_id=0):
    t, j = trellis.size(0) - 1, trellis.size(1) - 1
    blank_token = dictionary['|']

    path = [Point(j, t, emission[t, blank_id].exp().item())]
    while j > 0:
        # Should not happen but just in case
        assert t > 0

        # 1. Figure out if the current position was stay or change
        # Frame-wise score of stay vs change
        if tokens[j] == blank_token :
            p_stay = torch.tensor(max(emission[t-1, blank_id], -1))
        else :
            p_stay = emission[t - 1, blank_id]
        p_change = emission[t - 1, tokens[j]]

        # Context-aware score for stay vs change
        stayed = trellis[t - 1, j] + p_stay
        changed = trellis[t - 1, j - 1] + p_change
        
        # Update position
        t -= 1
        if changed > stayed:
            j -= 1
            
        # Store the path with frame-wise probability.
        prob = (p_change if changed > stayed else p_stay).exp().item()
        path.append(Point(j, t, prob))

    # Now j == 0, which means, it reached the SoS.
    # Fill up the rest for the sake of visualization
    while t > 0:
        prob = emission[t - 1, blank_id].exp().item()
        path.append(Point(j, t - 1, prob))
        t -= 1

    return path[::-1]

path = backtrack(trellis, emission, tokens)
for i, p in enumerate(path[:70]) :
    print(i, p, trellis[p.time_index, p.token_index])

for i in reversed(range(9, 14)) :
    print(trellis[61, i], trellis[62, i], trellis[63, i], trellis[64, i], trellis[65, i])

import tasks.audio_transcript_alignment.visualization as visual
visual.plot_trellis_path_probabilities(trellis, path)

def plot_trellis_with_path(trellis, path):
    # To plot trellis with path, we take advantage of 'nan' value
    trellis_with_path = trellis.clone()
    for _, p in enumerate(path):
        trellis_with_path[p.time_index, p.token_index] = float("nan")
    plt.imshow(trellis_with_path.T, origin="lower")
    plt.title("The path found by backtracking")
    plt.tight_layout()
    plt.show()
plot_trellis_with_path(trellis, path)

# Merge the labels
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

def merge_repeats(path):
    i1, i2 = 0, 0
    segments = []
    while i1 < len(path):
        while i2 < len(path) and path[i1].token_index == path[i2].token_index:
            i2 += 1
        score = sum(path[k].score for k in range(i1, i2)) / (i2 - i1)
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

segments = merge_repeats(path)

# Merge words
def merge_words(segments, separator="|"):
    words = []
    i1, i2 = 0, 0
    while i1 < len(segments):
        if i2 >= len(segments) or segments[i2].label == separator:
            if i1 != i2:
                segs = segments[i1:i2]
                word = "".join([seg.label for seg in segs])
                score = sum(seg.score * seg.length for seg in segs) / sum(seg.length for seg in segs)
                words.append(Segment(word, segments[i1].start, segments[i2 - 1].end, score))
            i1 = i2 + 1
            i2 = i1
        else:
            i2 += 1
    return words

word_segments = merge_words(segments)

def plot_alignments(trellis, segments, word_segments, waveform, sample_rate=bundle.sample_rate):
    trellis_with_path = trellis.clone()
    for i, seg in enumerate(segments):
        if seg.label != "|":
            trellis_with_path[seg.start : seg.end, i] = float("nan")

    fig, [ax1, ax2] = plt.subplots(2, 1)

    ax1.imshow(trellis_with_path.T, origin="lower", aspect="auto")
    ax1.set_facecolor("lightgray")
    ax1.set_xticks([])
    ax1.set_yticks([])

    for word in word_segments:
        ax1.axvspan(word.start - 0.5, word.end - 0.5, edgecolor="white", facecolor="none")

    for i, seg in enumerate(segments):
        if seg.label != "|":
            ax1.annotate(seg.label, (seg.start, i - 0.7), size="small")
            ax1.annotate(f"{seg.score:.2f}", (seg.start, i + 3), size="small")

    # The original waveform
    ratio = waveform.size(0) / sample_rate / trellis.size(0)
    ax2.specgram(waveform, Fs=sample_rate)
    for word in word_segments:
        x0 = ratio * word.start
        x1 = ratio * word.end
        ax2.axvspan(x0, x1, facecolor="none", edgecolor="white", hatch="/")
        ax2.annotate(f"{word.score:.2f}", (x0, sample_rate * 0.51), annotation_clip=False)

    for seg in segments:
        if seg.label != "|":
            ax2.annotate(seg.label, (seg.start * ratio, sample_rate * 0.55), annotation_clip=False)
    ax2.set_xlabel("time [second]")
    ax2.set_yticks([])
    fig.tight_layout()
    plt.show()

plot_alignments(
    trellis,
    segments,
    word_segments,
    waveform[0],
)




word_alignments = []
ratio = waveform.size(1) / 16000 / trellis.size(0)
for word in word_segments:
    word_alignments.append({
        'word' : word.label,
        'start' : word.start * ratio,
        'end' : word.end * ratio
    })
print(word_alignments)
true_alignment = utils.read_dict('D:\\Robin_dataset\\Switchboard Computed\\manual\\segmented\\22\\2220\\A\\sw2220A003.txt')
import utils.wer_alignment as align

true_alignment, word_alignments, _ = align.align_words(true_alignment, word_alignments, insertion_obj={'word': '', 'start':-1, 'end':-1})
import utils.alignment_metric as metric

score = metric.alignment_error(true_alignment, word_alignments)
print(score)

