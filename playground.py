# just for testing I swear
import os
import sys
import time
from itertools import dropwhile

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


def time_info_reading():
    time_start = time.time()
    info_shows = fetch_infos.get_show_infos("P:\\Plex Shows\\TV Shows\\Parks and Recreation")
    print(info_shows)
    print(mediainfolib.convert_seconds(info_shows[0][4]))
    time_end = time.time()
    return time_end - time_start


conn = manage_db.create_connection(db_path)
print(manage_db.check_entry_ex("shows", conn.cursor(), (86, "JoJo's Bizarre Adventure", 5, 171, 245113, 42217537643, 1662149867.533148)))


sql = "SELECT * FROM shows WHERE name like '%jojo''s%' "

print(manage_db.custom_sql(db_path, sql))
