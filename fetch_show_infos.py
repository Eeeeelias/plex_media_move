import csv
import datetime
import glob
import os
import re
from itertools import dropwhile
from sys import platform
from typing import AnyStr, List
from mediainfolib import convert_millis, get_duration, check_ffmpeg, get_language

if platform == "win32":
    sep = "\\"
else:
    sep = "/"


def get_show_infos(plex_path: AnyStr):
    drop = 'TV Shows'

    show_infos = []
    show_nr = 0
    show = ""
    seasons = 0
    episodes = 0
    size = 0.0
    last_modified = 0
    runtime = 0
    for media in glob.glob(plex_path + f"{sep}**{sep}*.mp4", recursive=True) + \
                 glob.glob(plex_path + f"{sep}**{sep}*.mkv", recursive=True):
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
            last_modified = os.path.getmtime(media) if last_modified < os.path.getmtime(media) else last_modified
            runtime += get_duration(media)
            continue
        show_infos.append(
            {"show_nr": show_nr, "show_name": show, "seasons": seasons, "episodes": episodes, "runtime": runtime, "show_size": size,
             "last_modified": last_modified})
        print(f"Show: {parts[0]}")
        show_nr += 1
        show = parts[0]
        seasons = 1
        episodes = 1
        last_modified = os.path.getmtime(media) if last_modified < os.path.getmtime(media) else last_modified
        size = os.path.getsize(media)
        runtime = get_duration(media)
    show_infos.append(
        {"show_nr": show_nr, "show_name": show, "seasons": seasons, "episodes": episodes, "runtime": runtime, "show_size": size,
         "last_modified": last_modified})

    return show_infos


def get_movie_infos(plex_path: AnyStr):
    movie_infos = []
    movie_nr = 1
    movie_name = ""
    year = 0
    version = "unique"
    for media in glob.glob(plex_path + f"{sep}**{sep}*.mp4", recursive=True) + \
                 glob.glob(plex_path + f"{sep}**{sep}*.mkv", recursive=True):
        filename = os.path.basename(media)
        print(f"Movie: {os.path.splitext(filename)[0]}")
        try:
            movie_name = re.search(r".+(?= \(\d{4}\))", filename).group()
            year = re.search(r"(?<=\()\d{4}(?=\))", filename).group()
        except AttributeError:
            print(f"Movie {filename} not properly named! Make sure its in 'Movie name (Year) - Version.ext' format.")
            exit(1)
        try:
            version = re.search(r"(?<=\(\d{4}\) - ).*(?=(.mp4)|(.mkv))", filename).group()
        except AttributeError:
            pass
        language = get_language(media)
        size = os.path.getsize(media)
        last_modified = os.path.getmtime(media)
        file_type = re.search(r"(?<=\.).+", filename).group()
        movie_infos.append(
            {"movie_nr": movie_nr, "movie_name": movie_name, "year": year,"language": language, "version": version, "size": size,
             "last_modified": last_modified, "file_type": file_type})
        movie_nr += 1
    return movie_infos


def write_to_csv(show_infos: List, filename="show_infos"):
    with open(filename + '.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Number', 'Name', 'Seasons', 'Episodes', 'Show size'])
        for show in show_infos:
            csvwriter.writerow(show.values())


def print_show_infos(show_infos: List):
    for show in show_infos:
        print(f"===== SHOW ======")
        print(f"Name: {show['show_name']}")
        print(f"Seasons: {show['seasons']}")
        print(f"Episodes: {show['episodes']}")
        print(f"Runtime: {convert_millis(show['runtime'])}")
        print(f"Last modified: {datetime.datetime.fromtimestamp(show['last_modified']).strftime('%Y-%m-%d, %H:%M')}")
        print(f"Show size: {round(show['show_size'] / (1024 ** 3), 2)} GB\n")
    return


def print_movie_infos(movie_infos: List):
    for movie in movie_infos:
        print(f"===== MOVIE ======")
        print(f"Name: {movie['movie_name']}")
        print(f"Year: {movie['year']}")
        print(f"Language: {movie['language']}")
        print(f"Version: {movie['version']}")
        print(f"Last modified: {datetime.datetime.fromtimestamp(movie['last_modified']).strftime('%Y-%m-%d, %H:%M')}")
        print(f"Movie size: {round(movie['size'] / (1024 ** 3), 2)} GB")
        print(f"File type: {movie['file_type']}\n")


def fetch_all(overall_path):
    overall_path = overall_path.rstrip(sep)
    if not check_ffmpeg():
        exit(1)
    info_shows = get_show_infos(overall_path + f"{sep}TV Shows")
    info_movies = get_movie_infos(overall_path + f"{sep}Movies")
    return info_shows, info_movies


if __name__ == '__main__':
    # P:\\Plex Shows
    # P:\\script_testing
    # info_shows, info_movies = fetch_all("P:\\Plex Shows")
    info_movies = get_movie_infos("P:\\Plex Shows\\Movies")
    # write_to_csv(info_movies, filename='movie_infos')
    print_movie_infos(info_movies)
    # print(f"Total size: {round(playground.sum_files(info_movies) / (1024 ** 3), 2)} GB")
    # write_to_csv(info)
