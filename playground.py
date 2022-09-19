# just for testing I swear
import concurrent.futures
import glob
import os
import re
import time
from itertools import dropwhile

import fetch_infos
import mediainfolib
from mediainfolib import seperator, sorted_alphanumeric, get_duration
import manage_db

conf = mediainfolib.get_config()
db_path = conf['database']['db_path'] + f"{seperator}media_database.db"
sep = seperator

env = 'LOCALAPPDATA'
folder = 'pmm'
data_path = os.getenv(env) + seperator + folder

conf_path = data_path + f"{seperator}config.json"
plex_path = "P:\\Plex Shows\\TV Shows"


def check_db_for_missing(plex_path):
    actual_folders = os.listdir(plex_path)
    db_found = [x[1] for x in manage_db.get_shows("", db_path)]

    for i in actual_folders:
        if i not in db_found:
            print("{} not found!".format(i))


def time_info_reading():
    time_start = time.time()
    info_shows = fetch_infos.get_show_infos("P:\\Plex Shows\\TV Shows\\Sankarea")
    print(info_shows)
    time_end = time.time()
    return time_end - time_start


print(time_info_reading())
# print("Runtime: {}s".format(get_infos()))

