from __future__ import annotations

from copy import deepcopy
from functools import cached_property
from operator import getitem
from typing import Optional, Iterator

test_input = '''

0:
###
##.
##.

1:
###
##.
.##

2:
.##
###
##.

3:
##.
###
##.

4:
###
#..
###

5:
###
.#.
###

4x4: 0 0 0 0 2 0
12x5: 1 0 1 0 2 2
12x5: 1 0 1 0 3 2

'''.strip()
test_solution = None, None

with open('input.txt') as f:
    puzzle_input = f.read().strip()


class Shape:
    def __init__(self, shape: list[list[bool]], piece_id: int):
        self.shape = shape
        self.id = piece_id

    @classmethod
    def from_lines(cls, lines: list[str], piece_id: int):
        shape = [[c == '#' for c in line] for line in lines]
        return cls(shape, piece_id)

    def flip(self) -> Shape:
        shape = [list(line) for line in list(zip(*self.shape))]
        return Shape(shape, self.id)

    def flip_vertically(self) -> Shape:
        return Shape(list(reversed(self.shape)), self.id)

    def rotate(self) -> Shape:
        return self.flip().flip_vertically()

    def __str__(self):
        lines = []
        for line in self.shape:
            lines.append(''.join(['#' if point else ' ' for point in line]))
        return '\n'.join(lines)

    def __eq__(self, other):
        return self.shape == other.shape


class Piece:
    def __init__(self, lines: list[str], piece_id: int):
        shape = Shape.from_lines(lines, piece_id)
        self.id = piece_id
        self.shapes = [shape]
        for _ in range(4):
            shape = shape.rotate()
            if shape not in self.shapes:
                self.shapes.append(shape)

            flipped = shape.flip()
            if flipped not in self.shapes:
                self.shapes.append(flipped)

    def __str__(self):
        shapes = [str(shape).split('\n') for shape in self.shapes]
        shapes = '\n'.join(['\t\t'.join(line for line in shape) for shape in zip(*shapes)])
        return f'Piece with {len(self.shapes)} shapes:\n{shapes}'

    def __getitem__(self, item):
        return getitem(self.shapes, item)

    @cached_property
    def size(self) -> int:
        shape = self.shapes[0]
        return sum(line.count(True) for line in shape.shape)

    def __iter__(self):
        return iter(self.shapes)


class PresentPlacementError(Exception):
    pass

class OutOfBoundsError(PresentPlacementError):
    pass

class RegionBlockedError(PresentPlacementError):
    pass


