import tasks.transcript_alignment as align
import utils.file as utils
import tasks.transcript_cleanup as cleanup 
import utils.constants as constants
    
files = [ f for f in utils.get_directory_files(constants.hesitation_dir, 'txt') if not f.stem in constants.controversial_files and not f.stem[2:6] in constants.ignore_files]
files = [ (utils.repath(f, constants.hesitation_dir, constants.manual_seg_dir), utils.repath(f, constants.hesitation_dir, constants.automatic_seg_dir), f) for f in files ]

for manual_f, automatic_f, hesitation_f in files[:100] :
    ta = ' '.join([ w['word'] for w in utils.read_label_timings_from_file(manual_f) ])
    tb = utils.read_file(automatic_f)
    tc = utils.read_file(hesitation_f)
    align.print_3_words(ta, tb, tc)

# 57 ['uhhuh', 'yeah', 'uhhuh', 'uhhuh', 'it', 'is', '', '', '', '', '', '', '', '', '', '', 'kind', '', '', '', '', '', '', '', '', '', '', '', '', '', 'of', 'expensive', 'it', 'is', '', '', '', '', '', '', '', '', '', '', '', 'of', 'course', 'the', 'chemicals', 'themselves', 'when', 'you', 'buy', 'them', "they're", 'expensive', 'too']
# 47 ['and', 'take', 'that', 'one', 'step', 'out', 'of', 'the', 'blue', 'they', 'want', 'too', 'much', 'money', 'you', 'just', 'kind', '', '', '', 'of', 'expensive', '', '', '', '', '', '', '', '', '', '', '', '', '', 'of', 'course', 'the', 'chemicals', 'themselves', 'when', 'you', 'buy', 'them', 'are', 'expensive', 'too']
# 47 ['services', 'pick', 'them', 'out', 'and', 'spray', 'for', 'weeds', 'and', 'be', 'able', 'to', 'fertilize', 'them', 'and', 'take', 'that', 'one', 'step', 'out', 'of', 'the', 'blue', 'thank', 'you', 'they', 'want', 'too', 'much', 'money', 'you', 'just', 'kind', 'of', 'expensive', 'of', 'course', 'the', 'chemicals', 'themselves', 'when', 'you', 'buy', 'them', 'are', 'expensive', 'too']