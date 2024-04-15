

def alignment_error_per_word(true_alignment : list, alignment : list, position=True, length=True) -> list[float] :
    'true_alignment and alignment need to contain lists of at least \'start\' \'end\' and \'word\''
    errors = []
    for one, two in zip(true_alignment, alignment) :
        if (not one['word']) or (not two['word']) or (one['end'] - one['start']) == 0 :
            continue

        if length :
            size = ( abs( (one['end'] - one['start']) - ( two['end'] - two['start'] ) ) /  (one['end'] - one['start'])  + 1 )
        else :
            size = 1
        if position :
            distance = ( abs( (one['end'] + one['start']) / 2 - ( two['end'] + two['start'] ) / 2 ) /  (one['end'] - one['start']) + 1 )
        else :
            distance = 1
        
        errors.append(1 / ( size * distance ))
    return errors


def alignment_error(true_alignment : list, alignment : list, position=True, length=True) -> float :
    'true_alignment and alignment need to contain lists of at least \'start\' \'end\' and \'word\''
    errors = alignment_error_per_word(true_alignment, alignment, position, length)
    if len(errors) == 0 :
        return 1
    return sum(errors) / len(errors)
        

