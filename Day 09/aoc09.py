import time

test_input = '''7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3'''


def main():
    with open('input.txt') as f:
        text = f.read()

    # text = test_input
    lines = text.split('\n')
    lines = (line.split(',') for line in lines)
    coordinates = [(int(x), int(y)) for x, y in lines]

    print(part_b(coordinates))


class Edge:
    def __init__(self, p, q):
        self.p = p
        self.q = q
        self.horizontal = p[1] == q[1]
        self.vertical = not self.horizontal

    def contains(self, x, y):
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


def part_b(coordinates):
    num = len(coordinates)
    edges = []

    def parse_edges():
        for i, p in enumerate(coordinates):
            if i == num-1:
                j = 0
            else:
                j = i+1
            q = coordinates[j]
            edges.append(Edge(p, q))

    parse_edges()

    # All edges are directed. The interior is either to the left or the right
    # of any edge vector.
    # To figure out which, choose any point on the boundary.
    # Find all horizontal edges that pass through the same x coordinate

    # x = edges[0].p[0]
    # slices = [edge for edge in edges if edge.horizontal and edge.contains(x, None)]
    # upper = min(slices, key=lambda e: e.p[1])

    # We see that upper.p[0] < upper.q[0],
    # therefore the interior is towards the left side of ALL edges

    # ---o---

    bounds = {}
    def get_bounds(p):
        x, y = p
        if p in bounds:
            return bounds[p]

        ys = [edge.p[1] for edge in edges if edge.horizontal and edge.contains(x, None)]
        xs = [edge.p[0] for edge in edges if edge.vertical and edge.contains(None, y)]
        ret = bounds[p] = (min(xs), max(xs), min(ys), max(ys))
        return ret

    def rectangle_contained(p, q):
        # Rectangle is contained iff all points on the boundary are contained.

        x0, y0 = p
        x1, y1 = q

        # We first check the opposite corners efficiently using the bounds.
        xmin, xmax, ymin, ymax = get_bounds(p)
        if not ymin <= y1 <= ymax:
            return False
        if not xmin <= x1 <= xmax:
            return False

        x0, x1 = sorted([x0, x1])
        y0, y1 = sorted([y0, y1])

        # Now we check if we overlap with the non-box in the middle
        if x0 < 94601 and not (y0 >= 50063 or y1 <= 48706):
            return False

        x_range = range(x0+1, x1)
        y_range = range(y0+1, y1)

        def _check():
            yield all(point_contained(*point) for point in [(x0, y1), (x1, y0)])
            yield all(point_contained(x0, y) for y in y_range)
            yield all(point_contained(x, y0) for x in x_range)
            yield all(point_contained(x1, y) for y in y_range)
            yield all(point_contained(x, y1) for x in x_range)
        return all(_check())

    points: set[tuple[int, int]] = set()

    def populate_points():
        for edge in edges:
            if edge.horizontal:
                x0, x1 = sorted([edge.p[0], edge.q[0]])
                for x in range(x0, x1+1):
                    points.add((x, edge.p[1]))
                continue
            y0, y1 = sorted([edge.p[1], edge.q[1]])
            for y in range(y0, y1+1):
                points.add((edge.p[0], y))
    populate_points()

    def point_contained(x, y):
        if (x, y) in points:
            return True
        return _point_contained(x, y)

    def _point_contained(x, y):
        # Find the largest horizontal edge above the point
        slices = [edge for edge in edges if edge.horizontal and edge.contains(x, None)]

        upper_slices = []
        lower_slices = []

        for edge in slices:
            if edge.p[1] == y:
                upper_slices.append(edge)
                lower_slices.append(edge)
                break
            if edge.p[1] > y:
                upper_slices.append(edge)
                continue
            lower_slices.append(edge)

        if not upper_slices:
            return False

        # We now find the closest upper and lower edge (which sandwich the given point)
        # All points in between are contained
        upper = min(upper_slices, key=lambda e: e.p[1])
        if upper.p[1] != y and upper.p[0] < upper.q[0]:
            return False
        lower = max(lower_slices, key=lambda e: e.p[1])

        for _y in range(lower.p[1], upper.p[1]+1):
            points.add((x, _y))

        # Same for left-right
        slices = [edge for edge in edges if edge.vertical and edge.contains(None, y)]

        upper_slices = []
        lower_slices = []

        for edge in slices:
            if edge.p[0] == x:
                upper_slices.append(edge)
                lower_slices.append(edge)
                break
            if edge.p[0] > x:
                upper_slices.append(edge)
                continue
            lower_slices.append(edge)

        if not upper_slices:
            return False

        upper = min(upper_slices, key=lambda e: e.p[0])
        if upper.p[0] != x and upper.p[1] > upper.q[1]:
            return False
        lower = max(lower_slices, key=lambda e: e.p[0])

        for _x in range(lower.p[0], upper.p[0]+1):
            points.add((_x, y))

        return True

    # a, b, c, d = (5600, 67661), (94601, 67661), (94601, 50063), (5600, 50063)
    # print(rectangle_contained(a, c))
    # print(point_contained(5601, 50063))
    # exit()

    def get_max_area() -> int:
        distance = 0
        print(len(coordinates))
        for i, (x, y) in enumerate(coordinates):
            print(i, distance)
            for j, (u, v) in enumerate(coordinates[i+1:]):
                # print(i, i+j+1)
                dx = abs(x-u)
                dy = abs(y-v)
                d = (dx+1) * (dy+1)
                if d <= distance:
                    continue
                if rectangle_contained((x, y), (u, v)):
                    distance = d
                    print(i, j)
                    print((x,y), (u,v))
        return distance

    return get_max_area()

def part_a(coordinates):
    distances = set()
    for i, (x, y) in enumerate(coordinates):
        for (u, v) in coordinates[i+1:]:
            d = (x-u+1) * (y-v+1)
            if d < 0:
                d *= -1
            distances.add(d)

    return max(distances)

if __name__ == '__main__':
    import time
    start = time.perf_counter()
    main()
    print(time.perf_counter() - start)
