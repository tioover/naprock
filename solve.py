from heapq import heappop, heappush


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


def solve_with_node(node: Node, max_loop=0x50, close=None):
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
        yield solve_with_node(Node(node, node.matrix, i, 'select '+str(i)))


def make_root_node(matrix, shape):
    return Node(None, matrix, 0, '', shape, 0)


def solve(matrix, shape):
    node = make_root_node(matrix, shape)
    for i in range(128):
        print(i, node.center, node.value)
        for new_solve in solve_generator(node):
            value = new_solve.value
            if value == 0:
                return new_solve
            elif new_solve.value < node.value:
                node = new_solve
    return node


def main():
    import sys
    shape = tuple(map(int, sys.argv[1:3]))
    x, y = shape
    matrix = tuple(map(int, sys.argv[3:3+x*y]))
    solve(matrix, shape)


if __name__ == '__main__':
    main()
