import os
import manage_db
import sys
from media_mover import data_path

db_path = data_path
# db_path = "test_db.db"

if input("Would you like to look for a [s]how or a [m]ovie? ") == "s":
    show = input("Put in a name for your search: ")
    res = manage_db.get_shows(search=show, db_path=db_path)
else:
    movie = input("Put in a name for your search: ")
    res = manage_db.get_shows(search=movie, db_path=db_path)

manage_db.print_shows(res)
