import os

import fetch_infos
import manage_db

db_path = os.getenv('LOCALAPPDATA') + "\\pmm\\media_database.db"
# db_path = "test_db.db"


res = manage_db.get_shows(search="Yome", db_path=db_path)
manage_db.print_shows(res)

res = manage_db.get_newest("shows", 1663504832.285441, db_path)