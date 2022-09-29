# just for testing I swear
import os
import random
import sys
import time
from itertools import dropwhile

import db_infos
import fetch_infos
import mediainfolib
from mediainfolib import seperator
import manage_db

conf = mediainfolib.get_config()
db_path = conf['database']['db_path'] + f"{seperator}media_database.db"
sep = seperator

env = 'LOCALAPPDATA'
folder = 'pmm'
data_path = os.getenv(env) + seperator + folder

conf_path = data_path + f"{seperator}config.json"
plex_path = "P:\\Plex Shows\\TV Shows"


def main():
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        info_shows = fetch_infos.fetch_all("P:\\Plex Shows")

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename="profiling_without_threading.prof")


if __name__ == '__main__':
    main()