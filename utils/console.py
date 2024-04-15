

def format_number(x, decimal_places=2, thousands=True, length=-1, force_sign=False) :
    if int(x) == x :
        x = int(x)
    include_force_sign = '+' if force_sign else ''
    include_decimal_place = '0' if type(x) == int else str(decimal_places)
    include_thousands = '' if not thousands else ',' 
    include_length = '' if length <= 0 else str(length)

    format_string = '{:' + include_force_sign + include_length + include_thousands + '.' + include_decimal_place + 'f}'

    return format_string.format(x)


def create_table_representation(table, distance=3, first_left=True, seperator=True, print_comment=True) -> list[str] :
    table_representation = []    
    colum_widths = [ max( [ len(str(row[cell])) for row in table] ) for cell in range(len(table[0])) ]

    for row in table :
        table_representation.append( [ 
            str(cell).ljust(width) if first_left and i == 0 else str(cell).rjust(width) for i, (cell, width) in enumerate(zip(row, colum_widths))
        ] )

    if seperator :
        for row in table_representation :
            row.insert(1, '│')

    for i in range(len(table_representation)) :
        table_representation[i] = (' '*distance).join(table_representation[i])

    if seperator :
        table_representation.insert(1, '─' * (colum_widths[0] + distance) + '┼' + '─' * (sum(colum_widths[1:]) + distance * len(colum_widths[1:]))) 

    if print_comment :
        for i in range(len(table_representation)) :
            table_representation[i] = '#' + ' '*distance + table_representation[i]
    
    return table_representation


def print_table(table, distance=3, first_left=True, seperator=True, print_comment=True) :
    table_representation = create_table_representation(table, distance, first_left, seperator, print_comment)
    for row in table_representation :
        print(row)


def print_tables(tables, table_seperation=10, distance=3, first_left=True, seperator=True, print_comment=True) :
    representations = []

    representations.append( create_table_representation(tables[0], distance, first_left, seperator, print_comment) )
    for table in tables[1:] :
        representations.append( create_table_representation(table, distance, first_left, seperator, print_comment=False) )
    
    max_len = max( len(table) for table in representations )

    for table in representations :
        table += [ ' '* len(table[0]) ] * max(0, max_len - len(table) )

    representation = list(map(list, zip(*representations)))
    for row in representation :
        print((' ' * table_seperation).join(row))
