import os

import matplotlib.image as mpimg

from lib import split_and_save
from markii import marker, out
from config import player_id, server, raw_problem_filename, solve_filename


def main(problem_id):
    print("Get Problem...")
    problem_id = input("Input Problem ID (default %s): " % problem_id) or problem_id
    os.system(".\client.exe GetProblem %s %s %s" % (server, problem_id, raw_problem_filename))
    print("Get Problem DONE")
    with open(raw_problem_filename, "rb") as img_file:
        _ = img_file.readline()
        shape_str, select_num_str, cost_str = [img_file.readline().decode().replace(
            "#", "").strip() for _ in range(3)]
    a, b = [int(i) for i in shape_str.split()]
    shape = (a, b)
    select_num = int(select_num_str)
    select_cost, swap_cost = [int(i) for i in cost_str.split()]
    print("shape: ", a, b)
    print("max selection number: ", select_num)
    print("selection cost: ", select_cost, "swap cost: ", swap_cost)


    img = mpimg.imread(raw_problem_filename)
    print("Split image.")
    zoom = 1
    # zoom = float(input("Image resize scale (default 1.0): ") or 1.0)
    split_and_save(img, shape, "exe\\blocks\\", zoom)

    print("Restore image")
    redo = "first"
    while redo:
        blocks, matrices = marker(shape, img)
        out(shape, blocks, matrices)
        redo = input("Redo? (Input any char redo): ")
    print("Done")
    print("========")
    input("Are you ready solve? (Press Enter)")
    os.system(".\\solve.exe %d %d" % shape)
    print("Done")
    print("Submit Answer")
    os.system(".\\client.exe SubmitAnswer %s %s %d %s" % (
        server, problem_id, player_id, solve_filename))
    print("This problem done. Good luck")


if __name__ == '__main__':
    for i in range(10000):
        main(str(i))
