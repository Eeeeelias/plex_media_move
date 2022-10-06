import json
import os
import sys
import time

import mediainfolib
from mediainfolib import data_path, seperator
from prompt_toolkit import prompt, HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter
import fetch_infos
import manage_db

config_path = data_path + f"{seperator}config.json"


def ensure_path_ex(path):
    if path == "":
        return None
    while not os.path.isdir(path):
        path = prompt(HTML("<ansiblue>[a] This is not a valid path. Put in a valid path: </ansiblue>"),
                      completer=PathCompleter()).lstrip('"').rstrip('"')
    return path


def set_media_mover():
    print_formatted_text(HTML("[i] Default values for media_mover (ENTER to skip)"))
    _orig_path = prompt(HTML("<ansiblue>[a] Put in the default path where your unsorted media is: </ansiblue>"),
                        completer=PathCompleter()).lstrip('"').rstrip('"')
    orig_path = ensure_path_ex(_orig_path)
    _dest_path = prompt(HTML("<ansiblue>[a] Put in the default path where you want your media to go: </ansiblue>"),
                        completer=PathCompleter()).lstrip('"').rstrip('"')
    dest_path = ensure_path_ex(_dest_path)
    overwrite = prompt(HTML("<ansiblue>[a] Should the mover overwrite existing files? </ansiblue>[y/N] ")).lower()
    overwrite = True if overwrite == "y" else False
    special = prompt(HTML("<ansiblue>[a] Put in special values for the mover to consider: </ansiblue>"))
    return {"orig_path": orig_path, "dest_path": dest_path, "overwrite": overwrite, "special": special}


def set_combiner():
    print_formatted_text(HTML("\n[i] Default values for movie combiner (ENTER to skip)"))
    _default_out = prompt(
        HTML("<ansiblue>[a] Put in the default path where you want combined movies to be saved: </ansiblue>"),
        completer=PathCompleter()).lstrip('"').rstrip('"')
    default_out = ensure_path_ex(_default_out)
    ask_again = prompt(HTML("<ansiblue>[a] Do you want to be asked for the path regardless? </ansiblue>[y/N] "))
    ask_again = True if ask_again == "y" else False
    return {"default_out": default_out, "ask_again": ask_again}


def set_database():
    print_formatted_text(HTML("\n[i] Default values for your database (ENTER for default)"))
    _db_path = prompt(HTML("<ansiblue>[a] Put in the path where you want your database to be stored: </ansiblue>"),
                      completer=PathCompleter()).lstrip('"').rstrip('"')
    db_path = ensure_path_ex(_db_path)
    if db_path is None:
        db_path = data_path
    return {"db_path": db_path}


def set_config():
    mover = {}
    combiner = {}
    database = {}
    if not os.path.exists(config_path):
        open(config_path, 'a').close()
    try:
        mover = set_media_mover()
        combiner = set_combiner()
        database = set_database()
    except KeyboardInterrupt:
        print("Aborting")
        exit(0)

    print_formatted_text(HTML("[i] Saving config at: {}\n".format(config_path)))
    json.dump({"mover": mover, "combiner": combiner, "database": database}, open(config_path, 'w'))
    create_db = prompt(HTML("<ansiblue>[a] Do you want to create the database now (If you already have a database it "
                            "will be deleted)? </ansiblue>[y/N] "))
    if create_db.lower() == "y":
        db_path = database['db_path'] + f"{seperator}media_database.db"
        _plex_path = prompt(HTML("<ansiblue>[a] Put in the path to your plex files: </ansiblue>"),
                            completer=PathCompleter()).lstrip('"').rstrip('"')
        plex_path = ensure_path_ex(_plex_path)
        info_shows, info_movies = fetch_infos.fetch_all(plex_path)
        manage_db.create_database(plex_path, db_path, info_shows, info_movies)
    print_formatted_text("[i] All done!")
    exit(0)


def redo_db(reindex=False):
    start = time.time()
    conf = mediainfolib.get_config()
    if conf['mover']['dest_path'] is not None:
        plex_path = conf['mover']['dest_path']
    else:
        _plex_path = prompt(HTML("<ansiblue>Put in the path to your plex files: </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
        plex_path = ensure_path_ex(_plex_path)
    db_path = conf['database']['db_path'] + f"{seperator}media_database.db"
    if not reindex:
        print("[i] Rebuilding database... (this could take a while)")
        info_shows, info_movies = fetch_infos.fetch_all(plex_path)
    else:
        info_shows = fetch_infos.update_shows(db_path, plex_path)
        info_movies = fetch_infos.get_movie_infos(plex_path + f"{seperator}Movies")
    if os.path.exists(db_path):
        os.remove(db_path)
    manage_db.create_database(plex_path, db_path, info_shows, info_movies)
    end = time.time()
    print("[i] Rebuilding the database finished in {} minutes".format(round((end-start) / 60.0, 2)))


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == '-db':
                redo_db()
        else:
            set_config()
    except KeyboardInterrupt:
        print("Exiting")
