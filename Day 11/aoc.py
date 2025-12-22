import functools


test_input = '''

aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
ddd: ggg
eee: out
fff: out
ggg: out
hhh: ccc fff iii
iii: out

'''.strip()

test_input_b = '''

svr: aaa bbb
aaa: fft
fft: ccc
bbb: tty
tty: ccc
ccc: ddd eee
ddd: hub
hub: fff
eee: dac
dac: fff
fff: ggg hhh
ggg: out
hhh: out

'''.strip()

test_solution = 5, 2

with open('input.txt') as f:
    puzzle_input = f.read().strip()


def solve(text: str, part_b: bool) -> int:
    if part_b and text.count('\n') < 50:
        text = test_input_b

    def parse_data() -> tuple[dict[int, tuple[int, ...]], dict[str, int]]:
        # If we don't manually include this, this function won't add it
        # since there's no machine connected to the output of out.
        ids = {'out': 0}
        known_ids = 1

        _devices = []
        for line in text.split('\n'):
            source, targets = line.split(': ', 1)
            _devices.append((source, targets.split(' ')))

        for source, _ in _devices:
            if source not in ids:
                ids[source] = known_ids
                known_ids += 1

        known_devices = set(ids.keys())
        output = {}

        for source, targets in _devices:
            this = tuple(ids[target] for target in targets if target in known_devices)
            output[ids[source]] = this

        return output, ids

    devices, device_ids = parse_data()
    you = device_ids['you'] if not part_b else device_ids['svr']
    out = device_ids['out']

    if not part_b:
        def find_path(start) -> int:
            if start == out:
                return 1
            if start not in devices:
                return 0
            return sum(find_path(device) for device in devices[start])
    else:
        dac = device_ids['dac']
        fft = device_ids['fft']

        @functools.cache
        def find_path(start, visited_dac=False, visited_fft=False) -> int:
            if start == out:
                if visited_dac and visited_fft:
                    return 1
                return 0
            if start not in devices:
                return 0
            visited_dac = visited_dac or start == dac
            visited_fft = visited_fft or start == fft
            return sum(find_path(device, visited_dac, visited_fft) for device in devices[start])

    return find_path(start=you)


def main():
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
