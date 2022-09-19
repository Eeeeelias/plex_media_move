# just for testing I swear
import glob
import os
from mediainfolib import sorted_alphanumeric, seperator

sep = seperator

plex_path = "P:\\script_testing\\TV Shows"


paths = glob.glob(plex_path + f"{sep}**{sep}*.mp4", recursive=True) + glob.glob(
            plex_path + f"{sep}**{sep}*.mkv", recursive=True)

for pa in sorted_alphanumeric(paths):
    print(pa)