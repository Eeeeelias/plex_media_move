import os.path
import sqlite3
import time
from datetime import datetime
from sqlite3 import Error
from typing import List
from mediainfolib import convert_millis, convert_country, cut_name, convert_size, add_minus, convert_seconds, \
    seperator as sep
import fetch_infos


def create_connection(db_file) -> sqlite3.Connection:
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def create_table(conn, sql_table) -> bool:
    try:
        curse = conn.cursor()
        curse.execute(sql_table)
    except Error as e:
        print(e)
        return False
    return True


def add_to_db(conn, table, media) -> tuple:
    if table == "show":
        sql = """INSERT INTO shows(id, name, seasons, episodes, runtime, size, modified)
                 VALUES(?,?,?,?,?,?,?)"""
    else:
        sql = """INSERT INTO movies(id, name, year, language, version, runtime, size, modified, type)
                 VALUES(?,?,?,?,?,?,?,?,?)"""
    curse = conn.cursor()
    curse.execute(sql, media)
    conn.commit()
    return curse.lastrowid


def create_database(plex_path, db_path, info_shows: List[tuple], info_movies: List[tuple]) -> None:
    if not os.path.exists(db_path):
        open(db_path, 'a').close()
    sql_create_shows = """ CREATE TABLE IF NOT EXISTS shows (
                                 id integer PRIMARY KEY,
                                 name text NOT NULL,
                                 seasons integer,
                                 episodes integer,
                                 runtime integer,
                                 size integer,
                                 modified real
                            );"""
    sql_create_movies = """ CREATE TABLE IF NOT EXISTS movies (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                year integer,
                                language text,
                                version text,
                                runtime integer,
                                size integer,
                                modified real,
                                type text
                            );"""
    connection = create_connection(db_path)
    shows = create_table(connection, sql_create_shows)
    if shows:
        print("[i] Shows created")
    else:
        print("[i] There was an error!")
    movies = create_table(connection, sql_create_movies)
    if movies:
        print("[i] Movies created")
    else:
        print("[i] There was an error!")
    for show in info_shows:
        last_show_id = add_to_db(connection, "show", show)
        # print(f"[i] Show {show[1]} added!")
    for movie in info_movies:
        last_movie_id = add_to_db(connection, "movie", movie)
        # print(f"[i] Movie {movie[1]} added!")
    cur = connection.cursor()
    cur.execute("SELECT name FROM shows")
    list_shows = list(cur.fetchall())
    completeness_check(plex_path + f"{sep}TV Shows", [x[0] for x in list_shows])
    # cur.execute("SELECT name FROM movies")
    # list_movies = list(cur.fetchall())
    # completeness_check(plex_path + f"{sep}Movies", list_movies)
    print(f"[i] {last_show_id} Shows now in the database!")
    print(f"[i] {last_movie_id} Movies now in the database!")


def update_database(additions: set[str], db) -> None:
    conn = create_connection(db)
    cur = conn.cursor()
    mov_new_cha = float('inf')
    sho_new_cha = float('inf')
    for added in additions:
        if f"Movies" in added:
            info = fetch_infos.get_movie_infos(added, nr=get_max_id("movies", cur)[0] + 1)[0]
            mov_new_cha = info[7] if mov_new_cha > info[7] else mov_new_cha
            pos_ex = check_entry_ex("movies", cur, info)
            if pos_ex is not None:
                tmp = list(info)
                tmp[0] = pos_ex
                info = tuple(tmp)
                update_sql("movies", cur, info)
                continue
            add_sql("movies", cur, info)
        else:
            info = fetch_infos.get_show_infos(added, nr=get_max_id("shows", cur)[0] + 1)[0]
            sho_new_cha = info[6] if sho_new_cha > info[6] else sho_new_cha

            pos_ex = check_entry_ex("shows", cur, info)
            if pos_ex is not None:
                tmp = list(info)
                tmp[0] = pos_ex
                info = tuple(tmp)
                update_sql("shows", cur, info)
                continue
            add_sql("shows", cur, info)
    conn.commit()
    if mov_new_cha < float('inf'):
        print("[i] New/Changed movies in the database:\n")
        res = prettify_out("movies", get_newest("movies", mov_new_cha, db))
        print(res)
    if sho_new_cha < float('inf'):
        print("[i] New/Changed shows in the database:\n")
        res = prettify_out("shows", get_newest("shows", sho_new_cha, db))
        print(res)
    return


