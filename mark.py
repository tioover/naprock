import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

rgb2gray = lambda rgb: np.dot(rgb[..., :3], [0.299, 0.587, 0.144])

def get_img(filename):
    img = mpimg.imread(filename)
    img = rgb2gray(img)
    return img


def split(img, shape, index):
    shape_a, shape_b = shape
    if len(img.shape) == 2:
        img_height, img_width = img.shape
    else:
        img_height, img_width, *_ = img.shape
    block_height, block_width = (img_height/shape_a, img_width/shape_b)
    a, b = index
    return img[a*block_height: (a+1)*block_height, b*block_width: (b+1)*block_width]


def down(img, shape):
    blocks = []
    a, b = shape
    for i in range(a):
        for j in range(b):
            piece = split(img, shape, (i, j))
            blocks.append(piece)
    return blocks


def compare_line(a, b) -> float:
    a = a[1: -1]
    return np.sum(np.minimum(np.minimum(
        np.fabs(a - b[0: -2]),
        np.fabs(a - b[1: -1])),
        np.fabs(a - b[2:])))


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


def up_right_mark(blocks: set):
    for block in blocks:
        right_block, _ = find(right, block, blocks)
        top_block, _ = find(top, block, blocks)
        top_right_block, _ = find(right, top_block, blocks)
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


def left_bottom_mark(blocks: set):
    for block in blocks:
        bottom_block, _ = find(bottom, block, blocks)
        left_block, _ = find(left, block, blocks)
        left_bottom_block, _ = find(bottom, left_block, blocks)
        left_bottom_right_block, _ = find(right, left_bottom_block, blocks)
        if bottom_block is left_bottom_right_block:
            block.bottom = bottom_block
            bottom_block.top = block
            block.left = left_block
            left_block.right = block
            left_block.bottom = left_bottom_block
            left_bottom_block.top = left_block
            left_bottom_block.right = bottom_block
            bottom_block.left = left_bottom_block
            block.marked = True
            left_block.marked = True
            left_bottom_block.marked = True
            bottom_block.marked = True


def loop_mark(blocks: set):
    for block in blocks:
        bottom_block, _ = find(bottom, block, blocks)
        left_block, _ = find(left, block, blocks)
        left_bottom_block, _ = find(bottom, left_block, blocks)
        left_bottom_right_block, _ = find(right, left_bottom_block, blocks)
        if bottom_block is not left_bottom_right_block:
            return

        bottom_right_block, _ = find(right, bottom_block, blocks)
        bottom_right_top_block, _ = find(top, bottom_right_block, blocks)
        bottom_right_top_left_block, _ = find(left, bottom_right_top_block, blocks)

        if bottom_right_top_left_block is block:
            block.bottom = bottom_block
            bottom_block.top = block
            block.left = left_block
            left_block.right = block
            left_block.bottom = left_bottom_block
            left_bottom_block.top = left_block
            left_bottom_block.right = bottom_block
            bottom_block.left = left_bottom_block
            bottom_block.right = bottom_right_block
            bottom_right_block.left = bottom_block
            bottom_right_block.top = bottom_right_top_block
            bottom_right_top_block.bottom = bottom_right_block
            bottom_right_top_block.left = block
            block.right = bottom_right_top_block
            for i in [block, left_bottom_block, left_block, left_bottom_right_block,
                      bottom_right_block, bottom_block, bottom_right_block, bottom_right_top_block]:
                i.marked = True


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


def piece_together(slices: list, aux, threshold, up_first):
    blocks = set(map(Block, slices))
    left_bottom_mark(blocks)
    loop_mark(blocks)
    if aux:
        auxiliary_mark(blocks, threshold)

    return blocks


def make_img(img, shape, blocks):
    img_height, img_width = img.shape
    shape_a, shape_b = shape
    block_height, block_width = (img_height/shape_a, img_width/shape_b)
    new_list = []
    close = set()
    for block in blocks:
        if block in close:
            continue
        a, b = img_height*2, img_width*2
        a_min, a_max, b_min, b_max = a, 0, b, 0
        new = np.ndarray((a, b))
        open_table = [(block, (a//2, b//2))]
        while open_table:
            block, shift = open_table.pop()
            if block in close:
                continue
            else:
                close.add(block)
            a, b = shift
            ah, bw = a+block_height, b+block_width
            try:
                new[a: ah, b: bw] = block.m
            except ValueError as e:
                print(new.shape)
                print((a, ah))
                print((b, bw))
                print(block.m)
                print(new[a: ah, b: bw])
                raise e

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


def main(filename="test.png", shape=(16, 16), aux=True, threshold=1, up_first=True):
    img = get_img(filename)
    slices = down(img, shape)
    blocks = piece_together(slices, aux, threshold, up_first)
    return make_img(img, shape, blocks)


if __name__ == '__main__':
    pass
