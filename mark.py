#!/usr/bin/env python3
import numpy as np
import matplotlib.image as mpimg
from random import shuffle
from lib import gray, split
import matplotlib.cm as cm


class Block:
    def __init__(self, piece):
        self.piece = piece
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None
        self.marked = False
        self.cache = dict()


class Reference:
    reverse = None

    def __new__(cls, x: Block, y: Block):
        if (cls, y) in x.cache:
            return x.cache[(cls, y)]
        else:
            ref = object.__new__(cls)
            x.cache[(cls, y)] = ref
            return ref

    def __init__(self, x: Block, y: Block):
        self.x, self.y = x, y
        self.value = self.diff()

    @classmethod
    def get_attr(cls) -> str:
        return cls.__name__.lower()

    @staticmethod
    def line_compare(a, b) -> float:
        l = a[1: -1]
        return np.sum(np.minimum(np.minimum(
            np.fabs(l - b[0: -2]),
            np.fabs(l - b[1: -1])),
            np.fabs(l - b[2:])))

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


def reverse(a, b):
    a.reverse = b
    b.reverse = a


reverse(Top, Bottom)
reverse(Left, Right)


loop_a = (Top, Right, Bottom, Left)
loop_b = (Left, Top, Right, Bottom)
loop_c = (Bottom, Left, Top, Right)
loop_d = (Right, Bottom, Left, Top)
loops = (loop_a, loop_b, loop_c, loop_d)


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


def good_mark(blocks: list):
    find_blocks = blocks.copy()
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
    matrices = []
    close = set()

    for block in blocks:
        if block in close:
            continue
        a_min, a_max, b_min, b_max = a, 0, b, 0
        matrix = np.ndarray((a*2, b*2), dtype=object)
        open_table = [(block, (a, b))]
        while open_table:
            block, shift = open_table.pop()
            if not block or block in close:
                continue
            close.add(block)
            a, b = shift
            matrix[a, b] = block

            a_min = a if a < a_min else a_min
            a_max = a if a > a_max else a_max
            b_min = b if b < b_min else b_min
            b_max = b if b > b_max else b_max

            open_table.append((block.top, (a-1, b)))
            open_table.append((block.right, (a, b+1)))
            open_table.append((block.bottom, (a+1, b)))
            open_table.append((block.left, (a, b-1)))
        matrices.append(matrix[a_min: a_max+1, b_min: b_max+1])
    return matrices


def max_matrix(matrices):
    max = 0
    m = None
    for matrix in matrices:
        a, b = matrix.shape
        now = a*b
        if now > max:
            max = now
            m = matrix
    return m


def block_size(matrix):
    for line in matrix:
        for block in line:
            if block:
                return block.piece.shape


def make_image(matrix):
    a, b = block_size(matrix)
    m, n = matrix.shape
    image = np.ndarray((m*a, n*b))
    for i, line in enumerate(matrix):
        for j, block in enumerate(line):
            if block:
                image[a*i: a*i+a, b*j: b*j+b] = block.piece
    return image


def mark(filename="test.png", shape=(10, 10)):
    image = gray(mpimg.imread(filename))
    pieces = split(image, shape)
    blocks = list(map(Block, pieces))
    good_mark(blocks)
    matrices = make_matrix(shape, blocks)
    return matrices


def main():
    import os
    os.system("rm out/*.png")
    matrices = mark()
    for i, matrix in enumerate(matrices):
        image = make_image(matrix)
        mpimg.imsave("out/%d.png" % i, image, dpi=1, cmap=cm.Greys_r)


if __name__ == '__main__':
    main()
