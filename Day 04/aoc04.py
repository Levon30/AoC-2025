
def main():
    with open('input.txt') as f:
        text = f.read()    

    test_input = '''..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.'''
    # text = test_input

    lines = [list(line) for line in text.split('\n')]
    height = len(lines)
    width = len(lines[0])
    # assert all(len(line) == width for line in lines)

    def check(x, y):
        if x < 0 or y < 0 or x >= width or y >= height:
            return False
        return lines[y][x] == '@'

    def accessible(x, y):
        hit = 0
        miss = 0
        for a in range(-1, 2):
            for b in range(-1, 2):
                if a == b == 0:
                    continue
                if check(x+a, y+b):
                    hit += 1
                else:
                    miss += 1
                if hit >= 4:
                    return False
                if miss >= 5:
                    return True
        assert False

    total = 0
    last_total = 0
    while True:
        last_total = total
        for y, line in enumerate(lines):
            for x, sym in enumerate(line):
                if sym != '@':
                    continue
                if accessible(x, y):
                    total += 1
                    lines[y][x] = '.'
        if total == last_total:
            break
    print(total)
                


if __name__ == '__main__':
    main()
