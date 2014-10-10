import os
import platform


def create_dir(name):
    if not os.path.isdir(name):
        os.mkdir(name)


create_dir("preview")
create_dir("exe")
create_dir(os.path.join("exe", "blocks"))

solve_file_name = "solve.rs"
out_file_name = "solve.exe" if platform.system() == "Windows" else "solve"
os.system("rustc %s -o %s --opt-level 2" % (solve_file_name, out_file_name))