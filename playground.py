import os
from datetime import datetime

import pycountry

import fetch_infos
import manage_db
import sys
from media_mover import data_path
from mediainfolib import seperator, convert_millis

db_path = data_path + f"{seperator}media_database.db"


if input("Would you like to look for a [s]how or a [m]ovie? ") == "s":
    show = input("Put in a name for your search: ")
    res = manage_db.get_shows(search=show, db_path=db_path)
    manage_db.print_shows(res)
else:
    movie = input("Put in a name for your movie search: ")
    res = manage_db.get_movies(search=movie, db_path=db_path, order='id', desc=False)
    manage_db.print_movies(res)
