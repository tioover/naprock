import numpy as np
import matplotlib.image as mpimg


def make_image_array(filename):
    gray = lambda rgb: np.dot(
        rgb[..., :3], [0.299, 0.587, 0.144])
    return gray(mpimg.imread(filename))


def down(image, shape):
    a, b = shape
    height, width, *_ = image.shape
    block_height, block_width = (height/a, width/b)
    return [
        image[
            i*block_height: (i+1)*block_height,
            j*block_width: (j+1)*block_width
        ] for i in range(a) for j in range(b)]


class Block:
    def __init__(self, piece):
        self.piece = piece
        self.top = None
        self.right = None
        self.bottom = None
        self.left = None
        self.marked = False


class Direction:
    def __init__(self, x: Block, y: Block, diff_value=None):
        self.x = x
        self.y = y
        self.diff_value = diff_value or self.diff()

    def __eq__(self, other):
        return self.x is other.x and self.y is other.y

    def diff(self):
        pass

    @staticmethod
    def compare_line(l1, l2) -> float:
        l1 = l1[1: -1]
        return np.sum(np.minimum(np.minimum(
            np.fabs(l1 - l2[0: -2]),
            np.fabs(l1 - l2[1: -1])),
            np.fabs(l1 - l2[2:])))

    @staticmethod
    def set_up(x, y):
        pass

    def build(self):
        self.set_up(self.x, self.y)
        self.x.marked = True
        self.y.marked = True


class Top(Direction):
    def diff(self):
        return self.compare_line(self.x.piece[0], self.y.piece[-1])

    @staticmethod
    def set_up(x, y):
        x.top = y
        y.bottom = x


class Right(Direction):
    def diff(self):
        return self.compare_line(self.x.piece[..., -1], self.y.piece[..., 0])

    @staticmethod
    def set_up(x, y):
        x.right = y
        y.left = x


class Bottom(Direction):
    def diff(self):
        return self.compare_line(self.x.piece[-1], self.y.piece[0])

    @staticmethod
    def set_up(x, y):
        x.bottom = y
        y.top = x


class Left(Direction):
    def diff(self):
        return self.compare_line(self.x.piece[..., 0], self.y.piece[..., -1])

    @staticmethod
    def set_up(x, y):
        x.left = y
        y.right = x


def search(blocks, base, direction):
    return min(
        (direction(base, block) for block in blocks),
        key=lambda x: x.diff_value)


def get_trace(blocks, block, steps):
    trace = []
    for step in steps:
        ref = search(blocks, block, step)
        block = ref.y
        trace.append(ref)
    return trace


def build_trace(trace):
    for i in trace:
        i.build()


def mark(blocks):
    id_steps_a = (Top, Right, Bottom, Left)
    id_steps_b = (Right, Top, Left, Bottom)
    id_steps_c = (Top, Left, Bottom, Right)
    id_steps_d = (Left, Top, Right, Bottom)
    id_steps_e = (Bottom, Right, Top, Left)
    id_steps_f = (Right, Bottom, Left, Top)
    id_steps_g = (Bottom, Left, Top, Right)
    id_steps_h = (Left, Bottom, Right, Top)
    find_blocks = blocks

    for block in blocks:
        is_id = lambda trace: trace[-1].y is block
        trace_a = get_trace(find_blocks, block, id_steps_a)
        trace_d = get_trace(find_blocks, block, id_steps_d)
        trace_g = get_trace(find_blocks, block, id_steps_g)
        trace_e = get_trace(find_blocks, block, id_steps_e)
        if is_id(trace_a) and is_id(trace_d) and is_id(trace_g) and is_id(trace_e) and\
                trace_a[0].y is trace_d[-2].y and trace_d[0].y is trace_g[-2].y and trace_a[-2].y is trace_e[-2].y:
            print("id")
            build_trace(trace_a)
            build_trace(trace_d)
            build_trace(trace_g)
            build_trace(trace_e)

    return blocks


def make_solved_image(img, shape, blocks):
    img_height, img_width = img.shape
    shape_a, shape_b = shape
    block_height, block_width = (img_height/shape_a, img_width/shape_b)
    new_list = []
    close = set()
    for block in blocks:
        if block in close:
            continue
        a, b = img_height*20, img_width*20
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
            new[a: ah, b: bw] = block.piece

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


def jigsaw(filename="test.png", shape=(10, 10)):
    image = make_image_array(filename)
    piece_list = down(image, shape)
    blocks = mark(list(map(Block, piece_list)))
    return make_solved_image(image, shape, blocks)