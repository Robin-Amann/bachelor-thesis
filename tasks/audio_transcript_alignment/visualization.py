import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

width = 12.0
height = 4.0

def plot_framewise_label_probability(emission) :
    matplotlib.rcParams["figure.figsize"] = [width, height / 2]
    plt.figure()
    plt.title("Frame-wise class probability")
    plt.xlabel("Time")
    plt.ylabel("Labels")

    ax = plt.gca()
    image = plt.imshow(emission.T)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1%", pad=0.1)
    plt.colorbar(image, cax=cax)

    plt.tight_layout()   
    plt.show()


def plot_trellis(trellis) :
    matplotlib.rcParams["figure.figsize"] = [width, height]
    plt.figure()
    ax = plt.gca()
    image = plt.imshow(trellis[:, :].T, origin="lower")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1%", pad=0.1)
    plt.colorbar(image, cax=cax)
    plt.annotate("- Inf", (trellis.size(1) / 5, trellis.size(1) / 1.5))

    plt.tight_layout()   
    plt.show()


def plot_trellis_with_path(trellis, path):
#     matplotlib.rcParams["figure.figsize"] = [width, height]
#     # To plot trellis with path, we take advantage of 'nan' value
#     trellis_with_path = trellis.clone()
#     for _, p in enumerate(path):
#         trellis_with_path[p.time_index, p.token_index] = float("nan")
#     plt.imshow(trellis_with_path[ : , : ].T, origin="lower")
# #    plt.title("The path found by backtracking")
#     plt.tight_layout()
#     plt.show()

    matplotlib.rcParams["figure.figsize"] = [width, height]
    plt.figure()
    ax = plt.gca()
    trellis_with_path = trellis.clone()
    for _, p in enumerate(path):
        trellis_with_path[p.time_index, p.token_index] = float("nan")
    image = plt.imshow(trellis_with_path[:, :].T, origin="lower")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1%", pad=0.1)
    plt.colorbar(image, cax=cax)
    plt.annotate("- Inf", (trellis.size(1) / 5, trellis.size(1) / 1.5))

    plt.tight_layout()   
    plt.show()



def plot_alignments(trellis, word_segments, waveform, sample_rate):
    fig, ax = plt.subplots(tight_layout=True, figsize=(width, height))
    ratio = waveform.size(0) / (trellis.size(0) - 1)
    ax.plot(waveform)
    for word in word_segments:
        x0 = ratio * word.start
        x1 = ratio * word.end
        ax.axvspan(x0, x1, alpha=0.1, color="red")
#        plt.annotate(f"{word.score:.2f}", (x0, 0.8))
        ax.annotate(word.label, (x0, 0.9))
    
    ax.set_xticks([])
    secax = ax.secondary_xaxis('bottom', functions=(lambda x : x / sample_rate, lambda x : x * sample_rate))
    secax.set_xlabel('time [second]')

    ax.set_yticks([])
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlim(0, waveform.size(-1))
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
