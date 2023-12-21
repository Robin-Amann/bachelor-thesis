

def alignment_error_per_word(true_alignment : list, alignment : list) -> list[float] :
    'true_alignment and alignment need to contain lists of at least \'start\' \'end\' and \'word\''
    errors = []
    for one, two in zip(true_alignment, alignment) :
        if (not one['word']) or (not two['word']) :
            continue
        size = ( abs( (one['end'] - one['start']) - ( two['end'] - two['start'] ) )  + 1 )
        distance = ( abs( (one['end'] + one['start']) / 2 - ( two['end'] + two['start'] ) / 2 )  + 1 )
        errors.append(1 / ( size * distance ))
    return errors


def alignment_error(true_alignment : list, alignment : list) -> float :
    'true_alignment and alignment need to contain lists of at least \'start\' \'end\' and \'word\''
    errors = alignment_error_per_word(true_alignment, alignment)
    if len(errors) == 0 :
        return 1
    return sum(errors) / len(errors)
        

