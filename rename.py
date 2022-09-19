import glob
import os
import re
from pathlib import Path
from sys import argv

offset = float('-inf')


def shift_numbers(file, off, start=1):
    dirname, name = os.path.split(file)
    episode_nr = re.search(r"(?<=[eE])\d+", name).group()
    episode_nr_int = int(episode_nr)
    if off == float('-inf'):
        off = episode_nr_int - start
    new_name = re.sub(r"(?<=[eE])\d+", "0" + str(episode_nr_int - off) + "_shift", name)
    os.rename(file, Path(dirname, new_name))
    print(f"Old Name: {name}")
    print(f"New Name: {re.sub(r'_shift', '', new_name)}\n")
    return start + 1, off


def rename_weird_format(rename_path):
    # Renaming some specific weird format
    for path in glob.glob(rename_path + "/*.mp4"):
        new_path = ""
        if re.search(r"Watch ", path) is not None:
            new_path = re.sub(r"Watch ", "", path)
        if re.search(r"(?<=S0\dE\d{2}).+", path) is not None:
            new_path = re.sub(r"(?<=[sS]0\d[eE]\d{2}).+", ".mp4", new_path)
        if new_path != "":
            os.rename(path, new_path)
            print("Renamed:", path)


if __name__ == '__main__':
    if len(argv) == 1:
        print("Please put in flags.")
        exit(1)
    try:
        if argv[1] == '-r':
            rename_weird_format(argv[2])
        if argv[1] == '-s':
            num_shift = int(argv[3])
            for file in glob.glob(argv[2] + "/*.mp4"):
                num_shift, offset = shift_numbers(file, start=num_shift, off=offset)
            for file in glob.glob(argv[2] + "/*.mp4"):
                name = re.sub(r"_shift", "", os.path.basename(file))
                os.rename(file, Path(os.path.dirname(file), name))
    except IndexError:
        print("You haven't supplied enough arguments. Please put in the right arguments")
    except TypeError:
        print("Make sure all arguments are put in properly")
    except ValueError:
        print("Make sure all arguments are put in properly")
