import utils.file as utils
import tasks.transcript_alignment.preprocessing as pre
import tasks.transcript_alignment.wer_align as alignment
from progress.bar import ChargingBar
import tasks.vocabulary_extraction as vocabulary_extraction


def hesitation_translation(manual_directory, automatic_directory, alignment_directory, hesitations_file = 'code\\sample_data\\vocabulary\\hesitations.txt') :
    hesitations = utils.read_file(hesitations_file).split('\n')
    files = utils.get_directory_files(alignment_directory, 'txt')
    # word hesitation nothing commentary
    numbers = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    with ChargingBar("Collecting Vocabulary", max=len(files)) as bar:
        for file in files :
            f = str(file)[len(alignment_directory) : ]
            manual = utils.read_file(manual_directory + f).lower()
            whisper = utils.read_file(automatic_directory + f).lower()
            operations =utils.read_file(alignment_directory + f).split()

            manual, _ = pre.process(transcript=manual, patterns=["\(\(", "\)\)"])
            whisper, _ = pre.process(transcript=whisper, patterns=['\.', ',', '\?', '!'])
            manual, whisper = alignment.align(manual.split(), whisper.split(), operations)

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

    print(numbers)

def hesitations_count(directory, patterns=[], hesitations_file = 'code\\sample_data\\vocabulary\\hesitations.txt') :
    vocabulary = vocabulary_extraction.get_vocabulary(directory, patterns)
        

def vocabulary_set_statistic(dir, hes='code\\sample_data\\vocabulary\\hesitations.txt') :
    hesitations_file = dir + '\\hesitations_by_eye.txt'   
    stutter_file = dir + '\\stutter.txt'
    common_file = dir + '\\vocabulary_common.txt'
    vocabulary_file = dir + '\\vocabulary.txt'

    hesitations = utils.read_vocabulary(hesitations_file)   
    stutter = utils.read_vocabulary(stutter_file)   
    common = utils.read_vocabulary(common_file)   
    vocabulary = utils.read_vocabulary(vocabulary_file)   
    commentary = { w: c for w, c in vocabulary.items() if '[' in w }


    vocabulary_sum = sum(vocabulary.values())
    print('vocabulary:'.ljust(12), f'{len(vocabulary): 12,}', f'{vocabulary_sum: 12,}')
#    common_sum = sum(common.values())
#    print('common:     ', f'{len(common): 012,}', f'{common_sum: 012,}', f'{common_sum / vocabulary_sum * 100:.2f}', '%')
#    hesitations_sum = sum(hesitations.values())
#    print('hesitations:', f'{len(hesitations): 012,}', f'{hesitations_sum: 012,}', f'{hesitations_sum / vocabulary_sum * 100:.2f}', '%')
#    stutter_sum = sum(stutter.values())
#    print('stutter:    ', f'{len(stutter): 012,}', f'{stutter_sum: 012,}', f'{stutter_sum / vocabulary_sum * 100:.2f}', '%')
#    commentary_sum = sum(commentary.values())
#    print('commentary: ', f'{len(commentary): 012,}', f'{commentary_sum: 012,}', f'{commentary_sum / vocabulary_sum * 100:.2f}', '%')
    for x, n in zip([common, hesitations, stutter, commentary], ['common:', 'hesitations:', 'stutter:', 'commentary:']) :
        x_sum = sum(x.values())
        print(n.ljust(12), f'{len(x): 12,}', f'{x_sum: 12,}', f'{x_sum / vocabulary_sum * 100: 6.2f}', '%')
        
    print(', '.join(commentary.keys()))