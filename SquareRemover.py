import sys
import random
import os
from collections import Counter

max_moves = int(os.environ.get('sr_moves', 10000))


templates = list()

# single moves
templates.append(('.m../.x../..../....', [(-1, 0, 2), ]))
templates.append(('..../mx../..../....', [(0, -1, 1), ]))
templates.append(('..m./..x./..../....', [(-1, 1, 2), ]))
templates.append(('..../..xm/..../....', [(0, 2, 2), ]))
templates.append(('..../..../mx../....', [(1, -1, 1), ]))
templates.append(('..../..../.x../.m..', [(2, 0, 0), ]))
templates.append(('..../..../..xm/....', [(1, 2, 3), ]))
templates.append(('..../..../..x./..m.', [(2, 1, 0), ]))

# diagnal
templates.append(('mx../xx../..../....', [(-1, -1, 2), (0, -1, 1)]))
templates.append(('..xm/..xx/..../....', [(-1, 2, 2), (0, 2, 3)]))
templates.append(('..../..../xx../mx..', [(2, -1, 0), (1, -1, 1)]))
templates.append(('..../..../..xx/..xm', [(2, 2, 0), (1, 2, 3)]))

# double slide horz
templates.append(('xx../xxmm/..../....', [(0, 1, 3), (0, 2, 3)]))
templates.append(('..xx/mmxx/..../....', [(0, 0, 1), (0, -1, 1)]))
templates.append(('..../..../xxmm/xx..', [(1, 1, 3), (1, 2, 3)]))
templates.append(('..../..../mmxx/..xx', [(1, 0, 1), (1, -1, 1)]))

# double slide vert
templates.append(('xx../xx../xm../xm..', [(1, 0, 0), (2, 0, 0)]))
templates.append(('xm../xm../xx../xx..', [(0, 0, 2), (-1, 0, 2)]))
templates.append(('..xx/..xx/..mx/..mx', [(1, 1, 0), (2, 1, 0)]))
templates.append(('..mx/..mx/..xx/..xx', [(0, 1, 2), (-1, 1, 2)]))

# three in a row horz
templates.append(('.xx./mmmx/.x../....', [(0, 0, 2), (-1, 0, 2)]))
templates.append(('.xx./mmmx/..x./....', [(0, 1, 2), (0, 0, 1), (-1, 0, 1)]))
templates.append(('.xx./xmmm/.x../....', [(0, 1, 2), (0, 2, 3)]))
templates.append(('..../.x../mmmx/..x.', [(1, 0, 0), (1, -1, 1)]))
templates.append(('..../..x./mmmx/..x.', [(1, 0, 0), (1, -1, 1)]))

# three in a row vert
templates.append(('xm../xmx./xm../xx..', [(0, 0, 1), (-1, 0, 2)]))
templates.append(('xx../xm../xmx./xm..', [(1, 0, 1), (1, 2, 0)]))
templates.append(('..mx/..mx/.xmx/..xx', [(0, 1, 3), (-1, 1, 2)]))
templates.append(('..xx/.xmx/.xmx/.xmx', [(1, 1, 3), (2, 1, 0)]))


def template_row_matches(sr, row, col, row_val, color):
    for col_pos, letter in enumerate(row_val):
        if letter == 'm' and sr.get_color(row, col+(col_pos-1)) != color:
            return False
        if letter == 'x' and sr.get_color(row, col+(col_pos-1)) == color:
            return False
    return True


def do_templates(sr, row, col, color, template_combo):
    template, moves = template_combo
    okay = True
    for row_pos, row_val in enumerate(template.split('/')):
        if not template_row_matches(sr, row+(row_pos-1), col, row_val, color):
            okay = False
    if okay:
        real_moves = [(_[0]+row, _[1]+col, _[2]) for _ in moves]
        print >>sys.stderr, 'At (%d,%d) with color %d matched template %s with moves %s' % (row, col, color, template, real_moves)
        for r, c, direction in real_moves:
            sr.move_tile(r, c, direction)


class Tile(object):
    def __init__(self, row, col, color=-1):
        self.color = color
        self.row = row
        self.col = col

    def is_off_board(self):
        return self.color == -1

    def __str__(self):
        return '(%d,%d,%d)' % (self.row, self.col, self.color)


def get_index(board_size, row, col, direction=None):
    if direction is None:
        return (board_size+2)*(row+1) + col+1
    else:
        new_row, new_col = get_coords(row, col, direction)
        return get_index(board_size, new_row, new_col)


def get_coords(row, col, direction):
    if direction is None:
        return row, col
    elif direction == 0:
        return row-1, col
    elif direction == 1:
        return row, col+1
    elif direction == 2:
        return row+1, col
    elif direction == 3:
        return row, col-1
    else:
        raise Exception('Bad direction: %s' % (direction, ))


