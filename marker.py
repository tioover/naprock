import os
import json
from os.path import join

import numpy
from matplotlib.image import imsave

from lib import split, grey, remove


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
    m, n = piece.shape
    image = numpy.ndarray((m*a, n*b))
    for index, block in enumerate(matrix):
        piece = block.img
        i = index // b
        j = index % b
        image[m*i: m*i+m, n*j: n*j+n] = piece
    return image


def preview(shape, solutions):
    remove("preview", "*.png")

    for num, solution in enumerate(solutions):
        imsave(
            fname=join("preview", "%d.png" % num),
            arr=matrix_to_image(shape, solution),
            dpi=1,
        )


def output(shape, blocks, solutions):
    solution = solutions[int(input("Choose a solve (default 0): ") or 0)]
    solve_map = [solution.index(block) for block in blocks]
    exe_map = [blocks.index(block) for block in solution]

    with open(join("exe", "in.txt"), "w") as exe_input:
        exe_input.writelines("%d %d\n" % shape)
        for i in exe_map:
            exe_input.writelines("%d\n" % i)
    with open("marked.txt", "w") as solve_input:
        for i in solve_map:
            solve_input.writelines("%d\n" % i)


def marker(shape, image):
    pieces = split(shape, grey(image))
    blocks = list(map(Block, pieces))
    write(pieces)
    solutions = []
    while True:
        os.system("pypy search.py %d %d" % shape)
        with open("mark_solutions.json") as solutions_file:
            solutions = list(map(
                lambda solution: list(map(lambda i: blocks[i], solution)),
                json.loads(solutions_file.read())
            ))
        preview(shape, solutions)
        if not input("Redo ? Input any char redo : "):
            break
    output(shape, blocks, solutions)
