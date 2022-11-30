# just for testing I swear
import glob
import timeit
from difflib import SequenceMatcher as SM

import src.manage_db
from src import mediainfolib
from src.mediainfolib import seperator
from src.manage_db import *

conf = mediainfolib.get_config()
db_path = conf['database']['db_path'] + f"{seperator}media_database.db"
sep = seperator

env = 'LOCALAPPDATA'
folder = 'pmm'
data_path = os.getenv(env) + seperator + folder

conf_path = data_path + f"{seperator}config.json"
plex_path = "P:\\Plex Shows\\TV Shows"


def make_data():
    data = []
    for i in range(1_000_000):
        tmp = [i, f"test{i}", i, i, i, i, i]
        data.append(tmp)
    return data


def main():
    pass


def num_videos():
    num_shows = src.manage_db.custom_sql(db_path, "SELECT SUM(episodes) FROM main.shows")[0][0]
    num_movies = src.manage_db.custom_sql(db_path, "SELECT COUNT(id) FROm main.movies")[0][0]
    return f"[i] You have {num_movies + num_shows} video files in your library!"


if __name__ == '__main__':
    dur = 0
    music = glob.glob("P:\\Music\\Music\\**\\*.mp3") + glob.glob("P:\\Music\\Music\\**\\*.m4a") + glob.glob("P:\\Music\\Music\\**\\*.wma")
    for i in music:
        dur += mediainfolib.get_duration(i)
        print(f"{i}: {dur}")
    print(mediainfolib.convert_millis(dur))
    ratio = SM(None, "Shokugeki no Souma", "Shokugeki no Souma: Ni no Sara").ratio()
    print(ratio)