def top_left(coord):
    return coord[0]-1, coord[1]-1


def above(coord):
    return coord[0]-1, coord[1]


def top_right(coord):
    return coord[0]-1, coord[1]+1


def left(coord):
    return coord[0], coord[1]-1


def right(coord):
    return coord[0], coord[1]+1


def bottom_left(coord):
    return coord[0]+1, coord[1]-1


def below(coord):
    return coord[0]+1, coord[1]


def bottom_right(coord):
    return coord[0]+1, coord[1]+1


class MySquareRemover(object):
    def __init__(self, colors, board, startSeed):
        self.number_colors = colors
        self.board_size = len(board)
        self.current_seed = startSeed
        self.tiles = list()
        self.moves = list()
        self.random_seed = startSeed
        self.filled_spaces_count = 0
        row = 0
        # add blanks
        for col in range(-1, self.board_size+1):
            self.tiles.append(Tile(-1, col))
        for board_line in board:
            self.tiles.append(Tile(row, -1))
            for col, color in enumerate(board_line):
                self.tiles.append(Tile(row, col, int(color)))
            self.tiles.append(Tile(row, self.board_size))
            row += 1
        for col in range(-1, len(board)+1):
            self.tiles.append(Tile(-1, col))
        print >>sys.stderr, 'board size', self.board_size

    def made_square(self, row, col):
        my_color = self.get_color(row, col)
        # top left
        if self.get_color(row-1, col-1) == my_color and self.get_color(row-1, col) == my_color and self.get_color(row, col-1) == my_color:
            return True
        # top right
        if self.get_color(row-1, col) == my_color and self.get_color(row-1, col+1) == my_color and self.get_color(row, col) == my_color:
            return True
        # bottom left
        if self.get_color(row, col) == my_color and self.get_color(row+1, col-1) == my_color and self.get_color(row+1, col) == my_color:
            return True
        # bottom right
        if self.get_color(row, col+1) == my_color and self.get_color(row+1, col) == my_color and self.get_color(row+1, col+1) == my_color:
            return True
        return False

    def is_under_moves(self):
        return len(self.moves) < max_moves

    def get_tile(self, row, col, direction=None):
        return self.tiles[get_index(self.board_size, row, col, direction)]

    def _same_color(self, row, col, color):
        return self.get_tile(row, col).color == color

    def _next_buffer_color(self):
        ret_val = self.random_seed % self.number_colors
        self.random_seed = (self.random_seed*48271) % 2147483647
        return ret_val

    def _set_tile(self, row, col, color):
        index = get_index(self.board_size, row, col)
        self.tiles[index] = Tile(row, col, color)

    def fill_spaces(self, space1, space2, space3, space4):
        self.filled_spaces_count += 1
        self._set_tile(space1[0], space1[1], self._next_buffer_color())
        self._set_tile(space2[0], space2[1], self._next_buffer_color())
        self._set_tile(space3[0], space3[1], self._next_buffer_color())
        self._set_tile(space4[0], space4[1], self._next_buffer_color())
        print >>sys.stderr, 'filled in space',\
            space1, self.get_color(*space1), \
            space2, self.get_color(*space2), \
            space3, self.get_color(*space3), \
            space4, self.get_color(*space4)

    def check_spaces(self, space1, space2, space3, space4):
        color = self.get_tile(space1[0], space1[1]).color
        if self.get_tile(space2[0], space2[1]).color != color:
            return
        if self.get_tile(space3[0], space3[1]).color != color:
            return
        if self.get_tile(space4[0], space4[1]).color != color:
            return
        # fill in this square
        self.fill_spaces(space1, space2, space3, space4)
        for space in (space1, space2, space3, space4):
            self.check_spaces(top_left(space), above(space), left(space), space)
            self.check_spaces(above(space), top_right(space), space, right(space))
            self.check_spaces(left(space), space, bottom_left(space), below(space))
            self.check_spaces(space, right(space), below(space), bottom_right(space))

    def move_tile(self, row, col, direction):
        tile_src = self.get_tile(row, col)
        tile_dest = self.get_tile(row, col, direction)
        #print >>sys.stderr, 'swapping', tile_src, tile_dest, 'move', len(self.moves)
        self._set_tile(tile_src.row, tile_src.col, tile_dest.color)
        self._set_tile(tile_dest.row, tile_dest.col, tile_src.color)
        self.moves.append((row, col, direction))
        tile_src = self.get_tile(row, col)
        tile_dest = self.get_tile(row, col, direction)
        if direction == 0:
            space = (row-1, col)
            self.check_spaces(top_left(space), above(space), left(space), space)
            self.check_spaces(above(space), top_right(space), space, right(space))
            self.check_spaces(left(space), space, bottom_left(space), below(space))
            self.check_spaces(space, right(space), below(space), bottom_right(space))
            space = (row, col)
            self.check_spaces(left(space), space, bottom_left(space), below(space))
            self.check_spaces(space, right(space), below(space), bottom_right(space))
        elif direction == 1:
            space = (row, col)
            self.check_spaces(top_left(space), above(space), left(space), space)
            self.check_spaces(above(space), top_right(space), space, right(space))
            space = (row, col+1)
            self.check_spaces(above(space), top_right(space), space, right(space))
            space = (row, col)
            self.check_spaces(left(space), space, bottom_left(space), below(space))
            self.check_spaces(space, right(space), below(space), bottom_right(space))
            space = (row, col+1)
            self.check_spaces(space, right(space), below(space), bottom_right(space))
        elif direction == 2:
            space = (row, col)
            self.check_spaces(top_left(space), above(space), left(space), space)
            self.check_spaces(above(space), top_right(space), space, right(space))
            self.check_spaces(left(space), space, bottom_left(space), below(space))
            self.check_spaces(space, right(space), below(space), bottom_right(space))
            space = (row+1, col)
            self.check_spaces(left(space), space, bottom_left(space), below(space))
            self.check_spaces(space, right(space), below(space), bottom_right(space))
        elif direction == 3:
            space = (row, col-1)
            self.check_spaces(top_left(space), above(space), left(space), space)
            self.check_spaces(above(space), top_right(space), space, right(space))
            space = (row, col)
            self.check_spaces(above(space), top_right(space), space, right(space))
            space = (row, col-1)
            self.check_spaces(left(space), space, bottom_left(space), below(space))
            self.check_spaces(space, right(space), below(space), bottom_right(space))
            space = (row, col)
            self.check_spaces(space, right(space), below(space), bottom_right(space))

    def remaining_move_count(self):
        return max_moves - len(self.moves)

    def get_color(self, row, col=None):
        if col is None:
            return self.tiles[row].color
        else:
            return self.tiles[get_index(self.board_size, row, col)].color

    def get_tile(self, row, col, direction=None):
        return self.tiles[get_index(self.board_size, row, col, direction)]

    def count_buddies(self, row, col, color=None):
        buddies = list()
        if color is None:
            color = self.get_color(row, col)
        for direction in range(4):
            buddies.append(self.get_tile(row, col, direction).color == color)
        return buddies

    def count_buddies_not_back(self, row, col, direction):
        next_row, next_col = get_coords(row, col, direction)
        next_buddies = self.count_buddies(next_row, next_col, self.get_color(row, col))
        next_buddies[(direction+2) % 4] = False
        return next_buddies

    def _should_do_swap(self, row, col, direction):
        #print >>sys.stderr,'Checking swap for', row, col, direction
        next_tile = self.get_tile(row, col, direction)
        if next_tile.is_off_board():
            return False
        if self.get_tile(row, col).color == next_tile.color:
            print >>sys.stderr, ' (%s) no same color %s' % (col, self.get_tile(row, col).color)
            return False
        buddy_count_me = sum(self.count_buddies(row, col))
        buddy_count_me_next = sum(self.count_buddies_not_back(row, col, direction))
        buddy_count_next = sum(self.count_buddies(row, col+1))
        row_next, col_next = get_coords(row, col, direction)
        buddy_count_next_me = sum(self.count_buddies_not_back(row_next, col_next, (direction+2)%4))
        if buddy_count_me_next > buddy_count_me and buddy_count_next_me > buddy_count_next:
            return True
        print >>sys.stderr, ' (%s) my new count and other new count 0' % (col, )
        return False

    def do_row_swaps(self, row):
        move_count = 0
        print >>sys.stderr, 'Row', row
        for col in range(self.board_size-1):
            if self._should_do_swap(row, col, 1):
                self.move_tile(row, col, 1)
                move_count += 1
                continue
        print >>sys.stderr, 'Row %d did %d moves' % (row, move_count)
        return move_count