class Problem:
    def __init__(self, width: int, height: int,
                 pieces: list[Piece],
                 pieces_left: list[int],
                 region: Optional[list[list[int]]] = None):
        self.width = width
        self.height = height
        self.pieces = pieces

        self.min_piece_size = min(piece.size for piece in pieces)

        # 0 means empty, 1 means filled, -1 means dead space
        if region is not None:
            self.region = region
        else:
            self.region = [[0] * width for _ in range(height)]

        self.empty_space = set()
        for y, line in enumerate(self.region):
            for x, c in enumerate(line):
                if c == 0:
                    self.empty_space.add((x, y))

        self.pieces_left = pieces_left

        # This marks all coordinates where we have decided not to place
        # the piece of the given ID.
        self.blacklist: dict[int, set[tuple[int, int]]] = {piece.id: set() for piece in self.pieces}

    @classmethod
    def from_line(cls, line: str, pieces: list[Piece]) -> Problem:
        dim, s_pieces = line.split(': ', 1)
        x, y = dim.split('x', 1)
        pieces_left = [int(p) for p in s_pieces.split(' ')]
        return cls(int(x), int(y), pieces, pieces_left)

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def __str__(self):
        left = ' '.join(str(p) for p in self.pieces_left)
        top = f'{self.width}x{self.height}; ({left}); {len(self.empty_space)} empty'
        region = '\n'.join([''.join(('x' if c == -1 else str(c) for c in line)) for line in self.region])
        return f'{top}\n{region}'

    def copy(self) -> Problem:
        problem = Problem(self.width, self.height, self.pieces,
                          self.pieces_left.copy(), deepcopy(self.region))
        problem.blacklist = deepcopy(self.blacklist)
        return problem

    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        self.region[y][x] = tile_id
        if (x, y) in self.empty_space:
            self.empty_space.remove((x, y))

    def kill_tile(self, x: int, y: int) -> None:
        self.set_tile(x, y, -1)

    def _check_deadspace(self, x: int, y: int) -> bool:
        if not self._in_bounds(x, y):
            return False
        if self.region[y][x] == -1:
            return True
        region = self.find_enclosed_region(x, y)
        if self._check_dead_region(region):
            return True

        # We now check if there's not enough empty space close to this
        # point, even though the region is large enough.
        # Specifically in the 5x5 area centred around the given point
        # and intersected with region, we check whether there's at
        # least 3 valid x and y variables.

        local = {(x0, y0) for x0, y0 in region if abs(x-x0) <= 2 and abs(y-y0) <= 2}
        xs = set()
        ys = set()
        for x0, y0 in local:
            xs.add(x0)
            ys.add(y0)
        # We could also check for len(local) >= self.min_piece_size
        # but since this is 5 in practice, it makes no difference.
        if len(xs) >= 3 and len(ys) >= 3:
            return False

        # If this failed, the given coordinate is dead.
        # We also check the surrounding tiles for dead space

        for x1, y1 in {(x-1, y), (x+1, y), (x, y-1), (x, y+1)}:
            if (x1, y1) not in region:
                continue
            self.kill_tile(x, y)
            self._check_deadspace(x1, y1)

        return True

    def _check_dead_region(self, region: set[tuple[int, int]]) -> bool:
        if len(region) < self.min_piece_size:
            self._kill_region(region)
            return True
        xs = set()
        ys = set()
        for x, y in region:
            xs.add(x)
            ys.add(y)
        if len(xs) < 3 or len(ys) < 3:
            self._kill_region(region)
            return True
        return False

    def _kill_region(self, region: set[tuple[int, int]]) -> None:
        for x, y in region:
            self.kill_tile(x, y)

    def place(self, shape: Shape, x: int, y: int) -> set[tuple[int, int]]:
        """Returns set of blocked coordinates,
        that inlcudes coordinates of placed points as well as
        newly created dead space."""
        sh = shape.shape
        self.pieces_left[shape.id - 1] -= 1

        # We want to keep track of blocked spaces.
        blocked = set()
        # These are the coordinates that are not directly blocked.
        # We check them for dead space later.
        empty = set()
        for j, line in enumerate(sh):
            for i, c in enumerate(line):
                if not c:
                    empty.add((i, j))
                    continue
                blocked.add((i, j))
                x0, y0 = x+i, y+j
                if not self._in_bounds(x0, y0):
                    raise OutOfBoundsError
                if self.region[y0][x0] != 0:
                    raise RegionBlockedError
                self.set_tile(x0, y0, shape.id)

        for i, j in empty:
            if self._check_deadspace(x+i, y+j):
                blocked.add((i, j))

        for dx in range(-1, 4):
            if dx in {-1, 3}:
                dys = range(-1, 4)
            else:
                dys = {-1, 3}
            for dy in dys:
                self._check_deadspace(x+dx, y+dy)

        return blocked

    def find_enclosed_region(self, x: int, y: int) -> set[tuple[int, int]]:
        """Finds the connected empty region at the given point.
        Returns empty set if given point is not empty."""
        assert self._in_bounds(x, y), f'Point ({x}, {y}) not in bounds'
        region = set()
        if self.region[y][x] == 0:
            self._find_enclosed_region(x, y, region)
        return region

    def _find_enclosed_region(self, x: int, y: int, region: set[tuple[int, int]]) -> None:
        """Mutates region parameter"""
        if len(region) > 100:
            return
        if not self._in_bounds(x, y):
            return
        if self.region[y][x] != 0 or (x, y) in region:
            return
        region.add((x, y))
        self._find_enclosed_region(x-1, y, region)
        self._find_enclosed_region(x+1, y, region)
        self._find_enclosed_region(x, y-1, region)
        self._find_enclosed_region(x, y+1, region)

    def get_required_space(self) -> int:
        total = 0
        for piece, left in zip(self.pieces, self.pieces_left):
            total += left * piece.size
        return total

    def cheese(self) -> bool:
        squares = self.width // 3 * self.height // 3
        return sum(self.pieces_left) <= squares

    def solve(self) -> bool:
        if self.cheese():
            return True
        return self._solve()

    def _solve(self, depth: int = 0) -> bool:
        for piece, c in zip(self.pieces, self.pieces_left, strict=True):
            if c == 0:
                continue
            break
        else:
            return True

        if len(self.empty_space) < self.get_required_space():
            return False

        for x, y in self.empty_space:

            if (x, y) in self.blacklist[piece.id]:
                continue

            if depth == 0:
                # Due to symmetry, we may place the first piece
                # in the top left quadrant.
                if x > self.width//2 or y > self.height//2:
                    continue

            problems: list[tuple[Problem, set[tuple[int, int]]]] = []
            for shape in piece:
                copied = self.copy()
                try:
                    blocked = copied.place(shape, x, y)
                except PresentPlacementError:
                    pass
                else:
                    problems.append((copied, blocked))

            self.blacklist[piece.id].add((x, y))

            # Some problems are worse than others.
            # If we have block the same squares or more,
            # then we can disregard a given problem
            filtered_problems = []
            for i, (p1, b1) in enumerate(problems):
                for j, (p2, b2) in enumerate(problems):
                    if i == j:
                        continue
                    # This only filters out strict supersets.
                    if b1.issuperset(b2) and b1 != b2:
                        break
                else:
                    # Now filtered problems might still contain problems with
                    # equal sets of blocked tiles
                    if any(b1 == bi for pi, bi in filtered_problems):
                        continue
                    filtered_problems.append((p1, b1))

            assert not problems or filtered_problems, str(len(problems)) + ' / ' + str(len(filtered_problems))

            if problems:
                print()
                print(filtered_problems[0][0])

            if any(p._solve() for p, _ in filtered_problems):
                return True

        return False

def solve(text: str, part_b: bool) -> int:
    pieces: list[Piece] = []

    def read_input() -> Iterator[Problem]:
        *s_pieces, s_problems = text.split('\n\n')
        for i, s_piece in enumerate(s_pieces):
            pieces.append(Piece(s_piece.split('\n')[1:], piece_id=i+1))
        return (Problem.from_line(p, pieces) for p in s_problems.split('\n'))
        # for p in s_problems.split('\n'):
        #     problems.append(Problem.from_line(p, pieces))

    problems = read_input()
    total = 0
    for problem in problems:
        total += problem.solve()

    return total


def main():
    print(solve(test_input, False))

def main2():
    if test_solution[0] is not None:
        out = solve(test_input, False)
        assert out == test_solution[0], f'Got: {out}, Expected: {test_solution[0]}'
        print('Test A passed!')
    if test_solution[1] is not None:
        out = solve(test_input, True)
        assert out == test_solution[1], f'Got: {out}, Expected: {test_solution[1]}'
        print('Test B passed!')

    print('A:', solve(puzzle_input, False))
    print('B:', solve(puzzle_input, True))

if __name__ == '__main__':
    main()
