# just for testing I swear
import glob
import os
import random
import re
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
    for path in glob.glob("P:\\Plex Shows\\Movies\\*.mp4"):
        checksum = fetch_infos.sha256_for_file(path)
        print(checksum)


if __name__ == '__main__':
    print(re.search("\.", "blablabla").group())
