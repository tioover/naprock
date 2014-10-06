import matplotlib.image as mpimg
import numpy as np

from heapq import heappop, heappush

from lib import grey, image_matrix, get_piece


class Block:
    def __init__(self, piece):
        self.piece = piece
        self.bottom_cache = {}
        self.right_cache = {}

    def __lt__(self, other):
        return True

    def __cmp__(self, _):
        return 0


diff = lambda a, b: np.sum(np.fabs(a - b))


def make_image(shape, matrix):
    piece = matrix[0].piece
    a, b = shape
    m, n = piece.shape
    image = np.ndarray((m*a, n*b), dtype=piece.dtype)
    for index, block in enumerate(matrix):
        piece = block.piece
        i = index // b
        j = index % b
        image[m*i: m*i+m, n*j: n*j+n] = piece
    return image


def search(shape, pieces, max_loop=1000000, factor=0):
    a, b = shape
    size = a*b
    entropy = lambda x: matrix_entropy(shape, x)
    value = lambda x: (size-len(x))*factor+entropy(x)

    solves = []
    open = []

    for head in pieces:
        heappush(open, (0, [head]))
    for i in range(max_loop):
        try:
            _, matrix = heappop(open)
        except IndexError:
            break
        length = len(matrix)
        if i % 1000 == 0:
            print("当前长度 ", length)
        if length == size:
            solves.append(matrix)
            print("在第 %8d 次循环找到了一个解" % i)
            continue
        for piece in pieces:
            if piece not in matrix:
                new_matrix = matrix.copy()
                new_matrix.append(piece)
                heappush(open, (
                    value(matrix),
                    new_matrix))
    solves.sort(key=entropy)
    return solves


def matrix_entropy(shape, matrix):
    a, b = shape
    block_a, block_b = matrix[0].piece.shape
    entropy = 0
    length = len(matrix)
    for now in range(length):
        i, j = now // a, now % a
        k, l = i+1, j+i
        right = now + 1
        bottom = now + b
        block = matrix[now]
        if bottom < length and k < a:
            bottom_block = matrix[bottom]
            if bottom_block in block.bottom_cache:
                value = block.bottom_cache[bottom_block]
            else:
                value = diff(block.piece[-1], bottom_block.piece[0]) / block_b
                block.bottom_cache[bottom_block] = value
            entropy += value
        if right < length and l < b:
            right_block = matrix[right]
            if right_block in block.right_cache:
                value = block.right_cache[right_block]
            else:
                value = diff(block.piece[:, -1], right_block.piece[:, 0]) / block_a
                block.right_cache[right_block] = value
            entropy += value
    return entropy / length


def marker(filename, shape):
    image = grey(mpimg.imread(filename))
    raw_matrix = image_matrix(image, shape)
    pieces = get_piece(raw_matrix)
    return search(shape, list(map(Block, pieces)))
