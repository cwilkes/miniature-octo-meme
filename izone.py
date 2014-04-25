from collections import defaultdict, Counter
import sys


def get_all_moves(row, col):
    ret = defaultdict(list)
    # upper left
    d = row, col
    ret[d].append([(row-1, col-1, 2), (row+0, col-1, 1)])
    ret[d].append([(row-1, col+0, 2), ])
    ret[d].append([(row-1, col+1, 3), (row-1, col+0, 2)])
    ret[d].append([(row+0, col-1, 1), ])
    ret[d].append([(row+1, col-1, 0), (row+0, col-1, 1)])
    # upper right
    d = row, col+1
    ret[d].append([(row-1, col+0, 1), (row-1, col+1, 2)])
    ret[d].append([(row-1, col+1, 2), ])
    ret[d].append([(row-1, col+2, 3), (row-1, col+1, 2)])
    ret[d].append([(row+0, col+2, 3), ])
    ret[d].append([(row+1, col+1, 0), (row+0, col+1, 3)])
    # bottom right
    d = row+1, col+1
    ret[d].append([(row+2, col+0, 1), (row+0, col+1, 0)])
    ret[d].append([(row+2, col+1, 0), ])
    ret[d].append([(row+2, col+2, 3), (row+1, col+1, 0)])
    ret[d].append([(row+1, col+2, 3), ])
    ret[d].append([(row+0, col+2, 2), (row+1, col+2, 3)])
    # bottom left
    d = row+1, col
    ret[d].append([(row+2, col-1, 1), (row+2, col+0, 0)])
    ret[d].append([(row+2, col+0, 0), ])
    ret[d].append([(row+2, col+1, 3), (row+2, col+0, 0)])
    ret[d].append([(row+1, col-1, 1), ])
    ret[d].append([(row+0, col-1, 2), (row+1, col-1, 1)])
    return ret

centered_moves = get_all_moves(0,0)
moves_to_final = defaultdict(list)
for dest in centered_moves.keys():
    for moves in centered_moves[dest]:
        src = moves[0][0], moves[0][1]
        moves_to_final[src].append((dest, moves))


def get_moves_to_dest(src, row, col):
    ret = list()
    for dest, moves in moves_to_final[src]:
        ret.append(((dest[0]+row,dest[1]+col), [(_[0]+row,_[1]+col,_[2]) for _ in moves]))
    return ret


def get_position_id(sr, row, col, direction=None):
    if direction is None:
        return row * sr.board_size + col
    else:
        if direction == 0:
            return get_position_id(sr, row-1, col)
        elif direction == 1:
            return get_position_id(sr, row, col+1)
        elif direction == 2:
            return get_position_id(sr, row+1, col)
        else:
            return get_position_id(sr, row, col-1)


class IZoneRegistry(object):
    def __init__(self, sr):
        self.sr = sr
        self.pos_to_izone = defaultdict(set)
        self.zone_id_to_zone = dict()

    def did_move(self, row, col, direction):
        zone_ids = set()
        pos1 = get_position_id(self.sr, row, col)
        print >>sys.stderr, 'p2izone', self.pos_to_izone.keys()
        for zone_id, block_count in self.pos_to_izone[pos1]:
            zone_ids.add(zone_id)
        pos2 = get_position_id(self.sr, row, col, direction)
        for zone_id, block_count in self.pos_to_izone[pos2]:
            zone_ids.add(zone_id)
        print >>sys.stderr, 'recalculating zones for position (%d,%d) direction %d with pos ids %d and %d: %s' % \
                            (row, col, direction, pos1, pos2, zone_ids)
        for zone_id in zone_ids:
            self.zone_id_to_zone[zone_id].find_pathways()

    def get_best_moves(self):
        # look for number 2 first
        for zone in self.zone_id_to_zone.values():
            if zone.block_count == 2 and len(zone.moves) > 0:
                return zone.moves
        return None

    def remove_izone_links(self, izone_id):
        print >>sys.stderr, 'removing links for zone', izone_id
        try:
            self.pos_to_izone.pop(izone_id)
        except:
            pass

    def register_links(self, izone_id, block_count, moves):
        if not moves:
            return
        print >>sys.stderr, 'allz1', sorted(self.pos_to_izone.keys())
        for block_move in moves:
            for move in block_move:
                pos_id = get_position_id(self.sr, move[0], move[1])
                self.pos_to_izone[pos_id].add((izone_id, block_count))
                print >>sys.stderr, 'Registered (%d,%d,%d) with these zones: %s' % (move[0], move[1], pos_id, self.pos_to_izone[pos_id])
        print >>sys.stderr, 'allz2', sorted(self.pos_to_izone.keys())

    def find_hits(self, positions):
        zone_ids = dict()
        for position in positions:
            pos_id = get_position_id(self.sr, position[0], position[1])
            for zone_id, block_count in self.pos_to_izone[pos_id]:
                zone_ids[zone_id] = block_count
        return zone_ids


