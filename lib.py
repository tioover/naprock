import os
import platform

import numpy as np

from matplotlib.image import imsave


is_windows = platform.system() == "Windows"


def grey(image):
    return np.dot(image[..., :3], [0.299, 0.587, 0.144])


def split(shape, image):
    a, b = shape
    height, width, *_ = image.shape
    block_height, block_width = (height/a, width/b)
    return [
        image[
            i*block_height: (i+1)*block_height,
            j*block_width: (j+1)*block_width
        ] for i in range(a) for j in range(b)]


def split_and_save(image, shape, path):
    for i, piece in enumerate(split(shape, image)):
        imsave(
            os.path.join(path, "%d.png" % i),
            piece
        )


def remove(*path_list):
    path = os.path.join(*path_list)
    command = "del " + path if is_windows else "rm " + path
    os.system(command)
