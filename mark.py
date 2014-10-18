from random import shuffle
from heapq import heappop, heappush
from itertools import permutations

import numpy
from matplotlib.image import imsave
from os.path import join

from lib import grey, split, remove, is_windows


class Block:
    def __init__(self, piece):
        self.piece = piece
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None
        self.marked = False
        self.cache = dict()

    def __lt__(self, _):
        return True


class Reference:
    reverse = None
    temp = False

    def __init__(self, x: Block, y: Block):
        self.x, self.y = x, y
        ref = self.__class__
        key = (ref, y)
        if key in x.cache:
            self.value = x.cache[(ref, y)]
        else:
            self.value = self.diff()
            x.cache[key] = self.value

    @classmethod
    def get_attr(cls) -> str:
        return cls.__name__.lower()

    @staticmethod
    def line_compare(a, b) -> float:
        l = a[1: -1]
        return numpy.sum(numpy.minimum(numpy.minimum(
            numpy.fabs(l - b[0: -2]),
            numpy.fabs(l - b[1: -1])),
            numpy.fabs(l - b[2:])))

    @staticmethod
    def get_line(x):
        return x[0]

    @classmethod
    def get(cls, x):
        return getattr(x, cls.get_attr())

    @classmethod
    def set(cls, x, y):
        return setattr(x, cls.get_attr(), y)

    def diff(self):
        a = self.get_line(self.x.piece)
        b = self.reverse.get_line(self.y.piece)
        return self.line_compare(a, b)

    def setup(self):
        self.set(self.x, self.y)
        self.reverse.set(self.y, self.x)
        self.x.marked = True
        self.y.marked = True


class Top(Reference):
    @staticmethod
    def get_line(x):
        return x[0]


class Bottom(Reference):
    @staticmethod
    def get_line(x):
        return x[-1]


class Left(Reference):
    @staticmethod
    def get_line(x):
        return x[..., 0]


class Right(Reference):
    @staticmethod
    def get_line(x):
        return x[..., -1]


def reverse_ref(a, b):
    a.reverse = b
    b.reverse = a


reverse_ref(Top, Bottom)
reverse_ref(Left, Right)


loop0 = (Top, Right, Bottom, Left)
loop1 = (Left, Top, Right, Bottom)
loop2 = (Bottom, Left, Top, Right)
loop3 = (Right, Bottom, Left, Top)
loops = (loop0, loop1, loop2, loop3)


def diff_min(li):
    return min(li, key=lambda x: x.value)


def search(blocks, block, step):
    return diff_min((step(block, i) for i in blocks))


def make_ring(blocks, block, steps):
    ring = []
    for step in steps:
        if step.get(block):
            ref = step(block, step.get(block))
        else:
            ref = search(blocks, block, step)
        block = ref.y
        ring.append(ref)
    return ring


def build_ring(ring):
    for ref in ring:
        ref.setup()


def is_well_rings(rings, center):
    for ring in rings:
        if ring[-1].y is not center:
            return False

    linked = lambda a, b: a[0].y is b[-2].y

    prev = None
    for ring in rings:
        if prev and not linked(prev, ring):
            return False
        prev = ring

    return True


def good_mark(blocks):
    find_blocks = list(blocks.copy())
    shuffle(find_blocks)
    for block in blocks:
        rings = [make_ring(find_blocks, block, loop) for loop in loops]
        if is_well_rings(rings, block):
            print("LOOP RINGS")
            for ring in rings:
                build_ring(ring)
    return blocks