def get_max_id(table, cursor: sqlite3.Cursor) -> tuple[int]:
    if table == "movies":
        return cursor.execute("SELECT MAX(id) FROM movies").fetchone()
    elif table == "shows":
        return cursor.execute("SELECT MAX(id) FROM shows").fetchone()
    return (1,)


def check_entry_ex(table: str, cursor: sqlite3.Cursor, info: tuple):
    possible_ex = None
    if table == "movies":
        possible_ex = cursor.execute(f"SELECT * FROM movies WHERE name='{info[1]}' AND version='{info[4]}'").fetchone()
    elif table == "shows":
        possible_ex = cursor.execute(f"SELECT * FROM shows WHERE name='{info[1]}'").fetchone()
    if possible_ex is not None:
        print("[i] Entry already found, updating existing")
        return possible_ex[0]
    print("[i] New entry detected")
    return None


def update_sql(table: str, cur: sqlite3.Cursor, info: tuple) -> None:
    sql_movie = """UPDATE movies
                  SET language = ?,
                      runtime = ?,
                      modified = ?,
                      size = ?,
                      type = ?
                  WHERE id = ?"""
    sql_show = """UPDATE shows 
                 SET seasons = ?,
                     episodes = ?,
                     runtime = ?,
                     size = ?,
                     modified = ?
                 WHERE id = ?"""

    if table == "movies":
        info_sql = (info[3], info[5], info[6], info[7], info[8], info[0])
        cur.execute(sql_movie, info_sql)
    elif table == "shows":
        info_sql = (info[2], info[3], info[4], info[5], info[6], info[0])
        cur.execute(sql_show, info_sql)


def add_sql(table: str, cur: sqlite3.Cursor, info: tuple) -> None:
    sql_movie = "INSERT INTO movies VALUES (?,?,?,?,?,?,?,?,?)"
    sql_shows = "INSERT INTO shows VALUES (?,?,?,?,?,?,?)"
    if table == "movies":
        cur.execute(sql_movie, info)
    elif table == "shows":
        cur.execute(sql_shows, info)


def delete_entry(table: str, cur: sqlite3.Cursor, id: int) -> None:
    if table == "movies":
        cur.execute("SELECT name FROM movies where id=?", (id,))
        print("[i] Deleting \'{}\'.".format(cur.fetchone()[0]))
        time.sleep(3)
        cur.execute("DELETE FROM movies WHERE id= ?", (id,))
    if table == "shows":
        cur.execute("SELECT name FROM shows where id=?", (id,))
        print("[i] Deleting \'{}\'.".format(cur.fetchone()[0]))
        time.sleep(3)
        cur.execute("DELETE FROM shows WHERE id= ?", (id,))


