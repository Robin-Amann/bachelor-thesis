import matplotlib
import matplotlib.pyplot as plt

width = 12.0
height = 4.8

def plot_framewise_label_probability(emission) :
    matplotlib.rcParams["figure.figsize"] = [width, height]
    plt.imshow(emission.T)
    plt.colorbar()
    plt.title("Frame-wise class probability")
    plt.xlabel("Time")
    plt.ylabel("Labels")
    plt.show()


def plot_trellis(trellis) :
    matplotlib.rcParams["figure.figsize"] = [width, height]
    plt.imshow(trellis[1:, 1:].T, origin="lower")
    plt.annotate("- Inf", (trellis.size(1) / 5, trellis.size(1) / 1.5))
    plt.colorbar()
    plt.show()


def plot_trellis_with_path(trellis, path):
    matplotlib.rcParams["figure.figsize"] = [width, height]
    # To plot trellis with path, we take advantage of 'nan' value
    trellis_with_path = trellis.clone()
    for _, p in enumerate(path):
        trellis_with_path[p.time_index, p.token_index] = float("nan")
    plt.imshow(trellis_with_path[1:, 1:].T, origin="lower")
    plt.title("The path found by backtracking")
    plt.show()
    

def plot_trellis_with_segments(trellis, segments, transcript, path):
    matplotlib.rcParams["figure.figsize"] = [width, height]
    # To plot trellis with path, we take advantage of 'nan' value
    trellis_with_path = trellis.clone()
    for i, seg in enumerate(segments):
        if seg.label != "|":
            trellis_with_path[seg.start + 1 : seg.end + 1, i + 1] = float("nan")

    fig, [ax1, ax2] = plt.subplots(2, 1, figsize=(16, 9.5))
    ax1.set_title("Path, label and probability for each label")
    ax1.imshow(trellis_with_path.T, origin="lower")
    ax1.set_xticks([])

    for i, seg in enumerate(segments):
        if seg.label != "|":
            ax1.annotate(seg.label, (seg.start + 0.7, i + 0.3), weight="bold")
            ax1.annotate(f"{seg.score:.2f}", (seg.start - 0.3, i + 4.3))

    ax2.set_title("Label probability with and without repetation")
    xs, hs, ws = [], [], []
    for seg in segments:
        if seg.label != "|":
            xs.append((seg.end + seg.start) / 2 + 0.4)
            hs.append(seg.score)
            ws.append(seg.end - seg.start)
            ax2.annotate(seg.label, (seg.start + 0.8, -0.07), weight="bold")
    ax2.bar(xs, hs, width=ws, color="gray", alpha=0.5, edgecolor="black")

    xs, hs = [], []
    for p in path:
        label = transcript[p.token_index]
        if label != "|":
            xs.append(p.time_index + 1)
            hs.append(p.score)

    ax2.bar(xs, hs, width=0.5, alpha=0.5)
    ax2.axhline(0, color="black")
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim(-0.1, 1.1)
    plt.tight_layout()
    plt.show()


def plot_alignments(trellis, word_segments, waveform):
    matplotlib.rcParams["figure.figsize"] = [width, height]
    ratio = waveform.size(0) / (trellis.size(0) - 1)
    plt.plot(waveform)
    for word in word_segments:
        x0 = ratio * word.start
        x1 = ratio * word.end
        plt.axvspan(x0, x1, alpha=0.1, color="red")
#        plt.annotate(f"{word.score:.2f}", (x0, 0.8))
        plt.annotate(word.label, (x0, 0.9))
    plt.xlabel("time [second]")
    plt.yticks([])
    plt.ylim(-1.0, 1.0)
    plt.xlim(0, waveform.size(-1))
   # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    plt.show()
    

def plot_trellis_path_probabilities(trellis, path, legend = "") :
    matplotlib.rcParams["figure.figsize"] = [width, height]
    x = list(range(len(path)))
    y = [trellis[p.time_index, p.token_index] for p in path]
    plt.plot(x, y)
    plt.legend([legend])
    plt.show()

def plot_alignment_probabilities(probabilities, legend) :
    plt.plot([i for i in range(len(probabilities))],probabilities)
    plt.legend([legend])
    plt.show()


def plot_speech_activation(wav, speech_timestamps, sample_rate) :
    matplotlib.rcParams["figure.figsize"] = [12, 4.8]
    plt.plot(wav)
    for timestamp in speech_timestamps:
        x1, x0 = timestamp.values()
        plt.axvspan(x0, x1, alpha=0.1, color="red")     # add vertical rectangle
    plt.xlabel("time [second]")
    plt.xlim(0, wav.size(-1))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    sec = int(len(wav)/sample_rate)
    plt.xticks([sample_rate * i for i in range(sec+1)], list(range(sec+1)))
    plt.show()