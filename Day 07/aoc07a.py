
def main():
    with open('input.txt') as f:
        text = f.read()
        assert '^^' not in text
        assert '\n^' not in text
        assert '^\n' not in text

    test_input = '''.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
...............'''

    # text = test_input
    lines = text.split('\n')

    part_b = True

    hits = 0
    beams = set()

    beams.add(lines[0].find('S'))
    for line in lines[1:]:
        splitters = {i for i, c in enumerate(line) if c == '^'}
        for splitter in splitters:
            if splitter in beams:
                beams.remove(splitter)
                beams.add(splitter-1)
                beams.add(splitter+1)
                hits += 1
    print(hits)


if __name__ == '__main__':
    main()
