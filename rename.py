import glob
import os
import re
from sys import argv

# Renaming some specific weird format

for path in glob.glob(argv[1] + '/*.mp4'):
    new_path = ""
    if re.search(r'Watch ', path) is not None:
        new_path = re.sub(r'Watch ', '', path)
    if re.search(r'(?<=S0\dE\d{2}).+', path) is not None:
        new_path = re.sub(r'(?<=S0\dE\d{2}).+', '.mp4', new_path)
    if new_path != "":
        os.rename(path, new_path)
        print("Renamed:", path)
