#!/usr/bin/env python3
import sys
from mark import np, mpimg, down
from random import shuffle


input_file_name = sys.argv[1]
shape = int(sys.argv[2]), int(sys.argv[3])
output_file_name = sys.argv[4] if len(sys.argv) > 4 else "problem.png"
img = mpimg.imread(input_file_name)

a, b = shape
img_a, img_b, _ = img.shape
if img_a % a:
    img_a = img_a // a * a
if img_b % b:
    img_b = img_b // b * b
m, n = img_a / a, img_b / b

new = np.ndarray((img_a, img_b, _))
lst = down(img[:img_a, :img_b], shape)
shuffle(lst)
for i in range(a):
    for j in range(b):
        piece = lst[i*b+j]
        new[i*m: i*m+m, j*n: j*n+n] = piece
mpimg.imsave(output_file_name, new, dpi=1)
t = mpimg.imread(output_file_name)
print(t.shape, img.shape)