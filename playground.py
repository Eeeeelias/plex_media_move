import os

import fetch_show_infos
import manage_db

db_path = os.getenv('LOCALAPPDATA') + "\\pmm\\media_database.db"
# db_path = "test_db.db"

# info_shows, info_movies = fetch_show_infos.fetch_all("P:\\script_testing")
# manage_db.create_database(db_path, info_shows, info_movies)
manage_db.get_movies(search="Die", db_path=db_path, order="year", desc=True)
conn = manage_db.create_connection(db_path)
cur = conn.cursor()

# infos = fetch_show_infos.get_show_infos("P:\\script_testing\\TV Shows\\Aho Girl")[0]
# tmp_infos = list(infos)
# tmp_infos[0] = 1
# tmp_infos[2] = "6"
# tmp_infos[3] = "24"
# infos = tuple(tmp_infos)

# manage_db.update_sql("shows", cur, infos)
# conn.commit()
movies = manage_db.get_shows(search="Pa", db_path=db_path, order="runtime")
manage_db.print_shows(movies)
movies_newest_changes = float('inf')
movies_newest_changes = 5
if movies_newest_changes < float('inf'):
    print(True)
else:
    print(False)
print(movies_newest_changes)
