import os

import matplotlib.image as mpimg

from lib import split_and_save, is_windows, remove
from marker import marker
from config import player_id, server, raw_problem_filename


def main(problem_id):
    print("Get Problem...")
    problem_id = input("Input Problem ID (default %s): " % problem_id) or problem_id
    if is_windows:
        prefix = ".\client.exe "
    else:
        prefix = "mono ./client "
    os.system(prefix + "GetProblem %s %s %s" % (server, problem_id, raw_problem_filename))
    print("Get Problem DONE")
    with open(raw_problem_filename, "rb") as img_file:
        _ = img_file.readline()
        shape_str, select_num_str, cost_str = [
            img_file.readline().decode()
            .replace("#", "").strip() for _ in range(3)]
    b, a = [int(i) for i in shape_str.split()]
    shape = (a, b)
    select_num = int(select_num_str)
    select_cost, swap_cost = [int(i) for i in cost_str.split()]
    print("shape: ", a, b)
    print("max selection number: ", select_num)
    print("selection cost: ", select_cost, "swap cost: ", swap_cost)

    image = mpimg.imread(raw_problem_filename)
    print("Split image.")
    blocks_path = os.path.join("exe", "blocks")
    remove(blocks_path, "*.png")
    split_and_save(image, shape, blocks_path)
    mpimg.imsave("problem.png", image, dpi=1)

    print("Restore image")
    marker(shape, image)
    print("Done")
    print("========")
    while True:
        max_loop = int(input("Solve max thousand loop  (default 50): ") or "50") * 1000
        input("Are you ready solve? (Press Enter)")
        solve_prefix = ".\solve.exe " if is_windows else "./solve "
        os.system(solve_prefix + "%d %d %d %d" % (a, b, select_num, max_loop))
        if not input("Redo solve? input any char redo : "):
            break
    print("Submit Answer")
    os.system(prefix+"SubmitAnswer %s %s %d solved.txt" % (
        server, problem_id, player_id))
    print("This problem done. Good luck")


if __name__ == '__main__':
    for n in range(1000):
        main(str(n))
