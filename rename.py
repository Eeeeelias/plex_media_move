import glob
import os
import re
from sys import argv
from pathlib import Path
shift = True
# change this num_shift param to specify with what number to start
num_shift = 1
offset = -1


def shift_numbers(file, off, start=1):
    dirname, name = os.path.split(file)
    print(name)
    episode_nr = re.findall(r'\d+', name)[1]
    episode_nr_int = int(episode_nr)
    if off == -1:
        off = episode_nr_int - start
    new_name = re.sub(episode_nr, "0" + str(episode_nr_int-off), name)
    os.rename(file, Path(dirname, new_name))
    return start+1, off


# Renaming some specific weird format
for path in glob.glob(argv[1] + '/*.mp4'):
    new_path = ""
    if re.search(r'Watch ', path) is not None:
        new_path = re.sub(r'Watch ', '', path)
    if re.search(r'(?<=S0\dE\d{2}).+', path) is not None:
        new_path = re.sub(r'(?<=[sS]0\d[eE]\d{2}).+', '.mp4', new_path)
    if new_path != "":
        os.rename(path, new_path)
        print("Renamed:", path)
    if shift:
        num_shift, offset = shift_numbers(path, start=num_shift, off=offset)
