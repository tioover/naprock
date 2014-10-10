import os
import platform

from itertools import permutations
from heapq import heappop, heappush
from random import shuffle

import matplotlib.image as mpimg
import matplotlib.cm as cm
import numpy as np

from lib import grey, image_matrix, get_piece


def diff(a, b):
    return np.sum(np.fabs(a-b))


def bottom(a, b):
    return diff(a[-1], b[0])


def right(a, b):
    return diff(a[:, -1], b[:, 0])


def top(a, b):
    return bottom(b, a)


def left(a, b):
    return right(b, a)


class Block:
    def __init__(self, img):
        self.img = img
        self.bottom_diff = {}
        self.right_diff = {}
        self.top_diff = {}
        self.left_diff = {}
        self.right = None
        self.bottom = None
        self.top = None
        self.left = None

    def set_cache(self, blocks):
        for block in blocks:
            bottom_diff = bottom(self.img, block.img)
            self.bottom_diff[block] = bottom_diff
            block.top_diff[self] = bottom_diff

            right_diff = bottom(self.img, block.img)
            self.right_diff[block] = right_diff
            block.left_diff[self] = right_diff

        self.bottom_diff = {
            block: bottom(self.img, block.img) for block in blocks}
        self.right_diff = {
            block: right(self.img, block.img) for block in blocks}

    def get_cache(self, f, block):
        if f is right:
            return self.right_diff[block]
        elif f is bottom:
            return self.bottom_diff[block]

    def __lt__(self, _):
        return True


def matrix_entropy(shape, matrix):
    a, b = shape
    length = len(matrix)
    entropy = 0
    for index, block in enumerate(matrix):
        i, j = index // a, index % a
        right_index = index+1
        right_block = matrix[right_index] if right_index < length else None
        bottom_index = index+b
        bottom_block = matrix[bottom_index] if bottom_index < length else None

        if bottom_block and i+1 < a:
            entropy += block.get_cache(bottom, matrix[bottom_index])
        if right_block and j+1 < b:
            entropy += block.get_cache(right, matrix[right_index])
    return entropy / length


diff_min = lambda x: min(x.items(), key=lambda y: y[1])[0]


def get_value(shape, height, mat, factor):
    a, b = shape
    size = a*b
    entropy = matrix_entropy(shape, mat)
    height_value = (size-height)*factor
    return height_value + entropy


def state_search(shape, blocks):
    a, b = shape
    size = a*b
    solutions = []
    raw_entropy = matrix_entropy(shape, blocks)
    print("block entropy is %f , / size is %s" % (raw_entropy, raw_entropy/size))
    while not solutions:
        try:
            factor = input("Input acceleration factor (default 0.0): ") or 0.0
            max_loop = input("Input thousand loop number (default 5): ") or 5
            max_loop, factor = int(max_loop), float(factor)
            max_loop *= 1000

            open_list = [(0, [head]) for head in blocks]
            shuffle(open_list)
            percentage = max_loop // 100

            for loop_num in range(max_loop):
                if not open_list:
                    break
                if len(open_list) > max_loop * 2:
                    open_list = open_list[: max_loop]
                value, matrix = heappop(open_list)
                num = len(matrix)
                if loop_num % percentage == 0:
                    print("%2d %% VALUE: %f" % (loop_num // percentage, value))
                if num == size:
                    heappush(solutions, (value, matrix))
                    print("A SOLUTION")
                    continue
                for new_block in blocks:
                    if new_block in matrix:
                        continue
                    new_tail = matrix.copy()
                    new_tail.append(new_block)
                    heappush(open_list, (
                        get_value(shape, num+1, new_tail, factor),
                        new_tail,
                    ))
        except KeyboardInterrupt:
            break

    solutions.sort(key=lambda x: x[0])
    return [item[1] for item in solutions]


def block_link(blocks):
    pass


def set_cache(blocks):
    for block in blocks:
        block.set_cache(blocks)


def marker(shape, img):
    image = grey(img)
    raw_matrix = image_matrix(image, shape)
    pieces = get_piece(raw_matrix)
    blocks = list(map(Block, pieces))
    print("diff value computing...")
    set_cache(blocks)
    print("done")
    if len(blocks) < 9:
        print("make matrices")
        matrices = list(permutations(blocks))
        print("done")
        print("sort matrices")
        matrices.sort(key=lambda x: matrix_entropy(shape, x))
        print("done")
    else:
        print("make matrices...")
        matrices = state_search(shape, blocks)
        print("done")
    return blocks, matrices


def matrix_to_image(shape, matrix):
    piece = matrix[0].img
    a, b = shape
    m, n = piece.shape
    image = np.ndarray((m*a, n*b), dtype=piece.dtype)
    for index, block in enumerate(matrix):
        piece = block.img
        i = index // b
        j = index % b
        image[m*i: m*i+m, n*j: n*j+n] = piece
    return image


def out(shape, blocks, solves):
    is_windows = platform.system() == "Windows"
    print("write file")
    if is_windows:
        os.system("del preview\*.png")
    else:
        os.system("rm preview/*.png")
    i = 0
    maximum = 10
    for matrix in solves:
        if i > maximum:
            break
        mpimg.imsave(
            os.path.join("preview", "%d.png" % i),
            matrix_to_image(shape, matrix),
            dpi=1,
            cmap=cm.Greys_r,
        )
        i += 1
    print("done")
    i = int(input("Choose a solve (default 0): ") or 0)
    solve = solves[i]

    ref = []
    exe_ref = []
    for block in blocks:
        ref.append(solve.index(block))

    for block in solve:
        exe_ref.append(blocks.index(block))

    with open(os.path.join("exe", "in.txt"), "w") as f:
        f.writelines("%d %d\n" % shape)
        for r in exe_ref:
            f.writelines("%d\n" % r)

    with open("marked.txt", "w") as f:
        for r in ref:
            f.writelines("%d\n" % r)


def main():
    import sys
    a, b = int(sys.argv[1]), int(sys.argv[2])
    shape = a, b
    image = mpimg.imread("problem.png")
    blocks, matrices = marker(shape, image)
    out(shape, blocks, matrices)



if __name__ == '__main__':
    main()