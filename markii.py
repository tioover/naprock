from itertools import permutations
import matplotlib.image as mpimg
import numpy as np

from lib import grey, image_matrix, get_piece


def diff(a, b):
    return np.sum(np.fabs(a-b))


def bottom(a, b):
    return diff(a[-1], b[0])


def right(a, b):
    return diff(a[:, -1], b[:, 0])


class Block:
    def __init__(self, img):
        self.img = img
        self.bottom_diff = None
        self.right_diff = None
        self.right = None
        self.bottom = None

    def set_cache(self, blocks):
        self.bottom_diff = {
            block: bottom(self.img, block.img) for block in blocks}
        self.right_diff = {
            block: right(self.img, block.img) for block in blocks}

    def get_cache(self, f, block):
        if f is right:
            return self.right_diff[block]
        elif f is bottom:
            return self.bottom_diff[block]


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
    solve_num = 0
    for block in blocks:
        if base is block:
            continue
        value = base.get_cache(f, block)
        result.append((value, block))

    result.sort(key=lambda x: x[0])
    if result[0][0] < threshold and result[1][0] - result[0][0] > threshold / 4:
        print(result[1][0] - result[0][0], '>', threshold / 4)
        return result[0][1]
    else:
        return None


def matrix_entropy(shape, matrix):
    a, b = shape
    entropy = 0
    size = len(matrix)
    length = 0
    for index, block in enumerate(matrix):
        if block is None:
            continue
        length += 1
        i, j = index // a, index % a
        right_i = index+1
        bottom_i = index+b

        if bottom_i < size and i+1 < a:
            entropy += block.get_cache(bottom, matrix[bottom_i])
        if right_i < size and j+1 < b:
            entropy += block.get_cache(right, matrix[right_i])
    return entropy / length


def test_make(block):
    img = block.img
    img_a, img_b = img.shape
    a, b = img_a, img_b
    if block.right is None:
        return img
    image = np.ndarray((a, b*2))
    image[:, :img_b] = img
    image[:, img_b:] = block.right.img
    v = list(block.right_diff.values())
    v.sort()
    print(v[:10])
    print(v[1]-v[0], v[2]-v[1], v[3]-v[2], v[4]-v[3], v[5]-v[4])
    value = block.get_cache(right, block.right)
    print(value)
    return image


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


def marker(filename, shape):
    image = grey(mpimg.imread(filename))
    raw_matrix = image_matrix(image, shape)
    pieces = get_piece(raw_matrix)
    blocks = list(map(Block, pieces))
    print("diff value computing...")
    set_cache(blocks)
    if len(blocks) <= 9:
        print("make matrices")
        matrices = list(permutations(blocks))
        print("sort matrices")
        matrices.sort(key=lambda x: matrix_entropy(shape, x))
    print("done\nlink block...")
    block_link(blocks)
    print("done\nmake matrices...")
    return blocks


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