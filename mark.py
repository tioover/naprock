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
    return compare_line(a.m[0], b.m[-1])


def right(a, b):
    return compare_line(a.m[:, -1], b.m[:, 0])


def bottom(a, b):
    return top(b, a)


def left(a, b):
    return right(b, a)


def find(f, base, blocks):
    min_index = 0
    min_value = float('inf')
    #print("----")
    for i in range(len(blocks)):
        block = blocks[i]
        value = f(base, block)
        #print(i, value)
        if value < min_value:
            #print("*")
            min_value = value
            min_index = i
    #print("----")
    return min_index, min_value


slices = down(img)


class Block:
    top = None
    left = None
    bottom = None
    right = None

    def __init__(self, m):
        self.m = m

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


def search():
    blocks = list(map(Block, slices))
    for block in blocks:
        if block.right:
            right_block = block.right
        else:
            right_index, _ = find(right, block, blocks)
            right_block = blocks[right_index]
        if block.top:
            top_block = block.top
        else:
            top_index, _ = find(top, block, blocks)
            top_block = blocks[top_index]
        if top_block.right:
            top_right_block = top_block.right
        else:
            top_right_index, _ = find(right, top_block, blocks)
            top_right_block = blocks[top_right_index]
        if top_right_block.bottom:
            top_right_bottom_block = top_right_block.bottom
        else:
            top_right_bottom_index, _ = find(bottom, top_right_block, blocks)
            top_right_bottom_block = blocks[top_right_bottom_index]
        if top_right_bottom_block is right_block:
            block.right = right_block
            right_block.left = block
            block.top = top_block
            top_block.bottom = block
            top_block.right = top_right_block
            top_right_block.left = top_block
            top_right_block.bottom = right_block
            right_block.up = top_right_block

    # for block in blocks:
    #     if block.left:
    #         left_block = block.left
    #     else:
    #         left_index, _ = find(left, block, blocks)
    #         left_block = blocks[left_index]
    #     if block.bottom:
    #         bottom_block = block.bottom
    #     else:
    #         bottom_index, _ = find(bottom, block, blocks)
    #         bottom_block = blocks[bottom_index]
    #     if bottom_block.left:
    #         bottom_left_block = bottom_block.left
    #     else:
    #         bottom_left_index, _ = find(left, bottom_block, blocks)
    #         bottom_left_block = blocks[bottom_left_index]
    #     if bottom_left_block.top:
    #         bottom_left_top_block = bottom_left_block.top
    #     else:
    #         bottom_left_top_index, _ = find(top, bottom_left_block, blocks)
    #         bottom_left_top_block = blocks[bottom_left_top_index]
    #     if bottom_left_top_block is left_block:
    #         block.left = left_block
    #         left_block.right = block
    #         block.bottom = bottom_block
    #         bottom_block.top = block
    #         bottom_block.left = bottom_left_block
    #         bottom_left_block.right = bottom_block
    #         bottom_left_block.up = left_block
    #         left_block.down = bottom_left_block

    img_height, img_width = img.shape
    new_list = []
    close = set()
    for block in blocks:
        if block in close:
            continue
        a, b = img_height*2, img_width*2
        new = np.ndarray((a, b), dtype=img.dtype)
        open_table = [(block, (a//2, b//2))]
        while open_table:
            block, shift = open_table.pop()
            if block in close:
                continue
            else:
                close.add(block)
            a, b = shift
            new[a: a+height, b: b+width] = block.m
            if block.top:
                open_table.append((block.top, (a-height, b)))
            if block.right:
                open_table.append((block.right, (a, b+width)))
            if block.bottom:
                open_table.append((block.bottom, (a+height, b)))
            if block.left:
                open_table.append((block.left, (a, b-width)))
        new_list.append(new)
    return new_list
