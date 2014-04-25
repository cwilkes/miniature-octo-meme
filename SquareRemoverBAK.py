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
templates.append(('..../..x./mmmx/..x.', [(1, 1, 0), (1, 0, 1), (1, -1, 1)]))

# three in a row vert
templates.append(('xm../xmx./xm../xx..', [(0, 0, 1), (-1, 0, 2)]))
templates.append(('xx../xm../xmx./xm..', [(1, 0, 1), (1, 2, 0)]))
templates.append(('..mx/..mx/.xmx/..xx', [(0, 1, 3), (-1, 1, 2)]))
templates.append(('..xx/.xmx/..mx/..mx', [(1, 1, 3), (2, 1, 0)]))


def template_row_matches(sr, row, col, row_val, color):
    for col_pos, letter in enumerate(row_val):
        if letter == 'm' and sr.get_color(row, col+(col_pos-1)) != color:
            return False
        if letter == 'x' and sr.get_color(row, col+(col_pos-1)) == color:
            return False
    return True


def do_templates(sr, row, col, color, template_pos):
    template, moves = templates[template_pos]
    okay = False
    for row_pos, row_val in enumerate(template.split('/')):
        if template_row_matches(sr, row+(row_pos-1), col, row_val, color):
            okay = True
    if okay:
        print >>sys.stderr, 'At (%d,%d) with color %d matched template %s with moves %s' % (row, col, color, template, moves)
        for row_d, col_d, move in moves:
            sr.move_tile(row+row_d, col+col_d, move)


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


class SquareRemover(object):
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


def play_randomly(sr):
    while sr.is_under_moves():
        row = random.randint(1, sr.board_size-2)
        col = random.randint(1, sr.board_size-2)
        direction = random.randint(0, 3)
        sr.move_tile(row, col, direction)


def get_min_max_for_size(pos, size, max_val):
    min_amount = max(0, pos-size/2)
    max_amount = min(max_val, min_amount+size)
    return list(range(max_amount-size, max_amount))


def make_neighbors_frame(sr):
    neighbors = list()
    for row in range(sr.board_size):
        neighbor_row = list()
        for col in range(sr.board_size):
            color_row = list()
            for c in range(sr.number_colors):
                color_row.append([set() for _ in range(5)])
            neighbor_row.append(color_row)
        neighbors.append(neighbor_row)
    for row in range(sr.board_size):
        for col in range(sr.board_size):
            c = dict()
            for color in range(sr.number_colors):
                c[color] = [set() for _ in range(10)]
            for row2 in get_min_max_for_size(row, 5, sr.board_size):
                for col2 in get_min_max_for_size(col, 5, sr.board_size):
                    color = sr.get_color(row2, col2)
                    distance = abs(row-row2) + abs(col-col2)
                    c[color][distance].add(((row2, col2), distance))
    return neighbors


def play_left_to_right(sr):
    print >>sys.stderr, make_neighbors_frame(sr)
    row = 0
    times_through = 0
    reversed = False
    while len(sr.moves) < max_moves:
        color = row % sr.number_colors
        r = range(sr.board_size-1)
        if reversed:
            color = (color + 1) % sr.number_colors
            r = range(sr.board_size-1, 0, -1)
        print >>sys.stderr, 'move', len(sr.moves), 'row', row, 'color', color
        did_move = False
        for col in r:
            if sr.get_color(row, col) == color:
                continue
            if sr.get_color(row,col+1) == color:
                sr.move_tile(row, col, 1)
                did_move = True
            if len(sr.moves) == max_moves:
                break
        row = (row + 1) % sr.board_size
        if did_move:
            times_through = 0
        else:
            times_through += 1
            if times_through >= sr.board_size:
                if reversed:
                    reversed = False
                    times_through = 0
                else:
                    reversed = True
                    times_through = 0
    play_randomly(sr)


def play_row_swaps(sr):
    row = 0
    move_scores = list()
    while len(sr.moves) < max_moves:
        move_scores.append(sr.do_row_swaps(row))
        if len(move_scores) == 2*sr.board_size:
            if sum(move_scores) == 0:
                break
            move_scores.pop(0)
        row = (row + 1) % sr.board_size
    print >>sys.stderr, 'switching to random mode'
    play_randomly(sr)
    while len(sr.moves) > max_moves:
        sr.moves.pop(max_moves)
    print >>sys.stderr, 'rows', len(sr.moves)


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