def get_best_color(sr, row, col, delta=1):
    # for now get the one with the most tiles and the lowest color number
    counts = Counter()
    for r in range(row-delta, row+delta+2):
        for c in range(col-delta, col+delta+2):
            counts[sr.get_color(r, c)] += 1
    best_color = 0
    best_color_count = 0
    for color in sorted(counts.keys()):
        if counts[color] > best_color_count:
            best_color = color
            best_color_count = counts[color]
    return best_color, counts[best_color]


def play_make_threes2(sr):
    start_row, start_col = 1, 1
    while sr.is_under_moves():
        cur_moves = len(sr.moves)
        for template in reversed(templates):
            print >>sys.stderr, 'on template', template
            for row in range(start_row, sr.board_size-2, 4):
                for col in range(start_col, sr.board_size-2, 4):
                    best_color, count = get_best_color(sr, row, col, 0)
                    if count != 3:
                        best_color, count = get_best_color(sr, row, col, 1)
                    do_templates(sr, row, col, best_color, template)
        if len(sr.moves) == cur_moves:
            break


def play_fill_ending(sr):
    while len(sr.moves) > max_moves:
        sr.moves.pop(max_moves)
    while sr.is_under_moves():
        sr.move_tile(0,0,1)

import pattern_counter as pc
from collections import defaultdict
import itertools as it

