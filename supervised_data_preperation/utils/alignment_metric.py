

def alignment_error(true_alignment, alignment) :
    errors = []
    for one, two in zip(true_alignment, alignment) :
        size = ( abs( (one['end'] - one['start']) - ( two['end'] - two['start'] ) )  + 1 )
        distance = ( abs( (one['end'] + one['start']) / 2 - ( two['end'] + two['start'] ) / 2 )  + 1 )
        print(one['transcript'], 1 / ( size * distance ))
        errors.append(1 / ( size * distance ))
    return sum(errors) / len(errors)
        