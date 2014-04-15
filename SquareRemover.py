import sys
import random


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
        print >>sys.stderr, 'filling in space', space1, space2, space3, space4
        self._set_tile(space1[0], space1[1], self._next_buffer_color())
        self._set_tile(space2[0], space2[1], self._next_buffer_color())
        self._set_tile(space3[0], space3[1], self._next_buffer_color())
        self._set_tile(space4[0], space4[1], self._next_buffer_color())

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
        print >>sys.stderr, 'swapping', tile_src, tile_dest
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
    while len(sr.moves) < 10000:
        row = random.randint(1, sr.board_size-2)
        col = random.randint(1, sr.board_size-2)
        direction = random.randint(0, 3)
        sr.move_tile(row, col, direction)


def play_left_to_right(sr):
    row = 0
    times_through = 0
    while len(sr.moves) < 10000:
        color = row % sr.number_colors
        print >>sys.stderr, 'move', len(sr.moves), 'row', row, 'color', color
        did_move = False
        for col in range(sr.board_size-1):
            if sr.get_color(row, col) == color:
                continue
            if sr.get_color(row,col+1) == color:
                did_move = True
                sr.move_tile(row, col, 1)
            if len(sr.moves) == 10000:
                break
        row = (row + 1) % sr.board_size
        if did_move:
            times_through = 0
        else:
            times_through += 1
            if times_through >= sr.board_size:
                break
    play_randomly(sr)


def play_row_swaps(sr):
    row = 0
    move_scores = list()
    while len(sr.moves) < 10000:
        move_scores.append(sr.do_row_swaps(row))
        if len(move_scores) == 2*sr.board_size:
            if sum(move_scores) == 0:
                break
            move_scores.pop(0)
        row = (row + 1) % sr.board_size
    print >>sys.stderr, 'switching to random mode'
    play_randomly(sr)
    while len(sr.moves) > 10000:
        sr.moves.pop(10000)
    print >>sys.stderr, 'rows', len(sr.moves)


def playIt(colors, board, startSeed):
    sr = SquareRemover(colors, board, startSeed)
    # play_randomly(sr)
    # play_row_swaps(sr)
    play_left_to_right(sr)
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
    if len(ret) != 30000:
        raise Exception('Must be array of length 30000, not %d' % (len(ret), ))

    for line in ret:
        print line
    sys.stdout.flush()
