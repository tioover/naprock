from heapq import heappop, heappush


class Node:
    def __init__(self, parent, matrix, center, step, shape=None, depth=None):
        self.shape = parent.shape if parent else shape
        self.parent = parent
        self.matrix = matrix
        self.center = center
        self.step = step
        self.depth = parent.depth + 1 if parent else depth
        self.matrix_distance = self.valuation()
        self.value = sum(self.matrix_distance)

    def valuation(self):
        m = self.matrix
        x, y = self.shape
        return tuple(
            (abs(int(i/y) - int(m[i]/y)) + abs((i % y) - (m[i] % y)) for i in range(len(m))))

    def __lt__(self, other):
        return True  # for heap

    def __repr__(self):
        x, y = self.shape
        m = self.matrix
        result = ''
        for i in range(x):
            result += str(m[i*y: (i+1)*y]) + '\n'
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
    matrix = list(node.matrix)

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
        m = matrix[:]
        m[shift], m[center] = m[center], m[shift]
        yield Node(node, tuple(m), shift, (name, node.step))


def solve_with_node(node: Node, max_loop=0x1000, close=None):
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
        if node.value < solve_node.value:
            solve_node = node
        if node.matrix in close:
            if node.depth > close[node.matrix].depth:
                close[node.matrix] = node
            continue
        elif node.value == 0:
            solve_node = node
            break
        else:
            close[node.matrix] = node
        for new_node in node_generator(node):
            open.push(new_node)
    return solve_node  # fail


def make_root_node(matrix, shape):
    return Node(None, matrix, 0, (), shape, 0)


def solve(matrix, shape):
    node = make_root_node(matrix, shape)
    return solve_with_node(node)


def main():
    import sys
    shape = tuple(map(int, sys.argv[1:3]))
    x, y = shape
    matrix = tuple(map(int, sys.argv[3:3+x*y]))
    solve(matrix, shape)


if __name__ == '__main__':
    main()
