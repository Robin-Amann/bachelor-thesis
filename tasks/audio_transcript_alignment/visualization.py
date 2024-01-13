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
    plt.imshow(trellis[:, :].T, origin="lower")
    plt.annotate("- Inf", (trellis.size(1) / 5, trellis.size(1) / 1.5))
    plt.colorbar()
    plt.show()


def plot_trellis_with_path(trellis, path):
    matplotlib.rcParams["figure.figsize"] = [width, height]
    # To plot trellis with path, we take advantage of 'nan' value
    trellis_with_path = trellis.clone()
    for _, p in enumerate(path):
        trellis_with_path[p.time_index, p.token_index] = float("nan")
    plt.imshow(trellis_with_path[ : , : ].T, origin="lower")
    plt.title("The path found by backtracking")
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
