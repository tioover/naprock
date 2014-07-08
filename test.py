import solve
from random import shuffle


def show_step(n):
    step = n.step
    result = []
    while step[1] is not ():
        result.append(step[0])
        step = step[1]
    return "".join(reversed(result))


a, b = 4, 4
problem = list(range(a*b))
shuffle(problem)
node = solve.solve(tuple(problem), (a, b))
print(node, show_step(node), node.depth)
