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
        elif self.top:
            return self.top.left

    @property
    def left_bottom(self):
        if self.left:
            return self.left.bottom
        elif self.bottom:
            return self.bottom.left

    @property
    def right_top(self):
        if self.right:
            return self.right.top
        elif self.top:
            return self.top.right

    @property
    def right_bottom(self):
        if self.right:
            return self.right.bottom
        elif self.bottom:
            return self.bottom.right


def search(threshold=0.5):
    blocks = list(map(Block, slices))
    find_blocks = blocks.copy()
    for block in blocks:
        find_index, find_value = find(right, block, find_blocks)
        if find_value <= threshold:
            block.right = find_blocks.pop(find_index)
            block.right.left = block
    for block in blocks:
        find_index, find_value = find(top, block, find_blocks)
        if find_value <= threshold:
            block.top = find_blocks.pop(find_index)
            block.top.bottom = block
    for block in blocks:
        find_index, find_value = find(bottom, block, find_blocks)
        if find_value <= threshold:
            block.bottom = find_blocks.pop(find_index)
            block.bottom.top = block
    for block in blocks:
        find_index, find_value = find(left, block, find_blocks)
        if find_value <= threshold:
            block.left = find_blocks.pop(find_index)
            block.left.right = block
    for block in blocks:
        if not block.top:
            if block.right_top:
                i, _ = find(left, block.right_top, find_blocks)
                j, _ = find(top, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.right_top.left = b
                    block.top = b
            elif block.left_top:
                i, _ = find(left, block.left_top, find_blocks)
                j, _ = find(top, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.left_top.right = b
                    block.top = b
        if not block.right:
            if block.right_top:
                i, _ = find(bottom, block.right_top, find_blocks)
                j, _ = find(right, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.right_top.bottom = b
                    block.right = b
            elif block.right_bottom:
                i, _ = find(top, block.right_bottom, find_blocks)
                j, _ = find(right, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.right_bottom.top = b
                    block.right = b
        if not block.bottom:
            if block.right_bottom:
                i, _ = find(left, block.right_bottom, find_blocks)
                j, _ = find(bottom, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.right_bottom.left = b
                    block.bottom = b
            elif block.left_bottom:
                i, _ = find(right, block.left_bottom, find_blocks)
                j, _ = find(bottom, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.left_bottom.right = b
                    block.bottom = b
        if not block.left:
            if block.left_top:
                i, _ = find(bottom, block.left_top, find_blocks)
                j, _ = find(left, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.left_top.bottom = b
                    block.left = b
            elif block.left_bottom:
                i, _ = find(top, block.left_bottom, find_blocks)
                j, _ = find(left, block, find_blocks)
                if i == j:
                    b = find_blocks[i]
                    block.left_bottom.top = b
                    block.left = b

    find_blocks = blocks.copy()
    for block in blocks:
        if block.top:
            continue
        find_index, find_value = find(top, block, find_blocks)
        if find_value <= threshold:
            block.top = find_blocks.pop(find_index)
            block.top.bottom = block

    img_height, img_width = img.shape
    new_list = []
    close = set()
    for i in range(len(blocks)):
        i = len(blocks) - i - 1
        if blocks[i] in close:
            continue
        new = np.ndarray((img_height*2, img_width*2), dtype=img.dtype)
        open = [(blocks[i], (img_height, img_width))]
        while open:
            block, shift = open.pop()
            if block in close:
                continue
            a, b = shift
            new[a: a+height, b: b+width] = block.m
            close.add(block)
            if block.top:
                open.append((block.top, (a-height, b)))
            if block.right:
                open.append((block.right, (a, b+width)))
            if block.bottom:
                open.append((block.bottom, (a+height, b)))
            if block.left:
                open.append((block.left, (a, b-width)))
        new_list.append(new)
    return new_list
