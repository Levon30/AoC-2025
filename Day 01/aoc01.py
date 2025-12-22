intervals = []
numbers = []
sorted_intervals = []


class Dial:
    def __init__(self):
        self.value = 50
        self.password = 0

    def read(self, text):
        direction, num = text[0], text[1:]
        num = int(num)
        if direction == 'L':
            num = -num

        self.value = (self.value + num) % 100
        if self.value == 0:
            self.password += 1

    def read_b(self, text):

        direction, num = text[0], text[1:]
        num = int(num)

        hun, num = divmod(num, 100)
        self.password += hun

        if num == 0:
            return

        if direction == 'L':
            if self.value > 0 and num >= self.value:
                self.password += 1
            self.value = self.value - num
            if self.value < 0:
                self.value += 100
        else:
            self.value += num
            if self.value >= 100:
                self.value -= 100
                self.password += 1
        assert 0 <= self.value < 100

        

def main():
    with open('input.txt') as f:
        text = f.read()

    test_input = '''L68
L30
R48
L5
R60
L55
L1
L99
R14
L82'''
    # text = test_input

    dial = Dial()
    for line in text.split('\n'):
        dial.read_b(line)
    print(dial.password)

if __name__ == '__main__':
    main()
