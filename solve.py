import time
import heapq
import solve_old
from copy import deepcopy as copy
from random import shuffle

height = 4
width = height
up = (-1, 0)
down = (1, 0)
left = (0, -1)
right = (0, 1)
direction = (up, down, left, right)


class DoNot(Exception):
    pass


def turn(matrix, shift, pos, new=True):
    line_num = height
    row_num = width
    x, y = pos
    a, b = shift
    x2, y2 = x+a, y+b
    if x2 < 0 or x2 >= line_num or y2 < 0 or y2 >= row_num:
        raise DoNot
    if new:
        matrix = copy(matrix)
    matrix[x][y], matrix[x2][y2] = matrix[x2][y2], matrix[x][y]
    return matrix, (x2, y2)


def reverse(shift):
    a, b = shift
    return -a, -b


def select(matrix):
    min_ = float('inf')
    pos = None
    for i in range(height):
        for j in range(width):
            for shift in direction:
                try:
                    m, center = turn(matrix, shift, (i, j), False)
                except DoNot:
                    continue
                value = valuation(m)
                if value < min_:
                    min_ = value
                    pos = (i, j)
                turn(m, reverse(shift), center, False)
    return min_, pos


def valuation(matrix):
    value = 0
    for i in range(height):
        for j in range(width):
            num = matrix[i][j]
            x = int(num / height)
            y = int(num % width)
            m = abs(i - x)
            n = abs(j - y)
            value += m+n  # 曼哈顿距离
    return float(value)


def solve(matrix):
    center = select(matrix)[1]
    open = []
    push = lambda x: heapq.heappush(open, x)
    pop = lambda: heapq.heappop(open)
    push((valuation(matrix), matrix, center))
    close = []

    while True:
        value, matrix, center = pop()
        # print(value, matrix)
        if matrix in close:
            continue
        elif value == 0:
            return matrix
        else:
            close.append(matrix)
        for shift in direction:
            try:
                new_node, pos = turn(matrix, shift, center)
            except DoNot:
                continue
            push((valuation(new_node), new_node, pos))
        value, pos = select(matrix)
        push((value, matrix, pos))


def turn_pipeline(m, lst):
    center = select(m)[1]
    for i in lst:
        try:
            m, center = turn(m, i, center)
        except DoNot:
            pass
    return m


def main():
    # print(solve(random_matrix()))
    m = [[i*width+j for j in range(width)] for i in range(width)]
    step = list(direction) * 10
    shuffle(step)
    m = turn_pipeline(m, step)
    print(m)
    print('old')
    t = time.time()
    solve_old.solve(m)
    print(time.time() - t)
    print('new')
    t = time.time()
    solve(m)
    print(time.time() - t)


if __name__ == '__main__':
    main()
