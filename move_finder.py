import moves_registry
import utils


class MoveAttempts(object):
    def __init__(self, window_size):
        # window_size is ignored for now, always 4
        self.requirements = list()
        self.moves = list()
        self.rot = moves_registry._get_2d_rotation_map(4)
        self.direction_rotation = [3, 0, 1, 2]
        self._create_move_attempts()

    def get_requirements_and_moves(self):
        return zip(self.requirements, self.moves)

    def _add_moves(self, requirements, moves):
        self.requirements.append(requirements)
        self.moves.append(moves)
        for _ in range(3):
            my_req = list()
            my_moves = list()
            for req in self.requirements[-1]:
                nextplacement = self.rot[req[0]][req[1]]
                my_req.append((nextplacement[0], nextplacement[1], req[2]))
            for move in self.moves[-1]:
                nextplacement = self.rot[move[0]][move[1]]
                my_moves.append((nextplacement[0], nextplacement[1], self.direction_rotation[move[2]]))
            self.requirements.append(my_req)
            self.moves.append(my_moves)

    def _create_move_attempts(self):
        # one hop in
        self._add_moves([(0, 1, True), (1, 1, False)], [(0, 1, 2), ])
        self._add_moves([(0, 2, True), (1, 2, False)], [(0, 2, 2), ])
        # move to side and in
        self._add_moves([(0, 1, True), (0, 2, False), (1, 2, False)], [(0, 1, 1), (0, 1, 2)])
        self._add_moves([(0, 2, True), (0, 1, False), (1, 1, False)], [(0, 2, 3), (0, 1, 2)])
        # push in
        self._add_moves([(0, 1, True), (1, 1, True), (2, 1, False)], [(1, 1, 2), (0, 1, 2)])
        self._add_moves([(0, 2, True), (1, 2, True), (2, 2, False)], [(1, 2, 2), (0, 2, 2)])
        # do L push
        self._add_moves([(0, 1, True), (1, 1, True), (2, 2, True), (2, 3, False)], [(2, 2, 1), (1, 1, 2), (0, 1, 2)])
        self._add_moves([(0, 2, True), (1, 2, True), (2, 2, True), (2, 1, False)], [(2, 2, 3), (1, 2, 2), (0, 2, 2)])
        # get out of corner
        self._add_moves([(0, 0, True), (0, 1, False), (1, 1, False)], [(0, 0, 1), (0, 1, 2)])
        self._add_moves([(0, 0, True), (0, 1, False), (0, 2, False), (1, 2, False)], [(0, 0, 1), (0, 1, 1), (0, 2, 2)])
        self._add_moves([(0, 0, True), (1, 0, False), (2, 0, False), (2, 1, False)], [(0, 0, 2), (1, 0, 2), (2, 0, 1)])
        self._add_moves([(0, 0, True), (1, 0, False), (2, 0, False), (2, 1, True), (2, 2, False)], [(0, 0, 2), (1, 0, 2), (2, 1, 1), (2, 0, 1)])


class MoveFinder(object):
    def __init__(self, sr, window_size=4):
        self.window_size = window_size
        self.move_attempts = MoveAttempts(self.window_size)
        self.move_registry = moves_registry.MovesRegistry(self.window_size)

    def find_moves(self, row_start):
        column = 0
        while column + self.window_size <= self.sr.board_size:
            self.move_registry.register_new_signature()
            moves_for_color = list()
            for color, bit_values in self._get_bit_values(row_start, column):
                all_moves = self._find_all_moves(bit_values, row_start, column)
                if len(all_moves) > 0:
                    moves_for_color.append((color, all_moves))
            if len(moves_for_color) > 0:
                yield ((row_start+column), moves_for_color)
                column += self.window_size
            else:
                column += 1

    def _find_all_moves(self, bit_values, row, column):
        all_moves = list()
        for req, moves in self.move_attempts.get_requirements_and_moves():
            if self._meets_requirements(bit_values, req):
                for move in moves:
                    move_from_row, move_from_col = row + move[0], column + move[1]
                    utils.swap_bits(bit_values, self.window_size, move_from_row, move_from_col, move[2])
                    all_moves.append((move_from_row, move_from_col, move[2]))
        return all_moves

    def _get_bit_values(self, row_start, col_start):
        for color in self.sr.number_colors:
            bit_values = list()
            for r, c in utils.row_and_columns(row_start, row_start+self.window_size, col_start, col_start+self.window_size):
                bit_values.append(self.sr.get_color(r, c) == color)
            yield (color, bit_values)

    def _meets_requirements(self, bit_values, requirements):
        for row, col, val in requirements:
            pos = utils.vector_pos(self.window_size, row, col)
            if bit_values[pos] != val:
                return False
        return True
