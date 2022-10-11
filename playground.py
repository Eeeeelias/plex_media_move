# just for testing I swear
import timeit
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


if __name__ == '__main__':
    start = timeit.default_timer()
    main()
    end = timeit.default_timer()
    print("Took: {:.2f}s".format(end-start))
    # delete()
