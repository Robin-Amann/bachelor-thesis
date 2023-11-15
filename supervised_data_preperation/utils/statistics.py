import utils.file as utils
import tasks.transcript_cleanup as pre
import tasks.transcript_alignment as alignment
from progress.bar import ChargingBar
import utils.constants as constants


def sb_hesitation_translation(manual_dir, automatic_dir, alignment_dir, hesitations_file = constants.hesitations_file) :
    hesitations = list( utils.read_vocabulary(hesitations_file).keys() )
    # sw2005A000.txt, sw2005A000.txt, sw2005A000.txt                                                                                                          names are equal
    # files = utils.get_dir_tuples([manual_dir, automatic_dir, alignment_dir], ['txt', 'txt', 'txt'], [lambda s : not 'Speech' in s, lambda s : True, lambda s : True], lambda l, ln : l == ln)
    # files = [(stub, f0, f1[0][1], f2[0][1]) for (stub, f0), f1, f2 in files]

    files = [(f.stem, f) for f in utils.get_directory_files(manual_dir, 'txt') if not 'Speech' in f.stem]
    files = [ (s, f, utils.repath(f, manual_dir, automatic_dir), utils.repath(f, manual_dir, alignment_dir)) for (s, f) in files ]
    numbers = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    for stub, manual_file, automatic_file, alignment_file in ChargingBar("Aligning Transcripts").iter(files) :
        manual_full = utils.read_label_timings_from_file(manual_file)
        operations = utils.read_file(alignment_file).split()
        automatic = utils.read_file(automatic_file)
        manual = ' '.join([w['word'] for w in manual_full])
        if len(manual_full) != len(manual.split()) :
            print("manual contains spaces")
        _, manual = pre.process(transcript=manual.lower())
        _, whisper = pre.process(transcript=automatic.lower())
        manual, whisper = alignment.align(manual.split(), whisper.split(), operations)
        for i, x in enumerate(manual) :
            if not x :
                manual_full.insert(i, {'word' : ''})
        manual = manual_full

        if len(manual) != len(whisper) :
            print()
            print("manual original    ", ' '.join([w['word'] for w in manual_full]))
            print("automatic original:", utils.read_file(automatic_file).lower())
            print("operations         ", operations)
            alignment.print_words([w['word'] for w in manual], whisper)
            continue

        for m, w in zip(manual, whisper) :
            if not m['word'] :  # nothing
                i = 2
            elif m['pause_type'] or m['is_restart'] :  # hesitation  (maybe just pause_type)
                i = 1
            else :  # word
                i = 0
            if not w :  # nothing
                j = 2
            elif w in hesitations or w[0] == '-' or w[-1] == '-' :  # hesitation
                j = 1
            else :  # word
                j = 0

            numbers[i][j] += 1

    for n in numbers :
        print(n)

# manual original:    i don't know um actually  earlier tonight we were watching to live and die in l           have you seen that movie
# automatic original: i don't know.   actually, earlier tonight we were watching to live         in dianna l.a. have you seen that movie?
# operations:         ['n', 'n', 'n', 'd', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n',       'd', 'd', 'n', 'r', 'i', 'n', 'n', 'n', 'n', 'n']

#                     i don't know um actually earlier tonight we were watching to live and die in l        have you  seen that movie
#                     i don't know    actually earlier tonight we were watching to live         in dianna l a    have you  seen that


#        whisper
# m      w        h      s
# a   w [1041215,  7648, 51545]
# n   h [185088,  13477, 72413]
# u   s [35439,    1207,     0]
# a
# l


# and_whether_the_the_  _united_nations_i_don't_think_the_u     _will_do_it_on_their_own_but_whether_the_united_nations_comes_around_and_says_hey_wait_a_minute_we_know_this_thing_isn't
# and_what   _are_the_uh_united_nations_i_don't_think_the_u_s   _will_do_it_on_their_own_but_what   _the_united_nations_comes_around_and_says_hey_wait_a_minute_we_know_this_thing_isn't

# i_don't_know_um_actually_earlier_tonight_we_were_watching_to_live_and_die_in_l_    _have_you_seen_that_movie
# i_don't_know_  _actually_earlier_tonight_we_were_watching_to_live_   _   _in_dianna_l   _a  _have_you _seen _that_movie