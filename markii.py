from itertools import permutations
from heapq import heappop, heappush
from random import shuffle

import matplotlib.image as mpimg
import numpy as np

#from numba import jit
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

    def __lt__(self, other):
        return True


def get_threshold(f, blocks):
    diff_list = []
    grad_list = []

    for base in blocks:
        base_diff_list = [base.get_cache(f, block) for block in blocks]
        base_diff_list.sort()
        diff_list.append(base_diff_list[0])
        grad_list.append(base_diff_list[1]-base_diff_list[0])
    diff_list.sort()
    grad_list.sort()
    threshold = sum(diff_list)/len(diff_list)
    grad = grad_list[len(grad_list)//2]
    print(diff_list)
    print("threshold: ", threshold)
    print(grad_list)
    print("grad: ", grad)
    print("----")
    return threshold


def search(f, base, blocks, threshold=None):
    threshold = threshold or get_threshold(f, blocks)
    result = []
    for block in blocks:
        if base is block:
            continue
        value = base.get_cache(f, block)
        result.append((value, block))

    result.sort(key=lambda x: x[0])
    if result[0][0] < threshold and result[1][0] - result[0][0] > threshold / 4:
        return result[0][1]
    else:
        return None


def matrix_entropy(shape, matrix):
    a, b = shape
    max_entropy = 0
    entropy = 0
    size = len(matrix)
    length = 0
    for index, block in enumerate(matrix):
        if not block:
            continue
        length += 1
        i, j = index // a, index % a
        right_i = index+1
        bottom_i = index+b

        if bottom_i < size and i+1 < a and matrix[bottom_i]:
            value = block.get_cache(bottom, matrix[bottom_i])
            entropy += value
            if value > max_entropy:
                max_entropy = value
        if right_i < size and j+1 < b and matrix[right_i]:
            value = block.get_cache(right, matrix[right_i])
            entropy += value
            if value > max_entropy:
                max_entropy = value
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
    blank_matrix = [None] * size
    solves = []
    open_list = []
    factor = input("Input acceleration factor (default 0.0): ") or 0.0
    max_loop = input("Input max loop number (default 50000): ") or 50000
    max_loop, factor = int(max_loop), float(factor)

    for head in blocks:
        matrix = blank_matrix.copy()
        matrix[0] = head
        open_list.append((0, 1, matrix))

    shuffle(open_list)

    one_of_max_loop = max_loop // 100

    for loop_num in range(max_loop):
        if not open_list:
            break
        if len(open_list) > max_loop * 2:
            open_list = open_list[: max_loop]
        if loop_num % one_of_max_loop == 0:
            print("%2d %%" % (loop_num // one_of_max_loop))
        try:
            value, num, matrix = heappop(open_list)
            if num == size:
                heappush(solves, (value, matrix))
                print("a solve")
                continue
            for i in range(size):
                if matrix[i]:
                    continue
                pre_open = []
                for new_block in blocks:
                    if new_block in matrix:
                        continue
                    new_matrix = matrix.copy()
                    new_matrix[i] = new_block
                    pre_open.append((
                        get_value(shape, num+1, new_matrix, factor),
                        num+1,
                        new_matrix
                    ))
                pre_open.sort()
                for item in pre_open[:8]:
                    heappush(open_list, item)
                break
        except KeyboardInterrupt:
            break

    solves.sort(key=lambda x: x[0])
    return [solve[1] for solve in solves]


def block_link(blocks):
    bottom_threshold = get_threshold(bottom, blocks)
    right_threshold = get_threshold(right, blocks)

    for block in blocks:
        if block.bottom is None:
            bottom_block = search(
                bottom, block, blocks, threshold=bottom_threshold)
            if bottom_block is not None:
                block.bottom = bottom_block
        if block.right is None:
            right_block = search(
                right, block, blocks, threshold=right_threshold)
            if right_block is not None:
                block.right = right_block


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
        # print("done\nlink block...")
        # block_link(blocks)
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
    import os
    print("write file")
    os.system("del preview\*.png")
    i = 0
    maximum = 10
    for matrix in solves:
        if i > maximum:
            break
        mpimg.imsave("preview\%d.png" % i, matrix_to_image(shape, matrix), dpi=1)
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

    with open("exe\in.txt", "w") as f:
        f.writelines("%d %d\n" % shape)
        for r in exe_ref:
            f.writelines("%d\n" % r)

    with open("marked.txt", "w") as f:
        for r in ref:
            f.writelines("%d\n" % r)


def main():
    import sys
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    shape = a, b
    image = mpimg.imread("problem.png")
    blocks, matrices = marker(shape, image)
    out(shape, blocks, matrices)



if __name__ == '__main__':
    main()
