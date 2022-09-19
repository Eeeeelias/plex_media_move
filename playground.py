# just for testing I swear
import glob
import os

import mediainfolib
from mediainfolib import seperator, data_path
import manage_db

db_path = data_path + f"{seperator}media_database.db"
sep = seperator

plex_path = "P:\\Plex Shows\\TV Shows"

actual_folders = os.listdir(plex_path)
db_found = [x[1] for x in manage_db.get_shows("", db_path)]

for i in actual_folders:
    if i not in db_found:
        print("{} not found!".format(i))


conf = mediainfolib.get_config()
orig_path = conf['mover']['orig_path']
plex_path = conf['mover']['dest_path']
special = conf['mover']['special'].split(" ")
print(len(special))
data_path = conf['database']['db_path']
db_path = data_path + f"{seperator}media_database.db"

print(os.path.isfile(""))
