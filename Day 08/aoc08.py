
def main():
    with open('input.txt') as f:
        text = f.read()

    test_input = '''\
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689
'''.strip()

    # text = test_input
    assert test_input
    part_b = False
    lines = text.split('\n')
    num_boxes = len(lines)

    coords = []
    def parse_coords():
        for line in lines:
            x, y, z = line.split(',', 2)
            x = int(x)
            y = int(y)
            z = int(z)
            coords.append((x, y, z))
    parse_coords()

    def get_all_distances():
        dist = []
        for i, (x, y, z) in enumerate(coords):
            for j, (u, v, w) in enumerate(coords[i + 1:]):
                val = (i, i + j + 1), (x - u) ** 2 + (y - v) ** 2 + (z - w) ** 2
                dist.append(val)

        return dist
    distances = get_all_distances()
    distances.sort(key=lambda x: x[1])

    def connect(i, j):
        if circuits[i] is circuits[j]:
            return
        new = circuits[i].union(circuits[j])
        for k in new:
            circuits[k] = new

    circuits = {i: {i} for i in range(num_boxes)}

    def solve_a():
        num_connections = 1000
        for (i, j), distance in distances[:num_connections]:
            connect(i, j)

        out = []
        for circuit in circuits.values():
            if circuit in out:
                continue
            out.append(circuit)

        lens = [len(circuit) for circuit in out]
        lens.sort(reverse=True)
        prod = 1
        for factor in lens[:3]:
            prod *= factor
        return prod

    def solve_b():
        for num, ((i, j), distance) in enumerate(distances):
            connect(i, j)
            if len(circuits[0]) == num_boxes:
                break
        else:
            raise

        return coords[i][0] * coords[j][0]

    if part_b:
        return solve_b()
    return solve_a()

if __name__ == '__main__':
    print(main())
