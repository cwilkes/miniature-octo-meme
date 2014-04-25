from collections import defaultdict

single_patterns = list()



def get_right_down(board_size, row, col, delta_back, delta_forward):
    for row_ender in range(max(0, row+delta_back), min(board_size, row+delta_forward)):
        for col_ender in range(max(0,col+delta_back), min(board_size, col+delta_forward)):
            yield (row_ender, col_ender)


class Ringer(object):
    def __init__(self, sr):
        self.sr = sr
        self.rings = dict()

    def add_ring(self, a_pos, a_color, b_pos, b_color, do_reverse=True):
        if not a_pos in self.rings:
            self.rings[a_pos] = dict()
        if not b_color in self.rings[a_pos]:
            self.rings[a_pos][b_color] = dict()
        distance = abs(a_pos[0]-b_pos[0]) + abs(a_pos[1]-b_pos[1])
        if not distance in self.rings[a_pos][b_color]:
            self.rings[a_pos][b_color][distance] = list()
        self.rings[a_pos][b_color][distance].append(b_pos)
        if do_reverse:
            self.add_ring(b_pos, b_color, a_pos, a_color, False)

    def _delete_ring(self, pos, color):
        for pos1 in self.rings:
            if color in self.rings[pos1]:
                for distance in self.rings[pos1][color]:
                    try:
                        self.rings[pos1][color][distance].remove(pos)
                    except:
                        pass

    def get_blocks_to_move(self, dest, dest_color):
        ret = list()
        if not dest in self.rings:
            return ret
        if not dest_color in self.rings[dest]:
            return ret
        for distance in sorted(self.rings[dest][dest_color]):
            ret.extend(self.rings[dest][dest_color][distance])
        return ret

    def do_move(self, a_pos, a_color, b_pos, b_color):
        self._delete_ring(a_pos, a_color)
        self._delete_ring(b_pos, b_color)
        for row_ender, col_ender in get_right_down(self.sr.board_size, a_pos[0], a_pos[1], -2, 2):
            self.add_ring(a_pos, b_color, (row_ender,col_ender), self.sr.get_color(row_ender, col_ender), False)
        for row_ender, col_ender in get_right_down(self.sr.board_size, b_pos[0], b_pos[1], -2, 2):
            self.add_ring(b_pos, a_color, (row_ender,col_ender), self.sr.get_color(row_ender, col_ender), False)


def find_moves(src, dst):
    ret = list()
    # do easiest for now
    while src[0] < dst[0]:
        ret.append((src[0], src[1], 2))
        src = src[0]+1, src[1]
    while src[0] > dst[0]:
        ret.append((src[0], src[1], 0))
        src = src[0]-1, src[1]
    while src[1] < dst[1]:
        ret.append((src[0], src[1], 1))
        src = src[0], src[1]+1
    while src[1] > dst[1]:
        ret.append((src[0], src[1], 3))
        src = src[0], src[1]-1
    return list(ret)


class Sweeper(object):
    def __init__(self, sr):
        self.sr = sr
        self.block_moves = defaultdict(list)
        # look for certain patterns
        self.ringer = Ringer(sr)
        for row_starter in range(sr.board_size):
            for col_starter in range(sr.board_size):
                for row_ender, col_ender in get_right_down(sr.board_size, row_starter, col_starter, 0, 2):
                    self.ringer.add_ring((row_starter, col_starter), sr.get_color(row_starter, col_starter),
                                         (row_ender, col_ender), sr.get_color(row_ender, col_ender))
        for row_starter in range(1, sr.board_size-1):
            for col_starter in range(1, sr.board_size-1):
                self._calc_block(row_starter, col_starter)

    def _calc_block(self, row, col):
        my_color = self.sr.get_color(row, col)
        for r, c in get_right_down(self.sr.board_size, row, col, -1, 1):
            if r == row and c == col:
                continue
            if my_color != self.sr.get_color(r, c):
                continue
            for block in self.ringer.get_blocks_to_move((r, c), my_color):
                distance = abs(block[0]-row) + abs(block[1]-col)
                # check that we aren't adding ourselves or my immediate neighbors
                if distance > 1:
                    self.block_moves[(row, col)].append((distance, block))

    def get_blocks_to_move(self, dest, dest_color):
        return self.ringer.get_blocks_to_move(dest, dest_color)

