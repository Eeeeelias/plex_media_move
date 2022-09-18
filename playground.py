import datetime
import os
from sys import argv
import manage_db
from media_mover import data_path
from mediainfolib import seperator, convert_millis

# db_path = data_path + f"{seperator}media_database.db"
if argv[1] is not None and os.path.isfile(argv[1]):
    db_path = argv[1]
else:
    db_path = "D:\\Downloads\\Telegram Desktop\\media_database.db"
db_path = data_path + f"{seperator}media_database.db"

print("Looking at: {}".format(db_path))
while 1:
    try:
        if input("Would you like to look for a [s]how or a [m]ovie? ") == "s":
            show = input("Put in a name for your search: ")
            res = manage_db.get_shows(search=show, db_path=db_path)
            manage_db.print_shows(res)
        else:
            movie = input("Put in a name for your movie search: ")
            res = manage_db.get_movies(search=movie, db_path=db_path, order='id', desc=False)
            manage_db.print_movies(res)
        next = input("Would you like to make another search? [y/N] ")
        if next.lower() == "n":
            exit(0)
        elif next.lower() == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
    except KeyboardInterrupt:
        print("\nFinishing")
        exit(0)
