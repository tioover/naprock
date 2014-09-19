import random

import matplotlib.image as mpimg
import numpy as np

from lib import gray, image_matrix, get_piece


diff = lambda a, b: np.sum(np.fabs(a - b))


def make_image(shape, matrix):
    piece = matrix[0]
    a, b = shape
    m, n = piece.shape
    image = np.ndarray((m*a, n*b), dtype=piece.dtype)
    for index, piece in enumerate(matrix):
        i = index // b
        j = index % b
        image[m*i: m*i+m, n*j: n*j+n] = piece
    return image


def cutoff(shape, matrix, threshold=20):
    a, b = shape
    size = a*b
    if size < 9:
        return False
    now = len(matrix) - 1
    i = now // b
    j = now % b
    if i > 0:
        value = diff(matrix[now][0], matrix[b*(i-1)+j][-1])
        if value > threshold:
            return True
    if j > 0:
        value = diff(matrix[now][..., 0], matrix[now-1][..., -1])
        if value > threshold:
            return True
    return False


def try_value(pieces):
    for piece in pieces:
        print(diff(pieces[0][0], piece[-1]))


def search(shape, pieces):
    a, b = shape
    size = a*b

    # try_value(pieces)
    # threshold = int(input("Please input threshold value:"))
    solves = []
    open = [(0, [piece]) for piece in pieces]

    for _ in range(1000):
        _, matrix = open.pop()
        length = len(matrix)
        if length == size:
            solves.append(tuple(matrix))
            print("a solve")
            continue
        for piece in pieces:
            for i in matrix:
                if i is piece:
                    break
            else:
                new = matrix.copy()
                new.append(piece)
                open.append((matrix_entropy(shape, new), new))
                open.sort(key=lambda x: x[0], reverse=True)
                # if not cutoff(shape, new, threshold):
                #     open.append(new)
    return solves


def matrix_entropy(shape, matrix):
    a, b = shape
    value = 0
    length = len(matrix)
    for now in range(length):
        i, j = now // a, now % a
        k, l = i+1, j+i
        right = now + 1
        bottom = now + b
        if bottom < length and k < a:
            value += diff(matrix[now][-1, ...], matrix[bottom][0, ...])
        if right < length and l < b:
            value += diff(matrix[now][..., -1], matrix[right][..., 0])
    return value / length


def marker(filename, shape):
    image = gray(mpimg.imread(filename))
    raw_matrix = image_matrix(image, shape)
    pieces = get_piece(raw_matrix)
    return search(shape, pieces)
