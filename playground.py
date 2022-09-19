# just for testing I swear
import os
import mediainfolib
from mediainfolib import seperator
import manage_db

conf = mediainfolib.get_config()
db_path = conf['database']['db_path'] + f"{seperator}media_database.db"
sep = seperator

env = 'LOCALAPPDATA'
folder = 'pmm'
data_path = os.getenv(env) + seperator + folder

conf_path = "C:\\Users\\gooog\\AppData\\Local\\pmm\\config.json"
# conf_path = data_path + f"{seperator}config.json"
plex_path = "P:\\Plex Shows\\TV Shows"


def check_db_for_missing(plex_path):
    actual_folders = os.listdir(plex_path)
    db_found = [x[1] for x in manage_db.get_shows("", db_path)]

    for i in actual_folders:
        if i not in db_found:
            print("{} not found!".format(i))


print(f"file: {conf_path}")
print(os.path.getsize(conf_path))
