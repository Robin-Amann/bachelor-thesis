import utils.file as utils
import utils.constants as c
import utils.wer_alignment as alignment
import utils.transcript as word_utils

# # # # # # # # # # # # # check why words are beeing wrongfully transcribed # # # # # # # # # # # # #

files = utils.get_dir_tuples([(c.manual_seg_dir, None, lambda f: not 'Speech' in f.stem), c.automatic_align_dir / '0'])

print(files[0])
i = 0
for manual_f, automatic_f in files :
    manual = utils.read_dict(manual_f)

    if len(manual) < 50 :
        continue
    automatic = utils.read_dict(automatic_f)
    manual, automatic, _ = alignment.align_words(manual, automatic, {'word' : ''})

    snips = []
    x = 0
    while x < len(manual) :
        m = manual[x]
        a = automatic[x]
        if m['word'] and a['word'] and word_utils.simplify(m['word']) != word_utils.simplify(a['word']) :
            y = x + 1
            while y < len(manual) and manual[y]['word'] and automatic[y]['word'] and word_utils.simplify(manual[y]['word']) != word_utils.simplify(automatic[y]['word']) :
                y += 1
            
            snips.append( ( manual[max(0, x-2):min(len(manual), y+2)], automatic[max(0, x-2):min(len(manual), y+2)]) )

            x = y + 1
        x += 1

    if snips :
        manual_s = []
        automatic_s = []
        for snip in snips :
            manual_s += [ w['word'] for w in snip[0] ] + ['|']
            automatic_s += [ w['word'] for w in snip[1] ] + ['|']

        alignment.print_words(manual_s[:-1], automatic_s[:-1])
        i += 1

    if i == 10 :
        break



# # # # # # # # # # # # # look at how automatic + retranscribed are aligned by WER # # # # # # # # # # # # #

files = utils.get_dir_tuples([
    (c.manual_seg_dir, None, lambda f: 'Speech' not in f.stem), 
    c.automatic_align_dir / '0', 
    c.retranscibed_dir / 'wav2vec2_LM'
])

for m, a, h in files[:5] :
    print(m.stem)
    manual = utils.read_dict(m)
    automatic = utils.read_dict(a)
    hesitation = utils.read_dict(h)

    ma, aa = alignment.align([ w['word'] for w in  manual], [ w['word'] for w in automatic ])
    alignment.print_words(ma, aa, speakers=['M:', 'A:'], word_per_line=50)

    ah = automatic + hesitation
    ah.sort(key=lambda w : w['start'])

    ma, aa = alignment.align([ w['word'] for w in manual ], [ w['word'] for w in ah ])
    alignment.print_words(ma, aa, speakers=['M:', 'A:'], word_per_line=50)
