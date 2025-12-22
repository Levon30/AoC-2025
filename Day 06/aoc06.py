
def main():
    with open('input.txt') as f:
        text = f.read()    

    test_input = '''123 328  51 64 
 45 64  387 23 
  6 98  215 314
*   +   *   +  '''
    # text = test_input

    part_b = True

    if part_b:
        lines = text.split('\n')
        lines, ops = lines[:-1], lines[-1]
        ops = [op for op in ops if op != ' ']

        lines = [list(line) for line in text.split('\n')[:-1]]
        lines = list(zip(*lines))
        nums = [''.join(line) for line in lines]
        nums = [num.strip() for num in nums]
        nums = [int(num) if num else None for num in nums]

        problems = []
        this = []
        for num in nums:
            if num is None:
                assert this
                problems.append(this)
                this = []
                continue
            this.append(num)
        if this:
            problems.append(this)

    else:
        lines = []
        text_lines = text.split('\n')
        for line in text_lines[:-1]:
            nums = [int(num) for num in line.split()]
            lines.append(nums)
        ops = text_lines[-1].split()
        problems = list(zip(*lines))

    total = 0
    for nums, op in zip(problems, ops, strict=True):
        if op == '+':
            total += sum(nums)
            continue
        assert op == '*'
        prod = 1
        for num in nums:
            prod *= num
        total += prod

    print(total)


if __name__ == '__main__':
    main()
