import numpy as np
import matplotlib.image as mpimg
# import matplotlib.pyplot as plt


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.144])


img = mpimg.imread("problem.png")
img = rgb2gray(img)
norm = np.linalg.norm
shape = (16, 16)
shape_a, shape_b = shape
img_height, img_width = img.shape
block_height, block_width = (img_height/shape_a, img_width/shape_b)


def split(m, index):
    a, b = index
    return m[a*block_height: (a+1)*block_height, b*block_width: (b+1)*block_width]


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
    return compare_line(a.m[0], b.m[-1])


def right(a, b):
    return compare_line(a.m[:, -1], b.m[:, 0])


def bottom(a, b):
    return top(b, a)


def left(a, b):
    return right(b, a)


def find(f, base, blocks):
    min_block = None
    min_value = float('inf')
    for block in blocks:
        value = f(base, block)
        if value < min_value:
            min_value = value
            min_block = block
    return min_block, min_value


slices = down(img)


class Block:
    top = None
    left = None
    bottom = None
    right = None

    def __init__(self, m):
        self.m = m
        self.marked = False

    @property
    def left_top(self):
        if self.left:
            return self.left.top

    @property
    def top_left(self):
        if self.top:
            return self.top.left

    @property
    def left_bottom(self):
        if self.left:
            return self.left.bottom

    @property
    def bottom_left(self):
        if self.bottom:
            return self.bottom.left

    @property
    def right_top(self):
        if self.right:
            return self.right.top

    @property
    def top_right(self):
        if self.top:
            return self.top.right

    @property
    def right_bottom(self):
        if self.right:
            return self.right.bottom

    @property
    def bottom_right(self):
        if self.bottom:
            return self.bottom.right


def basic_mark(blocks: set):
    for block in blocks:
        if block.right:
            right_block = block.right
        else:
            right_block, _ = find(right, block, blocks)
        if block.top:
            top_block = block.top
        else:
            top_block, _ = find(top, block, blocks)
        if top_block.right:
            top_right_block = top_block.right
        else:
            top_right_block, _ = find(right, top_block, blocks)
        if top_right_block.bottom:
            top_right_bottom_block = top_right_block.bottom
        else:
            top_right_bottom_block, _ = find(bottom, top_right_block, blocks)
        if top_right_bottom_block is right_block:
            block.right = right_block
            right_block.left = block
            block.top = top_block
            top_block.bottom = block
            top_block.right = top_right_block
            top_right_block.left = top_block
            top_right_block.bottom = right_block
            right_block.up = top_right_block
            block.marked = True
            top_block.marked = True
            top_right_block.marked = True
            top_right_bottom_block.marked = True
            right_block.marked = True


def auxiliary_mark(blocks: set, threshold):
    marked = set(filter(lambda x: x.marked, blocks))
    not_marked = blocks - marked
    for block in not_marked:
        found, v = find(left, block, marked)
        if v < threshold:
            block.left = found
            found.right = block
        else:
            found, v = find(bottom, block, marked)
            if v < threshold:
                block.bottom = found
                found.top = block
            else:
                found, v = find(right, block, marked)
                if v < threshold:
                    block.right = found
                    found.left = block
                else:
                    found, v = find(top, block, ma)
                    if v < threshold:
                        block.top = found
                        found.bottom = block


def search(threshold=2):
    blocks = set(map(Block, slices))
    basic_mark(blocks)
    auxiliary_mark(blocks, threshold)

    new_list = []
    close = set()
    for block in blocks:
        if block in close:
            continue
        a, b = img_height*2, img_width*2
        a_min, a_max, b_min, b_max = a, 0, b, 0
        new = np.ndarray((a, b), dtype=img.dtype)
        open_table = [(block, (a//2, b//2))]
        while open_table:
            block, shift = open_table.pop()
            if block in close:
                continue
            else:
                close.add(block)
            a, b = shift
            ah, bw = a+block_height, b+block_width
            new[a: ah, b: bw] = block.m

            # update show range.
            a_min = a if a < a_min else a_min
            a_max = ah if ah > a_max else a_max
            b_min = b if b < b_min else b_min
            b_max = bw if bw > b_max else b_max

            if block.top:
                open_table.append((block.top, (a-block_height, b)))
            if block.right:
                open_table.append((block.right, (a, b+block_width)))
            if block.bottom:
                open_table.append((block.bottom, (a+block_height, b)))
            if block.left:
                open_table.append((block.left, (a, b-block_width)))
        new_list.append(new[a_min: a_max, b_min: b_max])
    return new_list
