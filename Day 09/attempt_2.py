from __future__ import annotations

import itertools
from typing import Optional


class Edge:
    def __init__(self, p, q):
        self.p = p
        self.q = q
        self.horizontal = p[1] == q[1]
        self.vertical = not self.horizontal

        if self.horizontal:
            self.sign = self.p[0] < self.q[0]
        else:
            self.sign = self.p[1] < self.q[1]

        self.clockwise = None

    def contains(self, x: Optional[int], y: Optional[int]) -> bool:
        """Checks whether the point (x, y) is contained on this edge.
        If self.horizontal, y may be None.
        If self.vertical, x may be None."""
        if self.vertical:
            if x is not None and x != self.p[0]:
                return False
            limits = [self.p[1], self.q[1]]
            check = y
        else:
            if y is not None and y != self.p[1]:
                return False
            limits = [self.p[0], self.q[0]]
            check = x

        a, b = min(limits), max(limits)
        return a <= check <= b

    def __str__(self):
        return str((self.p, self.q))

    def __repr__(self):
        return str(self)


def solve(text: str, part_a: bool):

    coordinates = []
    for line in text.split('\n'):
        x, y = line.split(',')
        coordinates.append([int(x), int(y)])

    if part_a:
        return solve_a(coordinates)
    return solve_b(coordinates)


def solve_a(coordinates: list[list[int]]) -> int:
    distances = set()
    for (x, y), (u, v) in itertools.combinations(coordinates, 2):
        d = (x - u + 1) * (y - v + 1)
        if d < 0:
            d *= -1
        distances.add(d)

    return max(distances)


def solve_b(coordinates: list[list[int]]) -> int:

    polygon_coordinates = [c.copy() for c in coordinates]

    num = len(coordinates)
    edges: list[Edge] = []
    horizontals = []
    verticals = []

    def parse_edges():
        # Populates the edges list.
        # Also checks which edges are clockwise and counterclockwise
        # (that means, the edge after that goes clockwise)

        previous = Edge(polygon_coordinates[0], polygon_coordinates[1])
        edges.append(previous)
        for i, p in enumerate(polygon_coordinates[1:]):
            if i == num-2:
                j = 0
            else:
                j = i+2
            q = polygon_coordinates[j]
            edge = Edge(p, q)
            edges.append(edge)
            previous.clockwise = previous.vertical ^ (previous.sign ^ edge.sign)
            previous = edge

        edges[-1].clockwise = edges[-1].vertical ^ (edges[-1].sign ^ edges[0].sign)

        for edge in edges:
            if edge.vertical:
                verticals.append(edge)
                continue
            horizontals.append(edge)

    parse_edges()

    cw = sum(1 for edge in edges if edge.clockwise)
    clockwise = cw > num // 2
    assert abs(2*cw - num) == 4
    # If clockwise is True, more edges go cw than ccw,
    # so the interior is to the right side of all edges

    # We now bloat the polygon and move all corners by (.1, .1) to
    # make the square containment check easier.

    inc_x = inc_y = None
    edge = edges[0]
    if edge.vertical:
        inc_x = edge.sign ^ clockwise
    else:
        inc_y = not edge.sign ^ clockwise

    for edge in edges:
        if edge.vertical:
            inc_y = edge.sign ^ edge.clockwise ^ clockwise
        else:
            inc_x = edge.sign ^ edge.clockwise ^ clockwise
        edge.q[0] += 0.1 * (1 if inc_x else -1)
        edge.q[1] += 0.1 * (1 if inc_y else -1)

    # For a given point, we now store the maximal
    # horizontal and vertical line segment passing through the point
    # that is contained in the polygon.

    # {(x, y): ((x_min, x_max), (y_min, y_max))}
    cache_type = tuple[tuple[int, int], tuple[int, int]]
    cache: dict[tuple[int, int], cache_type] = {}

    def check_point(point: tuple[int, int]) -> cache_type:
        x, y = point
        left = 0
        right = float('inf')
        for edge in verticals:
            if not edge.contains(None, y):
                continue
            if edge.p[0] > x:
                right = min(right, edge.p[0])
                continue
            left = max(left, edge.p[0])

        up = float('inf')
        down = 0
        for edge in horizontals:
            if not edge.contains(x, None):
                continue
            if edge.p[1] > y:
                up = min(up, edge.p[1])
                continue
            down = max(down, edge.p[1])

        cache[(x, y)] = ((left, right), (down, up))
        return cache[(x, y)]

    def rectangle_contained(p, q):
        # Rectangle is contained iff all points on the boundary are contained.

        if p not in cache:
            check_point(p)
        if q not in cache:
            check_point(q)

        x0, y0 = p
        x1, y1 = q
        x0, x1 = sorted([x0, x1])
        y0, y1 = sorted([y0, y1])

        (x_min, x_max), (y_min, y_max) = cache[p]
        if not (x_min < x0 and x1 < x_max):
            return False
        if not (y_min < y0 and y1 < y_max):
            return False

        (x_min, x_max), (y_min, y_max) = cache[q]
        if not (x_min < x0 and x1 < x_max):
            return False
        if not (y_min < y0 and y1 < y_max):
            return False

        return True

    # print(point_contained(4, 2))
    # u, v, w, x = (5600, 67661), (94601, 67661), (94601, 50063), (5600, 50063)
    # print(rectangle_contained(u, w))
    # print(point_contained(5601, 50063))
    # exit()

    # noinspection PyUnusedLocal
    def get_max_area() -> int:
        distance = 0
        for (x, y), (u, v) in itertools.combinations(coordinates, 2):
            dx = abs(x-u)
            dy = abs(y-v)
            d = (dx+1) * (dy+1)
            if d <= distance:
                continue
            if rectangle_contained((x, y), (u, v)):
                distance = d
                # print((x,y), (u,v))
        return distance

    # Idea: We want to generate over all tuples (i, j) where i and j
    # correspond to the i-th and j-th coordinates.
    # Instead of using itertools.combinations, we just
    # naively start with i=0 and find the j which maximises the area,
    # then we set the next i to this optimal j and so on.

    # noinspection PyUnusedLocal
    def get_max_area_2() -> int:
        seen = set()

        distance = 0
        least_i = 0
        next_i = None

        while True:

            while least_i in seen:
                least_i += 1
            if least_i == num:
                break

            i = next_i if next_i is not None else least_i
            next_i = None
            seen.add(i)

            for j in range(num):
                if j in seen:
                    continue

                x, y = coordinates[i]
                u, v = coordinates[j]
                dx = abs(x - u)
                dy = abs(y - v)
                d = (dx + 1) * (dy + 1)

                if d <= distance:
                    continue

                if rectangle_contained((x, y), (u, v)):
                    distance = d
                    if j not in seen:
                        next_i = j

        return distance

    return get_max_area_2()


def run(title: str, filename: str, part_a: bool, expected: int | None) -> None:
    with open(filename, 'r') as f:
        text = f.read().strip()

    got = solve(text, part_a)
    if expected is not None:
        assert got == expected, f'{title}; Got: {got}, Expected: {expected}'
        return
    print(f'{title}: {got}')


def main():
    import time

    test_solutions = 50, 24
    solutions = 4733727792, 1566346198

    t_start = time.perf_counter()

    run('Test A', 'test_input.txt', True, test_solutions[0])
    run('Test B', 'test_input.txt', False, test_solutions[1])

    run('Problem A', 'input.txt', True, solutions[0])
    run('Problem B', 'input.txt', False, solutions[1])

    delay = time.perf_counter() - t_start
    print(f'All problems passed in {delay:.04f}s.')


if __name__ == '__main__':
    main()
