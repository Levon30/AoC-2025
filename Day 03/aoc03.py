def max_joltage(line, num=2):
    digits = []
    for i in range(num):
        leave = num-1-i
        if leave > 0:
            search = line[:-leave]
        else:
            search = line
        digit = max({int(d) for d in search})
        digits.append(digit)
        line = line[line.find(str(digit))+1:]
        assert len(line) >= leave

    digits = [str(d) for d in digits]
    return int(''.join(digits))

def main():
    with open('input.txt') as f:
        text = f.read()    

    test_input = '''987654321111111
811111111111119
234234234234278
818181911112111'''
    # text = test_input

    total = sum([max_joltage(line, num=12) for line in text.split('\n')])
    print(total)


if __name__ == '__main__':
    main()
