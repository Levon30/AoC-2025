import matplotlib.pyplot as plt

with open('input.txt') as f:
    lines = f.readlines()

coordinates = []
for line in lines:
    x, y = line.split(',')
    coordinates.append((int(x), int(y)))

x, y = zip(*coordinates)
plt.plot(x, y, color='blue', marker='o', linestyle='-', markersize=6)

plt.title('Advent of Code')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()
