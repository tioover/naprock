import os
import json

from os.path import join

import numpy

from matplotlib.image import imsave
from matplotlib.cm import Greys_r

from lib import split, grey, is_windows


class Block(object):
    def __init__(self, piece):
        self.img = piece


diff = lambda a, b: numpy.sum(numpy.fabs(a-b))
top = lambda a, b: diff(a[0], b[-1])
bottom = lambda a, b: diff(a[-1], b[0])
right = lambda a, b: diff(a[:, -1], b[:, 0])
left = lambda a, b: diff(a[:, 0], b[:, -1])


def write(pieces):
    with open("diff.json", "w") as diff_file:
        diff_file.write(json.dumps([{
            "top": [top(a, b) for b in pieces],
            "right": [right(a, b) for b in pieces],
            "bottom": [bottom(a, b) for b in pieces],
            "left": [left(a, b) for b in pieces],
        } for a in pieces]))


def matrix_to_image(shape, matrix):
    piece = matrix[0].img
    a, b = shape
    m, n, o = piece.shape
    image = numpy.ndarray((m*a, n*b, o), dtype=piece.dtype)
    for index, block in enumerate(matrix):
        piece = block.img
        i = index // b
        j = index % b
        image[m*i: m*i+m, n*j: n*j+n] = piece
    return image


def output(shape, blocks, solutions):
    if is_windows:
        os.system("del preview\*.png")
    else:
        os.system("rm preview/*.png")

    for num, solution in enumerate(solutions):
        imsave(
            fname=join("preview", "%d.png" % num),
            arr=matrix_to_image(shape, solution),
            dpi=1,
            cmap=Greys_r,
        )


def marker(shape, image):
    pieces = split(image, shape)
    blocks = list(map(Block, pieces))
    write(list(map(grey, pieces)))
    os.system("pypy search.py %d %d" % shape)
    with open("mark_solutions.json") as solutions_file:
        solutions = list(map(
            lambda solution: list(map(lambda i: blocks[i], solution)),
            json.loads(solutions_file.read())
        ))
    output(shape, blocks, solutions)


if __name__ == '__main__':
    main()