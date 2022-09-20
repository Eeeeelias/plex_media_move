import concurrent.futures
import csv
import datetime
import glob
import os
import re
from itertools import dropwhile
from typing import AnyStr, List
from mediainfolib import get_duration_cv2, check_ffmpeg, get_language, seperator, split_shows, \
    convert_seconds

sep = seperator


def get_show_infos(plex_path: str, nr=1) -> list[tuple]:
    _info_shows = []
    info_shows = []
    if os.path.basename(plex_path) != "TV Shows":
        _info_shows = [search_show(plex_path)]
    else:
        shows_to_check = [plex_path + sep + i for i in os.listdir(plex_path)]
        for show in shows_to_check:
            _info_shows.append(search_show(show))

    # single threaded loop
    id = nr
    for i in range(len(_info_shows)):
        _info_shows[i][0] = id
        info_shows.append(tuple(_info_shows[i]))
        id += 1
    return info_shows


def search_show(show):
    show_name = os.path.basename(show)
    print("[i] Show: {}".format(show_name))
    episodes = 0
    seasons = 0
    size = 0
    last_modified = 0
    runtime = 0
    for episode in glob.glob(show + f"{sep}**{sep}*.mp4") + glob.glob(show + f"{sep}**{sep}*.mkv"):
        parts = list(dropwhile(lambda x: x != "TV Shows", episode.split(sep)))[1:]
        # parts gives [show, season, episode]
        try:
            seasons = max(seasons, int(re.search(r"\d+", parts[1]).group()))
        except AttributeError:
            pass
        episodes = episodes + 1
        size += os.path.getsize(episode)
        last_modified = max(os.path.getmtime(episode), last_modified)
        runtime += get_duration_cv2(episode)
    return [0, show_name, seasons, episodes, runtime, size, last_modified]


def get_movie_infos(plex_path: AnyStr, nr=1) -> List[tuple]:
    movie_infos = []
    movie_nr = nr
    movie_name = ""
    year = 0
    version = "unique"
    # make it possible to check just a single media
    if os.path.isfile(plex_path):
        paths_to_check = [plex_path]
    else:
        paths_to_check = glob.glob(plex_path + f"{sep}**{sep}*.mp4", recursive=True) + glob.glob(
            plex_path + f"{sep}**{sep}*.mkv", recursive=True)
    for media in paths_to_check:
        filename = os.path.basename(media)
        print(f"[i] Movie: {os.path.splitext(filename)[0]}")
        try:
            movie_name = re.search(r".+(?= \(\d{4}\))", filename).group()
            year = re.search(r"(?<=\()\d{4}(?=\))", filename).group()
        except AttributeError:
            print(
                f"[w] Movie {filename} not properly named! Make sure its in 'Movie name (Year) - Version.ext' format.")
            exit(1)
        try:
            version = re.search(r"(?<=\(\d{4}\) - ).*(?=(.mp4)|(.mkv))", filename).group()
        except AttributeError:
            version = "unique"
        language = ";".join(get_language(media))
        runtime = get_duration_cv2(media)
        size = os.path.getsize(media)
        last_modified = os.path.getmtime(media)
        file_type = os.path.splitext(filename)[1]
        movie_infos.append((movie_nr, movie_name, year, language, version, runtime, size, last_modified, file_type))
        movie_nr += 1
    return movie_infos


# possibly borked
def write_to_csv(show_infos: List, filename="show_infos") -> None:
    filename = filename.rstrip('.csv')
    with open(filename + '.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        head = ['Number', 'Name', 'Seasons', 'Episodes', 'Runtime', 'Size', 'Last Updated']
        if filename != "show_infos":
            head = ['Number', 'Name', 'Year', 'Language', 'Version', 'Size', 'Last Updated', 'Filetype']
        csvwriter.writerow(head)
        for show in show_infos:
            csvwriter.writerow(show.values())


def print_show_infos(show_infos: List) -> None:
    for show in show_infos:
        print(f"===== SHOW ======")
        print(f"Name: {show[1]}")
        print(f"Seasons: {show[2]}")
        print(f"Episodes: {show[3]}")
        print(f"Runtime: {convert_seconds(show[4])}")
        print(f"Last modified: {datetime.datetime.fromtimestamp(show[6]).strftime('%Y-%m-%d, %H:%M')}")
        print(f"Show size: {round(show[5] / (1024 ** 3), 2)} GB\n")
    return


def print_movie_infos(movie_infos: List) -> None:
    for movie in movie_infos:
        print(f"===== MOVIE ======")
        print(f"Name: {movie[1]}")
        print(f"Year: {movie[2]}")
        print(f"Language: {movie[3]}")
        print(f"Version: {movie[4]}")
        print(f"Runtime: {convert_seconds(movie[5])}")
        print(f"Last modified: {datetime.datetime.fromtimestamp(movie[7]).strftime('%Y-%m-%d, %H:%M')}")
        print(f"Movie size: {round(movie[6] / (1024 ** 3), 2)} GB")
        print(f"File type: {movie[8]}\n")


def fetch_all(overall_path) -> tuple[List[tuple], List[tuple]]:
    overall_path = overall_path.rstrip(sep)
    if not check_ffmpeg():
        exit(1)
    info_shows = get_show_infos(overall_path + f"{sep}TV Shows")
    info_movies = get_movie_infos(overall_path + f"{sep}Movies")
    return info_shows, info_movies


if __name__ == '__main__':
    info_shows, info_movies = fetch_all("P:\\Plex Shows")
    write_to_csv(info_shows)
    write_to_csv(info_movies, filename='movie_infos')
