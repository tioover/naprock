import numpy as np
import matplotlib.image as mpimg
# import matplotlib.pyplot as plt


norm = np.linalg.norm
img = mpimg.imread("problem.png")
shape = (16, 16)
height, width, _ = img.shape
height, width = (height/16, width/16)


def split(m, index):
    a, b = index
    return m[a*height: (a+1)*height, b*width: (b+1)*width]


def down(m):
    blocks = []
    a, b = shape
    for i in range(a):
        for j in range(b):
            blocks.append(split(m, (i, j)))
    return blocks


def compare(o, p) -> float:
    o = o[1: -1]
    q = p[0: -2]
    r = p[1: -1]
    s = p[2:]

    x = map(norm, o - q)
    y = map(norm, o - r)
    z = map(norm, o - s)
    return sum((min(*l) for l in zip(x, y, z)))


def compare_line(a, b) -> float:
    return compare(a, b) + compare(b, a)


def top(a, b):
    return compare_line(a[0], b[-1])


def right(a, b):
    return compare_line(a[:, -1], b[:, 0])


def bottom(a, b):
    return top(b, a)


def left(a, b):
    return right(b, a)


def find(f, base, blocks):
    min_index = 0
    min_value = float('inf')
    for i in range(len(blocks)):
        block = blocks[i]
        value = f(base, block)
        if value < min_value:
            min_value = value
            min_index = i
    return min_index



def test(i):
    blocks = down(img)
    block = blocks[i]
    return block, blocks[find(top, block, blocks)]