def do_slide_top_left(sr, row, col, color):
    if sr.get_color(row, col) == color:
        return False
    if sr.get_color(row-1, col) == color:
        sr.move_tile(row-1, col, 2)
        return True
    elif sr.get_color(row, col-1) == color:
        sr.move_tile(row, col-1, 1)
        return True
    return False


def do_slide_top_right(sr, row, col, color):
    if sr.get_color(row, col+1) == color:
        return False
    if sr.get_color(row-1, col+1) == color:
        sr.move_tile(row-1, col+1, 2)
        return True
    elif sr.get_color(row, col+2) == color:
        sr.move_tile(row, col+2, 3)
        return True
    return False


def do_slide_bottom_left(sr, row, col, color):
    if sr.get_color(row+1, col) == color:
        return False
    if sr.get_color(row+1, col-1) == color:
        sr.move_tile(row+1, col-1, 1)
        return True
    elif sr.get_color(row+2, col) == color:
        sr.move_tile(row+2, col, 0)
        return True
    return False


def do_slide_bottom_right(sr, row, col, color):
    if sr.get_color(row+1, col+1) == color:
        return False
    if sr.get_color(row+2, col+1) == color:
        sr.move_tile(row+2, col+1, 0)
        return True
    elif sr.get_color(row+1, col+2) == color:
        sr.move_tile(row+1, col+2, 3)
        return True
    return False


def make_three_square(sr, row, col):
    best_color, number_tiles = get_best_color(sr, row, col)
    print >>sys.stderr, 'Working on (%d,%d) color: %d, tile count: %d' %(row, col, best_color, number_tiles)
    # hard code for now
    number_placed = sr.get_color(row, col) == best_color
    number_placed += sr.get_color(row, col+1) == best_color
    number_placed += sr.get_color(row+1, col) == best_color
    number_placed += sr.get_color(row+1, col+1) == best_color
    print >>sys.stderr,'number placed', number_placed
    if number_placed >= 3:
        return True
    if do_slide_top_left(sr, row, col, best_color):
        number_placed += 1
        print >>sys.stderr, 'TL number placed', number_placed
        if number_placed >= 3:
            return True
    if do_slide_top_right(sr, row, col, best_color):
        number_placed += 1
        print >>sys.stderr, 'TR number placed', number_placed
        if number_placed >= 3:
            return True
    if do_slide_bottom_left(sr, row, col, best_color):
        number_placed += 1
        print >>sys.stderr,'BL number placed', number_placed
        if number_placed >= 3:
            return True
    if do_slide_bottom_right(sr, row, col, best_color):
        number_placed += 1
        print >>sys.stderr,'BR number placed', number_placed
        if number_placed >= 3:
            return True
    # bah, didn't have enough to make a three spot
    return False


def find_double_slide(sr, row, col, color, d1):
    if sr.get_color(row, col) == color:
        return False
    if sr.get_color(row,col+1) == color:
        if sr.get_color(row,col+2) == color:
            sr.move_tile(row,col+1, 3)
            sr.move_tile(row,col+2, 3)
            return True
        if sr.get_color(row-1,col+1) == color:
            sr.move_tile(row,col+1, 3)
            sr.move_tile(row-1,col+1, 2)
            return True
    if sr.get_color(row+1,col) == color:
        if sr.get_color(row+1,col-1) == color:
            sr.move_tile(row+1,col, 0)
            sr.move_tile(row+1,col-1, 1)
            return True
        if sr.get_color(row+2,col) == color:
            sr.move_tile(row+1,col, 0)
            sr.move_tile(row+2,col, 0)
            return True


