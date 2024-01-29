data = [[ +251.946, -75.663, -7.325, +82.988, 1306112], [343071,  46076, 53740, 1115171, 1558058], [144654,  62371, 61194, 1091422, 1359641], [101027,  77545, 60880, 1076562, 1316014]]


def create_table_representation(table, distance=3, first_left=True, seperator=True, print_comment=True) :
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




print('# min len =', 0.2)
print_table([
        ['', 'insert', 'delete', 'replace', 'nothing', 'all', 'wer'],
    ] + [
        [ label ] + [ f'{x:+,}' for x in data_t] + ['{:6.4f}'.format(sum(data_t[:3]) / data_t[4])] for label, data_t in zip(['base', 'partial', '50', 'total'], data)
    ])
print()

