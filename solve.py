from copy import deepcopy as copy
from random import shuffle

width = 16
up = (-1, 0)
down = (1, 0)
left = (0, -1)
right = (0, 1)
direction = (up, down, left, right)


class DoNot(Exception):
    pass


class Node:
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data


def get_zero(matrix):
    line_num = len(matrix)
    row_num = len(matrix[0])
    pos = None
    for i in range(line_num):
        for j in range(row_num):
            if matrix[i][j] == 0:
                pos = (i, j)
    return pos


def turn(matrix, shift, pos):
    line_num = len(matrix)
    row_num = len(matrix[0])
    x, y = pos
    a, b = shift
    x2, y2 = x+a, y+b
    if x2 < 0 or x2 >= line_num or y2 < 0 or y2 >= row_num:
        raise DoNot
    matrix = copy(matrix)
    matrix[x][y], matrix[x2][y2] = matrix[x2][y2], matrix[x][y]
    return matrix, (x2, y2)


def valuation(matrix):
    a, b = len(matrix), len(matrix[0])
    value = 0
    for i in range(a):
        for j in range(b):
            num = matrix[i][j]
            x = int(num / a)
            y = int(num % b)
            m = abs(i - x)
            n = abs(j - y)
            value += m*m+n*n
    return float(value)


def order(l):
    num = 0
    prev = l[0]
    for i in range(1, len(l)):
        if l[i] < prev:
            num += 1
            prev = l[i]
    return num


def random_matrix():
    l = list(range(width*width))
    shuffle(l)
    return [[l[i*width+j] for j in range(width)] for i in range(width)]


def to_num(matrix):
    l = [num for line in matrix for num in line]
    base = 1
    result = 0
    for num in l:
        result += base*num
        base *= 10
    return result


def solve(matrix, center=None):
    if center is None:
        center = get_zero(matrix)
    open = [(matrix, center, valuation(matrix))]
    close = []

    while True:
        matrix, center, value = open.pop()
        if matrix in close:
            continue
        if value == 0:
            return matrix
        for shift in direction:
            try:
                new_node, pos = turn(matrix, shift, center)
            except DoNot:
                continue
            open.append((new_node, pos, valuation(new_node)))
        open.sort(key=lambda x: x[2], reverse=True)
        close.append(matrix)


def turn_pipeline(m, lst):
    center = get_zero(m)
    for i in lst:
        try:
            m, center = turn(m, i, center)
        except DoNot:
            pass
    return m, center


def main():
    # print(solve(random_matrix()))
    m = [[i*width+j for j in range(width)] for i in range(width)]
    step = list(direction) * 10
    shuffle(step)
    print('start')
    s = solve(*turn_pipeline(m, step))
    print(s)


if __name__ == '__main__':
    main()
