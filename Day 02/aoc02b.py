def is_invalid(num):
    # print(f'CHECK {num}')
    length = len(num)
    lengths = []
    for seg_length in range(1, length):
        if length % seg_length == 0:
            lengths.append(seg_length)
    return any((is_invalid_with_segment_length(i, num) for i in lengths))


def is_invalid_with_segment_length(seg_length, num):
    repeat = num[:seg_length]
    return num == repeat * (len(num) // seg_length)


def find_invalid(a, b):
    return [num for num in range(a, b+1) if is_invalid(str(num))]


def main():
    with open('input.txt') as f:
        text = f.read()

    test_input = '''11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124'''
    # text = test_input

    total = 0
    for line in text.split(','):
        a, b = line.split('-')
        inv = find_invalid(int(a), int(b))
        # print(inv)
        total += sum(inv)
    print(total)


if __name__ == '__main__':
    import time
    s = time.perf_counter()
    main()
    print(s-time.perf_counter())
