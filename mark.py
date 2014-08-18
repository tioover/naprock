import numpy as np
import matplotlib.image as mpimg
# import matplotlib.pyplot as plt


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.144])


img = mpimg.imread("problem.png")
img = rgb2gray(img)
norm = np.linalg.norm
shape = (16, 16)
height, width = img.shape
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


def compare_line(a, b) -> float:
    a = a[1: -1]
    p = b[0: -2]
    q = b[1: -1]
    r = b[2:]

    x = np.fabs(a - p)
    y = np.fabs(a - q)
    z = np.fabs(a - r)
    return sum((min(*li) for li in zip(x, y, z)))


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


_blocks = down(img)


def test(i):
    blocks = _blocks[:]
    block = blocks[i]
    return block, blocks[find(top, block, blocks)]