def do_single_round(sr, all_moves, chop_off_end_move=True):
    print >>sys.stderr, 'ROUND'
    # dictionary in form (row,col) => list of moves to solve
    # put in a queue so as to pull off the best ones
    queue = defaultdict(list)
    for key, moves in all_moves.items():
        queue[len(moves)].append((key, moves))
    # just start grabbing from the top
    moved_pieces = set()

    def key_in_moved(my_key):
        if (my_key[0]+1, my_key[1]+1) in moved_pieces:
            return True
        if (my_key[0]+1, my_key[1]+2) in moved_pieces:
            return True
        if (my_key[0]+2, my_key[1]+1) in moved_pieces:
            return True
        if (my_key[0]+1, my_key[1]+2) in moved_pieces:
            return True
        return False

    def moves_in_moved(moves):
        for r, c, direction in moves:
            if (r, c) in moved_pieces:
                return True
        return False

    count_moves = 0

    for number_moves in sorted(queue.keys()):
        print >>sys.stderr, ' Working on number moves %d with %d chances' % (number_moves, len(queue[number_moves]))
        for key, moves in queue[number_moves]:
            if key_in_moved(key):
                continue
                random.shuffle(moves)
            converted_moves = [(_[0] + key[0], _[1] + key[1], _[2]) for _ in moves]
            if moves_in_moved(converted_moves):
                continue
            lst = converted_moves[:-1] if chop_off_end_move else converted_moves
            if len(lst) == 0:
                continue
            pre_filled_count = sr.filled_spaces_count
            for move in lst:
                sr.move_tile(*move)
            count_moves += 1
            if sr.filled_spaces_count != pre_filled_count:
                print >>sys.stderr, 'breaking out as filled a spot'
                return count_moves
            # protect all of my turf
            for a, b in it.product(range(4), range(4)):
                moved_pieces.add((key[0]+a, key[1]+b))
            print >>sys.stderr, '  Did moves', lst
    return count_moves


import move_finder

class SquareRemover(object):
    def __init__(self):
        pass

    def playIt(self, colors, board, startSeed):
        sr = MySquareRemover(colors, board, startSeed)
        mf = move_finder.MoveFinder(sr, 4)
        for (row, col), color_moves in mf.find_moves(0):
            print row, col, color_moves
        all_moves = pc.count_patterns(sr.board_size, sr.number_colors, sr)
        loop_count = 0
        while loop_count < 500:
            do_single_round(sr, all_moves)
            all_moves = pc.count_patterns(sr.board_size, sr.number_colors, sr)
            if do_single_round(sr, all_moves, False) < 1:
                break
            all_moves = pc.count_patterns(sr.board_size, sr.number_colors, sr)
            if do_single_round(sr, all_moves, False) < 1:
                break
            all_moves = pc.count_patterns(sr.board_size, sr.number_colors, sr)
            do_single_round(sr, all_moves)
            all_moves = pc.count_patterns(sr.board_size, sr.number_colors, sr)
            if do_single_round(sr, all_moves, False) < 1:
                break
            loop_count+=1
        play_fill_ending(sr)
        moves_ret = list()
        for row, col, direction in sr.moves:
            moves_ret.append(row)
            moves_ret.append(col)
            moves_ret.append(direction)
        return moves_ret


if __name__ == '__main__':
    colors = int(sys.stdin.readline().strip())
    N = int(sys.stdin.readline().strip())
    board = list()
    for _ in range(N):
        board.append(sys.stdin.readline().strip())
    startSeed = int(sys.stdin.readline().strip())
    sre = SquareRemover()
    ret = sre.playIt(colors, board, startSeed)
    if len(ret) != 3*max_moves:
        raise Exception('Must be array of length 30000, not %d' % (len(ret), ))

    for line in ret:
        print line
    sys.stdout.flush()
