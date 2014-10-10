import sys
import json

from itertools import permutations
from random import shuffle
from heapq import heappush, heappop


class Block(object):
    def __init__(self):
        self.top = {}
        self.right = {}
        self.bottom = {}
        self.left = {}


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
            entropy += block.bottom[matrix[bottom_index]]
        if right_block and j+1 < b:
            entropy += block.right[matrix[right_index]]
    return entropy / length


def make_blocks():
    with open("diff.json") as diff_file:
        diff_dct_list = json.loads(diff_file.read())

    blocks = [Block() for _ in range(len(diff_dct_list))]

    for index, empty_block in enumerate(blocks):
        empty_block.top = {block: diff for block, diff in zip(blocks, diff_dct_list[index]['top'])}
        empty_block.right = {block: diff for block, diff in zip(blocks, diff_dct_list[index]['right'])}
        empty_block.bottom = {block: diff for block, diff in zip(blocks, diff_dct_list[index]['bottom'])}
        empty_block.left = {block: diff for block, diff in zip(blocks, diff_dct_list[index]['left'])}
    return blocks


def get_value(shape, height, mat, factor):
    a, b = shape
    size = a*b
    entropy = matrix_entropy(shape, mat)
    height_value = (size-height)*factor
    return height_value + entropy


def search(shape, blocks):
    a, b = shape
    size = a * b
    solutions = []
    raw_entropy = matrix_entropy(shape, blocks)
    print("block entropy is %f , / size is %s" % (raw_entropy, raw_entropy/size))
    while not solutions:
        try:
            factor = float(raw_input("Input acceleration factor (default 0.0): ") or 0.0)
            max_loop = int(raw_input("Input thousand loop number (default 5): ") or 5) * 1000

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
                    new_tail = matrix[:]
                    new_tail.append(new_block)
                    heappush(open_list, (
                        get_value(shape, num+1, new_tail, factor),
                        new_tail,
                    ))
            if solutions and raw_input("Redo ? Input any char redo : "):
                continue
        except KeyboardInterrupt:
            break
    return [item[1] for item in solutions]


def output(blocks, solutions):
    with open("mark_solutions.json", "w") as solutions_file:
        solutions_file.write(json.dumps([
            [blocks.index(block) for block in solution] for solution in solutions]))


def main():
    a, b = int(sys.argv[1]), int(sys.argv[2])
    shape = a, b
    blocks = make_blocks()
    solutions = list(permutations(blocks)) if len(blocks) <= 9 else search(shape, blocks)
    solutions.sort(key=lambda x: matrix_entropy(shape, x))
    output(blocks, solutions[: 10])


if __name__ == '__main__':
    main()