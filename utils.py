import itertools as it
import math


def row_and_columns(row_start, row_end, column_start, column_end):
    return it.product(range(row_start, row_end+1), range(column_start, column_end+1))


def vector_pos(window_size, row, col):
    return window_size*row + col


def swap_bits(bit_values, window_size, row, col, move_direction):
    move_to_row, move_to_row = next_position(row, col, move_direction)
    from_position = vector_pos(window_size, row, col)
    to_position = vector_pos(window_size, move_to_row, move_to_row)
    bit_values[from_position], bit_values[to_position] = bit_values[to_position], bit_values[from_position]


def next_position(row, col, direction):
    if direction == 0:
        return row-1, col
    elif direction == 1:
        return row, col+1
    elif direction == 2:
        return row+1, col
    elif direction == 3:
        return row, col-1
    else:
        raise Exception('Do not know how to move "%s"', direction)

def bit_values_to_int(bit_values):
    as_int = 0
    for pos, val in enumerate(bit_values):
        as_int += math.pow(2, len(bit_values)-pos-1) if val else 0
    return int(as_int)


def slashie_sig(signature_number, window_size=None):
    ret = ''
    word = bin(signature_number)[2:]
    while len(word) < window_size*window_size:
        word = '0' + word
    for i in range(0, len(word), window_size):
        if ret:
            ret += '/'
        ret += word[i:i+window_size]
    return ret
