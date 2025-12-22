intervals = []
numbers = []
sorted_intervals = []


def read():
    with open('input.txt') as f:
        text = f.read()

    test_input = '''3-5
10-14
16-20
12-18

1
'''
    # text = test_input

    s_interval, s_numbers = text.split('\n\n', 1)

    for line in s_interval.split('\n'):
        a, b = line.split('-', 1)
        intervals.append((int(a), int(b)))

    for line in s_numbers.split('\n')[:-1]:
        numbers.append(int(line))


def solve():
    total = 0
    for number in numbers:
        for a, b in intervals:
            if a <= number <= b:
                total += 1
                break
    return total


def sort_intervals():
    intervals.sort(key=lambda interval: interval[0])


def solve_b():
    sort_intervals()
    total = 0
    last = -1
    for a, b in intervals:
        if last >= b:
            continue
        if last >= a:
            a = last+1
        total += b-a+1
        last = b
    return total


def main():
    read()
    # print('\n'.join([str(i) for i in intervals]))
    print(solve_b())


if __name__ == '__main__':
    main()
