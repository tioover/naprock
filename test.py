import solve
from random import shuffle


def show_step(n):
    result = []
    while n.parent is not None:
        result.append(n.step)
        n = n.parent
    return " ".join(reversed(result))


x = 4
a, b = x, x
problem = list(range(a*b))
shuffle(problem)
node = solve.solve(tuple(problem), (a, b))
print(node, show_step(node), node.depth)
