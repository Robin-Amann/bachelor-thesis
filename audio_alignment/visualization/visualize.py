import matplotlib
import matplotlib.pyplot as plt

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