

def lines_to_words(ann) :
    trans = []
    special = set()
    pause_type = ""
    is_restart = False
    for line in ann :
        for part in line.split() :
            if part.startswith('{') :
                pause_type = part[1]
            elif part.endswith('}') :
                pause_type = ""
            elif part.startswith('[') :
                is_restart = True
            elif part.endswith(']') :
                is_restart = False
            elif len(part.split('/')) == 2 :
                word, annotation = part.split('/')
                trans.append({
                    'word' : word,
                    'annotation' : annotation,
                    'pause_type' : pause_type,
                    'is_restart' : is_restart
                })
            else :
                special.add(part)
    return trans, special


def merge_abbreviations(trans) :
    for i in range(len(trans) - 1) :
        if "'" in trans[i + 1]['word'] :
            trans[i]['word'] = trans[i]['word'] + trans[i+1]['word']
            trans[i]['annotation'] = trans[i]['annotation'] + "+" + trans[i+1]['annotation']
            trans[i+ 1]['word'] = ""
    trans = [w for w in trans if w['word']]
    return trans
    

def seperate_speaker(ann_content) :
    ann_content_temp = []
    start = 0
    while start < len(ann_content) :
        end = start
        while end < len(ann_content) and ann_content[end] != '' :
            end += 1
        ann_content_temp.append(ann_content[start:end])
        start = end + 1
    ann_A = [block[1:] for block in ann_content_temp if len(block) > 1 and 'SpeakerA' in block[0]]
    ann_B = [block[1:] for block in ann_content_temp if len(block) > 1 and 'SpeakerB' in block[0]]
    # flatten lists
    return [line for block in ann_A for line in block], [line for block in ann_B for line in block]