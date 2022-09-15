import glob
import re
from sys import platform
from itertools import dropwhile
from typing import AnyStr, List
import os

if platform == "win32":
    sep = "\\"
else:
    sep = "/"


def get_infos(plex_path: AnyStr, shows=True):
    drop = 'TV Shows'
    if not shows:
        drop = 'Movies'

    show_infos = []
    show = ""
    seasons = 0
    episodes = 0
    size = 0.0
    for media in glob.glob(plex_path + f"{sep}**{sep}*.mp4", recursive=True):
        # parts gives [show, season, episode]
        parts = list(dropwhile(lambda x: x != drop, media.split(sep)))[1:]
        if show == "":
            show = parts[0]
        if show == parts[0]:
            seasons = int(re.search(r"\d+", parts[1]).group())
            episodes = episodes + 1
            size += os.path.getsize(media)
            continue
        show_infos.append({"show_name": show, "seasons": seasons, "episodes": episodes, "show_size": size})
        show = parts[0]
        seasons = 1
        episodes = 1
        size = os.path.getsize(media)
    return show_infos


def print_infos(show_infos: List):
    for show in show_infos:
        print("===== SHOW ======")
        print(f"Name: {show['show_name']}")
        print(f"Seasons: {show['seasons']}")
        print(f"Episodes: {show['episodes']}")
        print(f"Show size: {round(show['show_size'] / (1024 ** 3), 2)} GB\n")
    return


if __name__ == '__main__':
    info = get_infos("P:\\script_testing\\TV Shows", shows=True)
    print_infos(info)
