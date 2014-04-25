import itertools as it
from collections import Counter, defaultdict
import sys




class CachedSolver(object):
    def __init__(self):
        self.cache = dict()

    def solve_pattern(self, pattern):
        if not pattern in self.cache:
            self.cache[pattern] = MoveSolver(pattern).solve_pattern()
        return self.cache[pattern]



def find_patterns(color_finder, window_size, base_row, base_col, color):
    patterns = [[0] * window_size * window_size for _ in range(4)]

    def rotate(a, b):
        return (-b + window_size) % window_size, (a + window_size) % window_size

    def position(r, c):
        return r * window_size + c

    def set_on(r1, c1):
        patterns[0][position(r1, c1)] = 1
        r1, c1 = rotate(r1, c1)
        patterns[1][position(r1, c1)] = 1
        r1, c1 = rotate(r1, c1)
        patterns[2][position(r1, c1)] = 1
        r1, c1 = rotate(r1, c1)
        patterns[3][position(r1, c1)] = 1

    for r, c in it.product(range(4), range(4)):
        if color_finder.get_color(base_row+r, base_col+c) == color:
            set_on(r, c)

    return map(lambda x: ''.join(str(_) for _ in x), patterns)


def count_patterns(board_size, number_colors, color_finder, window_size=4, min_color_size=4):
    cs = CachedSolver()
    ret = dict()
    for base_row, base_col in it.product(range(board_size-window_size+1), range(board_size-window_size+1)):
        color_count = Counter()
        for r, c in it.product(range(base_row, base_row+4), range(base_col, base_col+4)):
            color = color_finder.get_color(r, c)
            color_count[color] += 1
        for color in range(number_colors):
            if color_count[color] >= min_color_size:
                for pattern in find_patterns(color_finder, window_size, base_row, base_col, color):
                    key = base_row, base_col
                    try:
                        if not key in ret:
                            moves = cs.solve_pattern(pattern)
                            ret[key] = cs.solve_pattern(pattern)
                            #print >>sys.stderr, pattern, len(moves), moves
                    except Exception as ex:
                        print >>sys.stderr, ex
    return ret