def complete_four_square(sr, row, col):
    best_color, count = get_best_color(sr, row, col, 0)
    if do_slide_top_left(sr, row, col, best_color):
        count+=1
        if count == 4:
            return True
    if do_slide_top_right(sr, row, col, best_color):
        count+=1
        if count == 4:
            return True
    if do_slide_bottom_left(sr, row, col, best_color):
        count+=1
        if count == 4:
            return True
    if do_slide_bottom_right(sr, row, col, best_color):
        count+=1
        if count == 4:
            return True
    # hrm, well see if we can recruit anyone
    if not sr.get_color(row, col) == best_color and sr.get_color(row-1,col-1) == best_color:
        sr.move_tile(row-1,col-1, 2)
        sr.move_tile(row,col-1, 1)
        count+=1
        if count == 4:
            return True
    if not sr.get_color(row, col+1) == best_color and sr.get_color(row-1,col+2) == best_color:
        sr.move_tile(row-1,col+2, 2)
        sr.move_tile(row,col+2, 3)
        count+=1
        if count == 4:
            return True
    if not sr.get_color(row+1, col) == best_color and sr.get_color(row+2,col-1) == best_color:
        sr.move_tile(row+2,col-1, 0)
        sr.move_tile(row+1,col-1, 1)
        count+=1
        if count == 4:
            return True
    if not sr.get_color(row+1, col+1) == best_color and sr.get_color(row+2,col+2) == best_color:
        sr.move_tile(row+2,col+2, 0)
        sr.move_tile(row+1,col+2, 3)
        count+=1
        if count == 4:
            return True
    # finally check to see if we should do a slide with existing block
    find_double_slide(sr, row, col, best_color, (0,1), (0,))


    if sr.get_color(row,col+1) == color:
        if sr.get_color(row,col+2) == color:
            sr.move_tile(row,col+1, 3)
            sr.move_tile(row,col+2, 3)
            return True
        if sr.get_color(row-1,col+1) == color:
            sr.move_tile(row,col+1, 3)
            sr.move_tile(row-1,col+1, 2)
            return True
    if sr.get_color(row+1,col) == color:
        if sr.get_color(row+1,col-1) == color:
            sr.move_tile(row+1,col, 0)
            sr.move_tile(row+1,col-1, 1)
            return True
        if sr.get_color(row+2,col) == color:
            sr.move_tile(row+1,col, 0)
            sr.move_tile(row+2,col, 0)
            return True


def play_make_threes(sr):
    """Makes L shaped tokens"""
    quit = False
    while not quit:
        move_count = len(sr.moves)
        for row in range(1, sr.board_size-1, 4):
            for col in range(1, sr.board_size-1, 4):
                if sr.remaining_move_count() < 4:
                    quit = True
                    break
                make_three_square(sr, row, col)
        for row in range(1, sr.board_size-1, 4):
            for col in range(1, sr.board_size-1, 4):
                if sr.remaining_move_count() < 8:
                    quit = True
                    break
                complete_four_square(sr, row, col)
        if len(sr.moves) == move_count:
            break
    while sr.is_under_moves():
        sr.move_tile(0,0,1)


def play_make_threes2(sr):
    start_row, start_col = 1, 1
    while sr.is_under_moves():
        cur_moves = len(sr.moves)
        for template_pos in range(len(templates)):
            print >>sys.stderr, 'on template pos', template_pos
            for row in range(start_row, sr.board_size-2, 4):
                for col in range(start_col, sr.board_size-2, 4):
                    best_color, count = get_best_color(sr, row, col, 0)
                    if count != 3:
                        best_color, count = get_best_color(sr, row, col, 1)
                    do_templates(sr, row, col, best_color, template_pos)
        if len(sr.moves) == cur_moves:
            break

def play_fill_ending(sr):
    while len(sr.moves) > max_moves:
        sr.moves.pop(max_moves)
    while sr.is_under_moves():
        sr.move_tile(0,0,1)

import izone, sweeper


def do_sweeper(sr):
    s = sweeper.Sweeper(sr)
    pos = 1,1
    color = 2
    for key, val in s.block_moves.items():
        print >>sys.stderr, key, val

def playIt(colors, board, startSeed):
    sr = SquareRemover(colors, board, startSeed)
    # zregistry = izone.create_zones(sr)[0]
    # for _ in range(200):
    #     moves = zregistry.get_best_moves()
    #     print >>sys.stderr, 'zmoves', moves
    #     if moves:
    #         for block_moves in moves:
    #             for move in block_moves:
    #                 sr.move_tile(move[0], move[1], move[2])
    #                 zregistry.did_move(move[0], move[1], move[2])
    #     else:
    #         break
    # play_randomly(sr)
    # play_row_swaps(sr)
    #play_left_to_right(sr)
    play_make_threes2(sr)
    #do_sweeper(sr)
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

    ret = playIt(colors, board, startSeed)
    if len(ret) != 3*max_moves:
        raise Exception('Must be array of length 30000, not %d' % (len(ret), ))

    for line in ret:
        print line
    sys.stdout.flush()
