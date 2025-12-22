def find_invalid(a, b):
    invalids = []

    sep = len(a)//2
    start = int(a[:sep])
    stop = int(b[:sep])
    ia = int(a)
    ib = int(b)

    for num in range(start, stop+1):
        candidate = int(str(num)*2)

        if ia <= candidate <= ib:
            invalids.append(candidate)
    return invalids


def main():
    with open('input.txt') as f:
        text = f.read()

    test_input = '''11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124'''
    # text = test_input

    total = 0
    for line in text.split(','):
        a, b = line.split('-')
        if len(a) < len(b):
            if len(a) % 2 == 1:
                a = '1' + len(a) * '0'
            else:
                b = '9' * len(a)

        assert len(a) == len(b)
        if len(a) % 2 == 1:
            continue

        total += sum(find_invalid(a, b))
    print(total)


if __name__ == '__main__':
    import time
    s = time.perf_counter()
    main()
    print(time.perf_counter()-s)
