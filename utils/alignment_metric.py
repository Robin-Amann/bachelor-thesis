# error: what if some words are missing?

# list of words with at least 'start' and 'end' and 'word'
# lists need to be same size
def alignment_error(true_alignment : list, alignment : list) :
    'true_alignment and alignment need to contain lists of at least \'start\' \'end\' and \'word\''
    errors = []
    for one, two in zip(true_alignment, alignment) :
        if (not one['word']) or (not two['word']) :
            continue
        size = ( abs( (one['end'] - one['start']) - ( two['end'] - two['start'] ) )  + 1 )
        distance = ( abs( (one['end'] + one['start']) / 2 - ( two['end'] + two['start'] ) / 2 )  + 1 )
        errors.append(1 / ( size * distance ))
    if len(errors) == 0 :
        return 1
    return sum(errors) / len(errors)
        