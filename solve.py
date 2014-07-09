#!/bin/env pypy3
from heapq import heappop, heappush
from copy import copy
from time import time


class Node:
    def __init__(self, parent, matrix, center, step, shape=None, depth=None):
        self.shape = parent.shape if parent else shape
        self.parent = parent
        self.matrix = matrix
        self.center = center
        self.step = step
        self.depth = parent.depth + 1 if parent else depth
        self.value = self.valuation()

    def valuation(self):
        m = self.matrix
        x, y = self.shape
        result = 0
        for i in range(x*y):
            result += abs(int(i/y) - int(m[i]/y)) + abs((i % y) - (m[i] % y))
        return result

    def __lt__(self, other):
        return self.depth < other.depth  # for heap

    def __repr__(self):
        x, y = self.shape
        m = self.matrix
        result = ''
        for i in range(x):
            result += '|'.join(('%3d' % i for i in m[i*y: (i+1)*y])) + '\n'
        return result


class Heap:
    def __init__(self):
        self.heap = []

    def push(self, node):
        heappush(self.heap, (node.value, node))

    def pop(self):
        return heappop(self.heap)[1]


def node_generator(node: Node):
    center = node.center
    line, row = node.shape
    matrix = node.matrix

    shift_list = []
    up = center - row
    down = center + row
    left = center - 1
    right = center + 1

    if right % row != 0:
        shift_list.append((right, 'r'))
    if center % row != 0:
        shift_list.append((left, 'l'))
    if up >= 0:
        shift_list.append((up, 'u'))
    if down < len(matrix):
        shift_list.append((down, 'd'))

    for shift, name in shift_list:
        m = list(matrix)
        m[shift], m[center] = m[center], m[shift]
        yield Node(node, tuple(m), shift, name)


def solve_with_node(node: Node, max_loop=0x500, close=None):
    open = Heap()
    close = close or {}
    open.push(node)
    solve_node = node
    i = 0

    while i < max_loop:
        i += 1
        try:
            node = open.pop()
        except IndexError:
            break
        if node.value == 0:
            solve_node = node
            break
        elif node.matrix in close:
            if node.depth > close[node.matrix].depth:
                close[node.matrix] = node
            continue
        else:
            close[node.matrix] = node
        if node.value < solve_node.value:
            solve_node = node
        for new_node in node_generator(node):
            open.push(new_node)
    return solve_node


def solve_generator(node: Node):
    for i in range(len(node.matrix)):
        now = node
        if i != node.center:
            now = copy(node)
            now.center = i
            now.step = 'select '+str(i)
            now.parent = node
        yield solve_with_node(now)


def goal_reduce(matrix, goal):
    new = [None for i in range(len(matrix))]
    for i, num in enumerate(goal):
        pos = matrix.index(num)
        new[pos] = i
    return tuple(new)


def make_root_node(matrix, shape, goal):
    if goal:
        matrix = goal_reduce(matrix, goal)
    return Node(None, matrix, 0, '', shape, 0)


def solve(matrix, shape, goal):
    node = make_root_node(matrix, shape, goal)
    t = time()
    i = 0
    for i in range(16):
        print(i, node.center, node.value)
        for new_solve in solve_generator(node):
            value = new_solve.value
            if value == 0:
                return new_solve
            elif new_solve.value < node.value:
                node = new_solve
    t = time() - t
    print(t, t/i)
    return node


def main():
    import sys
    l = sys.argv[1:3]
    shape = tuple(map(int, l))
    x, y = shape
    l = sys.argv[3:]
    l = l[:x*y]
    matrix = tuple(map(int, l))
    l = l[:x*y]
    goal = tuple(map(int, l)) or None
    assert not goal or len(goal) == x*y
    solve(matrix, shape, goal)


if __name__ == '__main__':
    main()
