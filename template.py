def solve(text: str, part_a: bool) -> int:
    pass


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

    test_solutions = None, None
    solutions = None, None

    t_start = time.perf_counter()

    run('Test A', 'test_input.txt', True, test_solutions[0])
    run('Test B', 'test_input.txt', False, test_solutions[1])

    run('Problem A', 'input.txt', True, solutions[0])
    run('Problem B', 'input.txt', False, solutions[1])

    delay = time.perf_counter() - t_start
    print(f'All problems passed in {delay:.04f}s.')


if __name__ == '__main__':
    main()
