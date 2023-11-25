import matplotlib
import matplotlib.pyplot as plt
import numpy as np

width = 12.0
height = 4.8

def plot_speech_activation(wav, speech_timestamps, sample_rate) :
    matplotlib.rcParams["figure.figsize"] = [width, height]
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


def plot_words_and_speech(wav, words, speech_timestamps, sample_rate) :
    sec = int(len(wav)/sample_rate)
    
    matplotlib.rcParams["figure.figsize"] = [width, height]
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    plt.plot(wav)
    plt.xlim(0, wav.size(-1))
    y_limit = max([abs(i) for i in plt.ylim()])
    plt.ylim(-y_limit, y_limit)
    plt.xlabel("time [second]")
    plt.xticks([sample_rate * i for i in range(sec+1)], list(range(sec+1)))
    
    for timestamp in speech_timestamps:
        end, start = timestamp.values()
        plt.hlines(y=-0, xmin=start, xmax=end, colors="r")
    for i, word in enumerate(words) :
        transcript, start, end, _ = word.values()
        plt.axvspan(start, end, alpha=0.1, color="red")     # add vertical rectangle
        plt.text(x=start, y=-y_limit * (0.75 + 0.1*(i % 3)), s=transcript)
    plt.show()

def plot_gaps(wav, audio_fragments, sample_rate) :
    sec = int(len(wav)/sample_rate)
    
    matplotlib.rcParams["figure.figsize"] = [width, height]
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    plt.plot(wav)
    plt.xlim(0, wav.size(-1))
    y_limit = max([abs(i) for i in plt.ylim()])
    plt.ylim(-y_limit, y_limit)
    plt.xlabel("time [second]")
    plt.xticks([sample_rate * i for i in range(sec+1)], list(range(sec+1)))
    
    for fragment in audio_fragments:
        start, end, _, speech = fragment.values()
        plt.axvspan(start, end, alpha=0.1, color="r")     # add vertical rectangle
        for speech_fragment in speech :
            s, e = speech_fragment.values()
            plt.axvspan(start + s, start + e, alpha=0.1, color="g")     # add vertical rectangle    
    plt.show()

def plot_alignment_comparison(wav, words_list, speech_timestamps_list, legend, sample_rate) :
    sec = int(len(wav)/sample_rate)
    matplotlib.rcParams["figure.figsize"] = [2*width, len(words_list)*height]
    fig, axs = plt.subplots(len(words_list), 1)
    for ax, words, speech_timestamps, name in zip(axs, words_list, speech_timestamps_list, legend) :
        ax.plot(wav)
        ax.set_title(name)
        ax.set_xlim(0, wav.size(-1))
        y_limit = max([abs(i) for i in ax.get_ylim()])
        ax.set_ylim(-y_limit, y_limit)
        ax.set_xlabel("time [second]")
        ax.set_xticks([sample_rate * i for i in range(sec+1)], list(range(sec+1)))
        
        for timestamp in speech_timestamps:
            end, start = timestamp.values()
            ax.hlines(y=-0, xmin=start, xmax=end, colors="r")
        for i, word in enumerate(words) :
            transcript, start, end, _ = word.values()
            ax.axvspan(start, end, alpha=0.1, color="red")     # add vertical rectangle
            ax.text(x=start, y=-y_limit * (0.75 + 0.1*(i % 3)), s=transcript)
    fig.tight_layout()
    plt.show()


s = 4

def plot_hesitation_translation(with_rep, no_rep) :
    species = ("With Repetitions", "Without Repetitions")
    penguin_means = {
        'word': (with_rep[1][0], no_rep[1][0]),
        'hesitation': (with_rep[1][1], no_rep[1][1]),
        'silence': (with_rep[1][2], no_rep[1][2]),
    }

    x = np.arange(len(species))  # the label locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots(layout='constrained', figsize=(2*s, 2*s))
    fig.tight_layout()
    for multiplier, (attribute, measurement) in enumerate(penguin_means.items()):
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)

    ax.set_title('Hesitations translated as')
    ax.set_xticks(x + width, species)
    ax.legend(loc='upper right', ncols=3)
    # ax.set_ylim(0, 1)
    plt.show()


def plot_all(ax00, ax01, ax02, ax03, ax04, ax05, ax06, ax07, ax08, ax09) :
    fig, axs = plt.subplots(4, 3, figsize=(3 * s, 3 *s))
    fig.tight_layout()
    for y, row in enumerate([[ax00, ax01, ax02], [ax03, ax04, ax05], [ax06, ax07, ax08]]) :
        for x, ax  in enumerate(row) :
            axs[y][x].hist(ax[0], len(ax[0]), weights = ax[1])
            axs[y][x].set_title(ax[2])
    axs[3][0].hist(ax09[0], len(ax09[0]), weights = ax09[1])
    axs[3][0].set_title(ax09[2])

    plt.show()