from mark import main
import matplotlib.pyplot as plt

l = main("test.png", (10, 10), False)
m = map(plt.imshow, l)

n = lambda: next(m)