# returns movies that contain the search word
def get_movies(search: str, db_path: str, order='name', desc=True) -> list[tuple]:
    sort = "ASC" if not desc else "DESC"
    sql = f"SELECT * FROM movies WHERE name like '%{search}%' ORDER BY {order} {sort}"
    conn = create_connection(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return rows


def get_shows(search: str, db_path: str, order='name', desc=True) -> list[tuple]:
    sort = "ASC" if not desc else "DESC"
    sql = f"SELECT * FROM shows WHERE name like '%{search}%' ORDER BY {order} {sort}"
    conn = create_connection(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return rows


def get_newest(table: str, search: float, db_path: str):
    cur = create_connection(db_path).cursor()
    sql_show = f"SELECT * FROM shows WHERE modified >= '{search}' ORDER BY modified"
    sql_movie = f"SELECT * FROM movies WHERE modified >= '{search}' ORDER BY modified"
    if table == "movies":
        cur.execute(sql_movie)
    elif table == "shows":
        cur.execute(sql_show)
    return cur.fetchall()


def get_specific(db_path: str, sql: str):
    cur = create_connection(db_path).cursor()
    cur.execute(sql)
    return cur.fetchall()


def completeness_check(path, db_names) -> None:
    shows_list = [x for x in os.listdir(path)]

    for i in shows_list:
        if i not in db_names:
            print(f"[i] \'{i}\' not in your database!")


def prettify_out(table: str, rows: List[tuple]) -> str:
    if rows is None:
        return ""
    if table == 'movies':
        return prettify_movies(rows)
    elif table == 'shows':
        return prettify_shows(rows)
    return ""


def prettify_movies(rows: List[tuple]) -> str:
    max_len_names = os.get_terminal_size().columns - 96 - 12
    db_out = ""
    stopper = "    " + "".join([add_minus() for i in range(max_len_names + 96)]) + "\t\n"
    head = "    | ID  | Name{:%d}| Year | Language{:7} | Version{:3} | Runtime | Size{:4} | Added{:12} | Type |\t\n" % (
                max_len_names - 3)
    empty_res = "    | {:4}   {:%d}   {:7}   {:8}   {:9}   {:17}   {:26}    |\t\n" % max_len_names
    movie_row = "    | {0:3} | {1:%d} | {2} | {3:15} | {4:10} | {5:6}  | {6:5} GB | {7} | {8} |\t\n" % max_len_names
    error_row = "    | {0:3} | {1:%d} | {2} | {3:15} | {4:10} | {5:6}  | {6:5} GB | {7} | {8} |\t\n" % max_len_names
    db_out += stopper
    db_out += head.format("", "", "", "", "")
    db_out += stopper
    if len(rows) == 0:
        db_out += empty_res.format("None", "", "", "", "", "", "")
    for row in rows:
        try:
            db_out += movie_row.format(row[0], cut_name(row[1], max_len_names), row[2], convert_country(row[3]), row[4],
                                       convert_millis(row[5]), round(row[6] / (1024 ** 3), 2),
                                       datetime.fromtimestamp(row[7]).strftime('%Y-%m-%d, %H:%M'), row[8])
        except OSError:
            db_out += error_row.format("N/A", "ERROR", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")
    db_out += stopper
    return db_out


def prettify_shows(rows: List[tuple]) -> str:
    max_len_names = os.get_terminal_size().columns - 75 - 12
    print("Max len names", max_len_names)
    db_out = ""
    stopper = "    " + "".join([add_minus() for i in range(max_len_names + 75)]) + "\t\n"
    head = "    | ID  | Name{:%d}| Seasons | Episodes | Runtime{:2} | Added{:12} | Size{:5} |\t\n" % (max_len_names - 3)
    empty_res = "    | {:4}   {:%d}   {:7}   {:8}   {:9}   {:17}   {:5}    |\t\n" % max_len_names
    shows_row = "    | {0:3} | {1:%d} | {2:7} | {3:8} | {4:9} | {5:17} | {6:6} GB |\t\n" % max_len_names
    error_row = "    | {:3} | {:%d} | {:7} | {:8} | {:9} | {:17} | {:6} GB |\t\n" % max_len_names
    db_out += stopper
    db_out += head.format("", "", "", "")
    db_out += stopper
    if len(rows) == 0:
        db_out += empty_res.format("None", "", "", "", "", "", "")
    for row in rows:
        try:
            db_out += shows_row.format(row[0], cut_name(row[1], max_len_names), row[2], row[3], convert_seconds(row[4]),
                                       datetime.fromtimestamp(row[6]).strftime('%Y-%m-%d, %H:%M'), convert_size(row[5]))
        except OSError:
            db_out += error_row.format("N/A", "ERROR", "N/A", "N/A", "N/A", "N/A", "N/A")
            continue
    db_out += stopper
    return db_out


def custom_sql(db_path: str, sql: str) -> list:
    cur = None
    try:
        cur = create_connection(db_path).cursor()
        cur.execute(sql)
    except Error as e:
        print(e)
        print("Your query doesn't work like this. See above for exact error.")
    return cur.fetchall()
