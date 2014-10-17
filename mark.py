#!/usr/bin/env python3
import numpy as np
from random import shuffle
from lib import grey, split


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
    m, n = a*4, b*4
    result = []
    matrices = []
    unmarked = set()
    close = set()

    for block in blocks:
        if not block or block in close:
            continue
        a_min, a_max, b_min, b_max = m, 0, n, 0
        matrix = np.zeros((m, n))
        open_table = [(block, (m//2, n//2))]
        while open_table:
            block, shift = open_table.pop()
            if not block or block in close:
                continue
            close.add(block)
            i, j = shift
            matrix[i, j] = block

            a_min = i if i < a_min else a_min
            a_max = i if i > a_max else a_max
            b_min = j if j < b_min else b_min
            b_max = j if j > b_max else b_max

            open_table.append((block.top, (i-1, j)))
            open_table.append((block.right, (i, j+1)))
            open_table.append((block.bottom, (i+1, j)))
            open_table.append((block.left, (i, j-1)))
        result.append(matrix[a_min: a_max+1, b_min: b_max+1])

    for matrix in result:
        if matrix.shape == (1, 1):
            unmarked.add(matrix[0, 0])
        else:
            matrices.append(matrix)
    return matrices


def max_matrix(matrices):
    maximum = 0
    mat = None
    for matrix in matrices:
        a, b = matrix.shape
        now = a*b
        if now > maximum:
            maximum = now
            mat = matrix
    return mat


def first_block(matrix):
    for line in matrix:
        for block in line:
            if block:
                return block


def make_image(matrix):
    piece = first_block(matrix).piece
    a, b = piece.shape
    m, n = matrix.shape
    image = np.zeros((m*a, n*b))
    for i, line in enumerate(matrix):
        for j, block in enumerate(line):
            if block:
                image[a*i: a*i+a, b*j: b*j+b] = block.piece
    return image


def marker(shape, img):
    image = grey(img)
    pieces = split(shape, image)
    blocks = list(map(Block, pieces))
    good_mark(blocks)
    matrices = make_matrix(shape, blocks)
    matrix = max_matrix(matrices)
    return matrix