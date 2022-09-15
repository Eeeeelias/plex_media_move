import csv
import glob
import re
from sys import platform
from itertools import dropwhile
from typing import AnyStr, List, Dict
import os

if platform == "win32":
    sep = "\\"
else:
    sep = "/"


def get_infos(plex_path: AnyStr, shows=True):
    plex_path = plex_path.rstrip(sep)
    drop = 'TV Shows'
    if not shows:
        drop = 'Movies'

    show_infos = []
    show_nr = 0
    show = ""
    seasons = 0
    episodes = 0
    size = 0.0
    for media in glob.glob(plex_path + f"{sep}**{sep}*.mp4", recursive=True):
        # parts gives [show, season, episode]
        parts = list(dropwhile(lambda x: x != drop, media.split(sep)))[1:]
        if show == "":
            print(f"Show: {parts[0]}")
            show = parts[0]
            show_nr = 1
        if show == parts[0]:
            try:
                seasons = int(re.search(r"\d+", parts[1]).group())
            except AttributeError:
                pass
            episodes = episodes + 1
            size += os.path.getsize(media)

            continue
        show_infos.append(
            {"show_nr": show_nr, "show_name": show, "seasons": seasons, "episodes": episodes, "show_size": size})
        print(f"Show: {parts[0]}")
        show_nr += 1
        show = parts[0]
        seasons = 1
        episodes = 1
        size = os.path.getsize(media)
    show_infos.append(
        {"show_nr": show_nr, "show_name": show, "seasons": seasons, "episodes": episodes, "show_size": size})

    return show_infos


def print_infos(show_infos: List):
    for show in show_infos:
        print("===== SHOW ======")
        print(f"Name: {show['show_name']}")
        print(f"Seasons: {show['seasons']}")
        print(f"Episodes: {show['episodes']}")
        print(f"Show size: {round(show['show_size'] / (1024 ** 3), 2)} GB\n")
    return


def write_to_csv(show_infos: List):
    with open('show_infos.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Number', 'Name', 'Seasons', 'Episodes', 'Show size'])
        for show in show_infos:
            csvwriter.writerow(show.values())


if __name__ == '__main__':
    # P:\\Plex Shows\\TV Shows
    # P:\\script_testing\\TV Shows
    info = get_infos("P:\\Plex Shows\\TV Shows", shows=True)
    #print_infos(info)
    write_to_csv(info)