def make_matrix(shape, blocks):
    a, b = shape
    size = a * b

    solutions = set()
    for index in range(size):
        for block in blocks:
            matrix = [None for _ in range(size)]
            open_list = [(block, index)]
            close = set()

            while open_list:
                block, index = open_list.pop()
                if block in close:
                    continue
                close.add(block)
                matrix[index] = block
                i, j = index // b, index % b
                top_block = block.top
                bottom_block = block.bottom
                left_block = block.left
                right_block = block.right
                if top_block and i != 0:
                    open_list.append((top_block, index-b))
                if bottom_block and i + 1 != a:
                    open_list.append((bottom_block, index+b))
                if right_block and j + 1 != b:
                    open_list.append((right_block, index+1))
                if left_block and j != 0:
                    open_list.append((left_block, index-1))
            solutions.add(tuple(matrix))
    maximum = 0
    max_solutions = []

    for solution in solutions:
        num = 0
        for block in solution:
            if block:
                num += 1
        if num > maximum:
            maximum = num
            max_solutions = [solution]
        elif num == maximum:
            max_solutions.append(solution)
    return max_solutions


def matrix_to_image(shape, matrix):
    piece = None
    for block in matrix:
        if block:
            piece = block.piece
    a, b = shape
    m, n = piece.shape
    image = numpy.zeros((m*a, n*b))
    for index, block in enumerate(matrix):
        if block is None:
            continue
        piece = block.piece
        i = index // b
        j = index % b
        image[m*i: m*i+m, n*j: n*j+n] = piece
    return image


def matrix_entropy(shape, matrix):
    a, b = shape
    size = a * b
    length = 0
    entropy = 0
    for index, block in enumerate(matrix):
        if not block:
            continue
        length += 1
        i, j = index // a, index % a
        right_index = index+1
        right_block = matrix[right_index] if right_index < size else None
        bottom_index = index+b
        bottom_block = matrix[bottom_index] if bottom_index < size else None

        if bottom_block and i+1 < a:
            entropy += block.cache[(Bottom, bottom_block)]
        if right_block and j+1 < b:
            entropy += block.cache[(Right, right_block)]
    return entropy / length


def preview(shape, solutions):
    import os
    remove("preview", "*.png")
    for i, solution in enumerate(solutions):
        image = matrix_to_image(shape, solution)
        imsave(os.path.join("preview", "%d.png" % i), image)
    if is_windows:
        os.system("preview\\0.png")


def fill(shape, blocks, solution, vertical=False):
    a, b = shape
    size = a * b
    unmarked = set(set(blocks) - set(solution))
    if not unmarked:
        return solution
    solution = list(solution)
    for _ in range(10):
        for index in range(size):
            i, j = index // b, index % b
            if vertical:
                if i + 1 != a and solution[index] and solution[index+b] is None:
                    solution[index+b] = search(unmarked, solution[index], Bottom).y
                    unmarked.remove(solution[index+b])
                if i != 0 and solution[index] and solution[index-b] is None:
                    solution[index-b] = search(unmarked, solution[index], Top).y
                    unmarked.remove(solution[index-b])
            if j + 1 != b and solution[index] and solution[index+1] is None:
                solution[index+1] = search(unmarked, solution[index], Right).y
                unmarked.remove(solution[index+1])
            if j != 0 and solution[index] and solution[index-1] is None:
                solution[index-1] = search(unmarked, solution[index], Left).y
                unmarked.remove(solution[index-1])
    return solution


def output(shape, blocks, solution):
    solve_map = [solution.index(block) for block in blocks]
    exe_map = [blocks.index(block) for block in solution]

    with open(join("exe", "in.txt"), "w") as exe_input:
        exe_input.writelines("%d %d\n" % shape)
        for i in exe_map:
            exe_input.writelines("%d\n" % i)
    with open("marked.txt", "w") as solve_input:
        for i in solve_map:
            solve_input.writelines("%d\n" % i)


def marker(shape, img):
    image = grey(img)
    pieces = split(shape, image)
    blocks = list(map(Block, pieces))
    good_mark(blocks)
    solutions = []
    while True:
        vertical = input("Vertical? (default NOT):")
        solutions = [fill(shape, blocks, solution, vertical) for solution in make_matrix(shape, blocks)]
        preview(shape, solutions)
        if not input("Redo? (Press any key continue) "):
            break
    if len(solutions) != 1:
        solution = solutions[int(input("Choose a solve (default 0): ") or 0)]
    else:
        solution = solutions[0]
    output(shape, blocks, solution)
    return solution