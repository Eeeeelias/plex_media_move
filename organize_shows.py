import glob
import os
import re
import shutil
from sys import argv

# This little script reads out episodes that are in "episode s0xe0x.mp4" format and puts them in a Season x folder
# The input directory must be the one containing all the shows you want to order in that way.
# Program usage: python3 organize_shows.py INPUT_DIR
# Example: python3 organize_shows.py "P:\\Plex\TV Shows"

wrong_episodes = []
for path in glob.glob(argv[1] + "/**/"):
    if len(glob.glob(path + "/*.mp4")) == 0:
        print('skipping:', path)
        continue
    for show in glob.glob(path + "/*.mp4"):

        try:
            season = re.search(r'\d(?=[eE]\d{1,4})', show).group()
        except AttributeError:
            wrong_episodes.append(path)
            break

        if not os.path.exists(path + "/Season {}".format(season)):
            os.makedirs(path + "/Season {}".format(season))

        shutil.move(show, path + "/Season {}/".format(season))
    print("did:", path)

for i in wrong_episodes:
    print("CHECK YOUR EPISODES IN:", i)
