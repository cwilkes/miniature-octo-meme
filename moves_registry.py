import sys
import utils


class Rotations(object):
    def __init__(self, window_size):
        self.window_size = window_size
        self.rotation_vector = self._get_rotation_vector()
        self.rotation_map = self._get_2d_rotation_map()
        self.direction_rotation = [3, 0, 1, 2]

    def rotate_bit_values(self, bit_values):
        ret = [False] * len(bit_values)
        for pos, val in enumerate(bit_values):
            ret[self.rotation_map[pos]] = val
        return ret

    def rotate_move(self, row, col, move):
        ret = list(self.rotation_map[row][col])
        ret.append(self.direction_rotation[move])
        return ret

    def _get_rotation_vector(self):
        center = (self.window_size-1)/2.0
        row1 = -center
        col1 = -center
        ret = list()
        for pos1 in range(self.window_size*self.window_size):
            row2, col2 = -col1, row1
            pos2 = int((row2+center)*self.window_size + (col2+center))
            ret.append(pos2)
            col1 += 1
            if col1 > center:
                row1 += 1
                col1 = -center
        return ret

    def _get_2d_rotation_map(self):
        rotation_map = list()
        rot_map_row = list()
        for _ in self.rotation_vector:
            row = _ / self.window_size
            col = _ - self.window_size*row
            rot_map_row.append((row, col))
            if len(rot_map_row) == self.window_size:
                rotation_map.append(rot_map_row)
                rot_map_row = list()
        return rotation_map


class MovesRegistry(object):
    def __init__(self, window_size):
        self.sigs = dict()
        self.window_size = window_size
        self.bit_value_size = window_size*window_size
        self.rotations = Rotations(window_size)
        print >>sys.stderr, 'rotation map', self.rotations.rotation_map

    def register_new_signature(self, bit_values):
        """returns an integer value of the overlay, or None if it has already been registered"""
        as_int = utils.bit_values_to_int(bit_values)
        return None if as_int in self.sigs else as_int

    def register_moves(self, signature, moves):
        self.sigs[signature] = moves
        # now do the rotations
        as_bit_values = list()
        for c in bin(signature)[2:]:
            as_bit_values.append(True if c == '1' else False)
        while len(as_bit_values) < self.window_size*self.window_size:
            as_bit_values.insert(0, False)
        if len(as_bit_values) != self.window_size*self.window_size:
            raise Exception('Bad length from signature %d : %s expected %d have %d' % (signature, as_bit_values, self.window_size*self.window_size, len(as_bit_values)))
        # now rotate these moves around so as to enable fast lookups
        prev_moves = list(moves)
        print >>sys.stderr, 'R:  %d : %s to %s' % (signature, utils.slashie_sig(signature, self.window_size), moves)
        for _ in range(3):
            as_bit_values = self.rotations.rotate_bit_values(as_bit_values)
            my_moves = list()
            for r, c, move in prev_moves:
                my_moves.append(*self.rotations.rotate_move(r, c, move))
            signature = self.register_new_signature(as_bit_values)
            print >>sys.stderr, ' => %05d : %s to %s' % (signature, utils.slashie_sig(signature, self.window_size), my_moves)
            self.sigs[signature] = my_moves
            prev_moves = list(my_moves)

    def get_moves_for(self, bit_values):
        as_int = utils.bit_values_to_int(bit_values)
        if as_int in self.sigs:
            return self.sigs[as_int]
        else:
            return None
