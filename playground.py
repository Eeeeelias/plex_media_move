# just for testing I swear
import re
import os
from prompt_toolkit import prompt, HTML
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
    for i in range(13, 201):
        open(f"P:\\script_testing\\Detektiv Conan s01e0{i}.mp4", "a").close()


if __name__ == '__main__':
    main()
