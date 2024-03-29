import concurrent.futures
import csv
import datetime
import glob
import os
import random
import re
from itertools import dropwhile
from typing import AnyStr, List
from sys import exit
from src.mediainfolib import get_duration_cv2, check_ffmpeg, get_language, seperator, \
    convert_seconds, get_duration, get_config, config_path, season_episode_matcher

sep = seperator


def latest_modified(show):
    # 0 in case some show is behaving weirdly
    modified = [0]
    episodes = glob.glob(show + "/**/*.mkv") + glob.glob(show + "/**/*.mp4")
    for episode in episodes:
        modified.append(os.path.getmtime(episode))
    return max(modified)


def get_show_infos(plex_path: str, nr=1) -> list[tuple]:
    if not os.path.exists(plex_path):
        return []
    _info_shows = []
    info_shows = []
    if os.path.basename(plex_path) != "TV Shows" and os.path.basename(plex_path) != "Anime":
        _info_shows = [search_show(plex_path)]
    else:
        shows_to_check = [plex_path + sep + i for i in os.listdir(plex_path)]
        for show in shows_to_check:
            _info_shows.append(search_show(show))

    id = nr
    for i in range(len(_info_shows)):
        if _info_shows[i][3] > 0:
            _info_shows[i][0] = id
            info_shows.append(tuple(_info_shows[i]))
            id += 1
    return info_shows

# doesn't work with anime
def get_episode_infos(plex_path: str) -> list[list]:
    _info_episodes = []
    used_ids = []
    if os.path.basename(plex_path) != "TV Shows":
        _info_episodes, new_ids = search_episodes(plex_path, used_ids=used_ids)
    else:
        shows_to_check = [plex_path + sep + i for i in os.listdir(plex_path)]
        for show in shows_to_check:
            episodes, new_ids = search_episodes(show, used_ids=used_ids)
            _info_episodes.extend(episodes)
    used_ids.extend(new_ids)
    return _info_episodes


def search_episodes(show: str, used_ids) -> tuple[list[list], list]:
    show_name = os.path.basename(show)
    _show_type = "TV Shows" if os.path.basename(os.path.dirname(show)) == "TV Shows" else "Anime"
    print("[i] Show: {}".format(show_name))
    episodes = []
    db = get_config(config_path)['database']['db_path'] + "\\media_database.db"
    # used_ids = []

    for episode in glob.glob(show + f"{sep}**{sep}*.mp4") + glob.glob(show + f"{sep}**{sep}*.mkv"):
        parts = list(dropwhile(lambda x: x != _show_type, episode.split(sep)))[1:]
        # parts gives [show, season, episode]
        id = str(random.randint(10000000, 99999999))
        while int(id) in used_ids:
            id = str(random.randint(10000000, 99999999))
        used_ids.append(int(id))
        season, ep_num = season_episode_matcher(parts[2])
        size = os.path.getsize(episode)
        last_modified = os.path.getmtime(episode)
        runtime = get_duration_cv2(episode)
        episodes.append([id, parts[0], season, ep_num, runtime, size, last_modified])
    return episodes, used_ids


def search_show(show):
    show_name = os.path.basename(show)
    _show_type = "TV Shows" if os.path.basename(os.path.dirname(show)) == "TV Shows" else "Anime"
    print("[i] Show: {}".format(show_name) if _show_type == "TV Shows" else "[i] Anime: {}".format(show_name))
    episodes = 0
    seasons = 0
    size = 0
    last_modified = 0
    runtime = 0
    for episode in glob.glob(show + f"{sep}**{sep}*.mp4") + glob.glob(show + f"{sep}**{sep}*.mkv"):
        parts = list(dropwhile(lambda x: x != _show_type, episode.split(sep)))[1:]
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
            movie_name = filename
            year = 1900
        try:
            version = re.search(r"(?<=\(\d{4}\) - ).*(?=(.mp4)|(.mkv))", filename).group()
        except AttributeError:
            version = "unique"
        language = ";".join(get_language(media))
        runtime = get_duration(media)
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


def fetch_all(overall_path) -> tuple[List[tuple], List[tuple], List[tuple]]:
    overall_path = overall_path.rstrip(sep)
    if not check_ffmpeg():
        exit(1)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(x, y) for x, y in zip([get_show_infos, get_show_infos, get_movie_infos],
                                                         [overall_path + f"{sep}TV Shows",
                                                          overall_path + f"{sep}Anime",
                                                          overall_path + f"{sep}Movies"])]
        results = [f.result() for f in futures]
    # info_shows = get_show_infos(overall_path + f"{sep}TV Shows")
    # info_movies = get_movie_infos(overall_path + f"{sep}Movies")
    return results[0], results[1], results[2]


def reindex_shows(db_path: str, plex_path: str, type: str) -> List[tuple]:
    from src.manage_db import custom_sql
    _show_type = "TV Shows" if type == "shows" else "Anime"
    _info_shows = []
    info_shows = []
    show_dirs = glob.glob(plex_path + f"{sep}{_show_type}{sep}*")
    for show in show_dirs:
        name = os.path.split(show)[1]
        sql = f"""SELECT * FROM {type} WHERE name='{name.replace("'", "''")}'"""
        existing_info = custom_sql(db_path, sql)
        if len(existing_info) > 0:
            last_modified = latest_modified(show)
            if existing_info[0][6] == last_modified:
                print("[i] Show: {}".format(name) if _show_type == "TV Shows" else "[i] Anime: {}".format(name))
                _info_shows.append(list(existing_info[0]))
                continue
        _info_shows.append(search_show(show))

    id = 1
    for i in range(len(_info_shows)):
        if _info_shows[i][3] > 0:
            _info_shows[i][0] = id
            info_shows.append(tuple(_info_shows[i]))
            id += 1
    return info_shows


def reindex_movies(db_path: str, plex_path: str) -> List[tuple]:
    from src.manage_db import custom_sql
    _info_movies = []
    info_movies = []
    plex_path = plex_path + f"{sep}Movies"
    paths_to_check = glob.glob(plex_path + f"{sep}**{sep}*.mp4", recursive=True) + glob.glob(
        plex_path + f"{sep}**{sep}*.mkv", recursive=True)

    for media in paths_to_check:
        file_name = os.path.splitext(os.path.basename(media))[0]
        matches = re.search(r"(.*) \((\d+)\) - (.*)", file_name)
        try:
            name = matches.group(1)
            year = matches.group(2)
            version = matches.group(3)
            sql = f"""SELECT * FROM main.movies WHERE name='{name.replace("'", "''")}' 
                                                  AND year={year} 
                                                  AND version='{version.replace("'", "''")}' """
        except AttributeError:
            try:
                matches = re.search(r"(.*) \((\d+)\)", file_name)
                name = matches.group(1)
                year = matches.group(2)
                sql = f"""SELECT * FROM main.movies WHERE name='{name.replace("'", "''")}' AND year={year}"""
            except AttributeError:
                print(f"[w] Error with {file_name}, moving on")
                continue
        existing_info = custom_sql(db_path, sql)
        if len(existing_info) > 0:
            last_modified = os.path.getmtime(media)
            if existing_info[0][7] == last_modified:
                print("[i] Movie: {}".format(name))
                _info_movies.append(list(existing_info[0]))
                continue
        _info_movies.append(list(get_movie_infos(media)[0]))
    id = 1
    for i in range(len(_info_movies)):
        _info_movies[i][0] = id
        info_movies.append(tuple(_info_movies[i]))
        id += 1
    return info_movies
