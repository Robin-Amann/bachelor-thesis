import utils.file as utils
import tasks.transcript_alignment.preprocessing as pre
import tasks.transcript_alignment.wer_align as alignment
from progress.bar import ChargingBar
import tasks.vocabulary_extraction as vocabulary_extraction
import utils.constants as constants


def hesitation_translation(manual_directory, automatic_directory, alignment_directory, hesitations_file = constants.hesitations) :
    hesitations = list( utils.read_vocabulary(hesitations_file).keys() )
    files = utils.get_directory_files(alignment_directory, 'txt')
    # word hesitation nothing commentary
    numbers = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    with ChargingBar("Aligning Transcripts", max=len(files)) as bar:
        for file in files :
            f = str(file)[len(alignment_directory) : ]
            manual = utils.read_file(manual_directory + f).lower()
            whisper = utils.read_file(automatic_directory + f).lower()
            operations =utils.read_file(alignment_directory + f).split()
            x1 = manual
            y1 = whisper
            manual, _ = pre.process(transcript=manual, patterns=["\(\(", "\)\)"])
            whisper, _ = pre.process(transcript=whisper, patterns=['\.', ',', '\?', '!'])
            x2 = manual
            y2 = whisper
            manual, whisper = alignment.align(manual.split(), whisper.split(), operations)
            if len(manual) != len(whisper) :
                print()
                print(operations)
                print(x1, '|', y1)
                print(x2, '|', y2)
                print(manual, '|', whisper)
            for m, w in zip(manual, whisper) :
                if not m :
                    i = 2
                elif m in hesitations or m[0] == '-' or m[-1] == '-' :
                    i = 1
                elif m[0] == '[' :
                    i = 3
                else :
                    i = 0
                if not w :
                    j = 2
                elif w in hesitations or w[0] == '-' or w[-1] == '-' :
                    j = 1
                elif w[0] == '[' :
                    j = 3
                else :
                    j = 0
                numbers[i][j] += 1

            bar.next()

    for n in numbers :
        print(n)
        

def vocabulary_set_statistic(dir, hes='code\\sample_data\\vocabulary\\hesitations.txt') :
    hesitations_file = dir + '\\hesitations.txt'   
    stutter_file = dir + '\\interruptions.txt'
    common_file = dir + '\\vocabulary_common.txt'
    vocabulary_file = dir + '\\vocabulary.txt'

    all_hesitations = utils.read_vocabulary(constants.hesitations).keys()
    hesitations = {w: c for w, c in utils.read_vocabulary(hesitations_file).items() if w in all_hesitations}
    stutter = utils.read_vocabulary(stutter_file)   
    common = utils.read_vocabulary(common_file)   
    vocabulary = utils.read_vocabulary(vocabulary_file)   
    commentary = { w: c for w, c in vocabulary.items() if '[' in w }


    vocabulary_sum = sum(vocabulary.values())
    print('vocabulary:'.ljust(15), f'{len(vocabulary): 12,}', f'{vocabulary_sum: 12,}')
    for x, n in zip([common, hesitations, stutter, commentary], ['common:', 'hesitations:', 'interruptions:', 'commentary:']) :
        x_sum = sum(x.values())
        print(n.ljust(15), f'{len(x): 12,}', f'{x_sum: 12,}', f'{x_sum / vocabulary_sum * 100: 6.2f}', '%')
        
    print(', '.join(commentary.keys()))