def get_square_positions(row, col, direction):
    if direction == 0:
        return [(row, col-1), (row-1, col-1)]


def get_moves_to_middle((row, col), (middle_row, middle_col)):
    src = row-middle_row,col-middle_col
    for dest, moves in moves_to_final[src]:
        yield ((middle_row+dest[0],middle_col+dest[1]), [(_[0]+middle_row,_[1]+middle_col,[2]) for _ in moves])


class IZone(object):
    def __init__(self, sr, izone_registry, row, col):
        self.sr, self.izone_registry = sr, izone_registry
        self.row, self.col = row, col
        self.id = get_position_id(self.sr, self.row, self.col)
        self.moves = list()
        self.block = [(row,col), (row,col+1), (row+1,col+1), (row+1,col)]
        self.outside = [(row-1,col-1), (row-1,col), (row-1,col+1), (row-1, col+2),
                        (row,col+2), (row+1,col+2), (row+2,col+2), (row+2,col+1),
                        (row+2,col), (row+2,col-1), (row+1,col-1), (row-1,col)]
        self.block_count = -1
        self.izone_registry.zone_id_to_zone[self.id] = self

    def _positions_different_color(self, color):
        ret = list()
        for my_row, my_col in self.block:
            if self.sr.get_color(my_row, my_col) != color:
                ret.append((my_row,my_col))
        return ret

    def _interal_get_moves_to_dest(self, r, c):
        return get_moves_to_dest((r-self.row,c-self.col),r, c)

    def _get_moves_for_color_match(self, dest_row, dest_col, color):
        ret = list()
        for dest, moves in self._interal_get_moves_to_dest(dest_row, dest_col):
            src_color = self.sr.get_color(moves[0][0], moves[0][1])
            if src_color == color:
                ret.append(moves)
        return ret

    def _find_best_pathway(self):
        middle = Counter()
        for my_row, my_col in self.block:
            color = self.sr.get_color(my_row, my_col)
            #print >>sys.stderr, 'Color at (%d,%d) is %s' % (my_row, my_col, color)
            middle[color] += 1
        #print >>sys.stderr,'Top colors for (%d,%d): %s' % (self.row, self.col, middle.most_common())
        # if you have 3 inside blocks automatically win
        top_color, top_color_count = middle.most_common()[0]
        if top_color_count == 3:
            # find the odd man out
            dest_row, dest_col = self._positions_different_color(top_color)[0]
            return 3, self._get_moves_for_color_match(dest_row, dest_col, top_color)
        # now we can have 2 or 1 of each color
        if top_color_count == 2:
            ret = list()
            for dest_row, dest_col in self._positions_different_color(top_color):
                ret.extend(self._get_moves_for_color_match(dest_row, dest_col, top_color))
            top_color, top_color_count = middle.most_common()[1]
            if top_color_count == 2:
                for dest_row, dest_col in self._positions_different_color(top_color):
                    ret.extend(self._get_moves_for_color_match(dest_row, dest_col, top_color))
            return 2, ret
        # all colors are different
        ret = list()
        for color in middle.keys():
            for dest_row, dest_col in self._positions_different_color(color):
                ret.extend(self._get_moves_for_color_match(dest_row, dest_col, color))
        return 1, ret

    def find_pathways(self):
        print >>sys.stderr, 'finding pathways for zoneid', self.id
        #self.izone_registry.remove_izone_links(self.id)
        self.block_count, self.moves = self._find_best_pathway()
        self.izone_registry.register_links(self.id, self.block_count, self.moves)

    def __str__(self):
        return 'Pos: (%d,%d), BlockCount:%d, Moves: %s' % (self.row, self.col, self.block_count, self.moves)

def create_zones(sr):
    zones = list()
    registry = IZoneRegistry(sr)
    for row in range(1, sr.board_size-3):
        for col in range(1, sr.board_size-3):
            z = IZone(sr, registry, row, col)
            z.find_pathways()
            zones.append(z)
    return registry, zones
