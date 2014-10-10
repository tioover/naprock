import os
import platform

import numpy as np

#from scipy.misc import imresize
from matplotlib.image import imsave


is_windows = platform.system() == "Windows"


def grey(image):
    return np.dot(image[..., :3], [0.299, 0.587, 0.144])


def image_matrix(image, shape):
    a, b = shape
    height, width, *_ = image.shape
    block_height, block_width = (height/a, width/b)
    matrix = np.ndarray(shape, dtype=object)
    for i in range(a):
        for j in range(b):
            matrix[i, j] = image[
            i*block_height: (i+1)*block_height,
            j*block_width: (j+1)*block_width
        ]
    return matrix


def get_piece(matrix):
    return [piece for line in matrix.tolist() for piece in line]


def split(image, shape):
    a, b = shape
    height, width, *_ = image.shape
    block_height, block_width = (height/a, width/b)
    return [
        image[
            i*block_height: (i+1)*block_height,
            j*block_width: (j+1)*block_width
        ] for i in range(a) for j in range(b)]


def split_and_save(image, shape, path):
    for i, piece in enumerate(split(image, shape)):
        imsave(
            os.path.join(path, "%d.png" % i),
            piece
        )
