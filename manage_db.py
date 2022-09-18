import os.path
import sqlite3
from datetime import datetime
from sqlite3 import Error
from typing import List

import fetch_infos
from mediainfolib import convert_millis, convert_country, cut_name, convert_size


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


def add_to_db(conn, type, media) -> tuple:
    if type == "show":
        sql = """INSERT INTO shows(id, name, seasons, episodes, runtime, size, modified)
                 VALUES(?,?,?,?,?,?,?)"""
    else:
        sql = """INSERT INTO movies(id, name, year, language, version, runtime, size, modified, type)
                 VALUES(?,?,?,?,?,?,?,?,?)"""
    curse = conn.cursor()
    curse.execute(sql, media)
    conn.commit()
    return curse.lastrowid


def create_database(db_path, info_shows: List[tuple], info_movies: List[tuple]) -> None:
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
        print_movies(get_newest("movies", mov_new_cha, db))
    if sho_new_cha < float('inf'):
        print("[i] New/Changed shows in the database:\n")
        print_shows(get_newest("shows", mov_new_cha, db))
    return


def add_minus():
    return "-"


def get_max_id(type, cursor: sqlite3.Cursor) -> tuple[int]:
    if type == "movies":
        return cursor.execute("SELECT MAX(id) FROM movies").fetchone()
    elif type == "shows":
        return cursor.execute("SELECT MAX(id) FROM shows").fetchone()
    return (1,)


def check_entry_ex(type: str, cursor: sqlite3.Cursor, info: tuple):
    possible_ex = None
    if type == "movies":
        possible_ex = cursor.execute(f"SELECT * FROM movies WHERE name='{info[1]}' AND version='{info[4]}'").fetchone()
    elif type == "shows":
        possible_ex = cursor.execute(f"SELECT * FROM shows WHERE name='{info[1]}'").fetchone()
    if possible_ex is not None:
        print("[i] Entry already found, updating existing")
        return possible_ex[0]
    print("[i] New entry detected")
    return None


def update_sql(type: str, cur: sqlite3.Cursor, info: tuple) -> None:
    sql_movie = """UPDATE movies
                  SET language = ?,
                      runtime = ?,
                      size = ?,
                      modified = ?,
                      type = ?
                  WHERE id = ?"""
    sql_show = """UPDATE shows 
                 SET seasons = ?,
                     episodes = ?,
                     runtime = ?,
                     modified = ?,
                     size = ?
                 WHERE id = ?"""

    if type == "movies":
        info_sql = (info[3], info[5], info[6], info[7], info[8], info[0])
        cur.execute(sql_movie, info_sql)
    elif type == "shows":
        info_sql = (info[2], info[3], info[4], info[5], info[6], info[0])
        cur.execute(sql_show, info_sql)


def add_sql(type: str, cur: sqlite3.Cursor, info: tuple) -> None:
    sql_movie = "INSERT INTO movies VALUES (?,?,?,?,?,?,?,?,?)"
    sql_shows = "INSERT INTO shows VALUES (?,?,?,?,?,?,?)"
    if type == "movies":
        cur.execute(sql_movie, info)
    elif type == "shows":
        cur.execute(sql_shows, info)


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


def get_newest(type: str, search: float, db_path: str):
    cur = create_connection(db_path).cursor()
    sql_show = f"SELECT * FROM shows WHERE modified = '{search}' ORDER BY modified"
    sql_movie = f"SELECT * FROM movies WHERE modified = '{search}' ORDER BY modified"
    if type == "movies":
        cur.execute(sql_movie)
    elif type == "shows":
        cur.execute(sql_show)
    return cur.fetchall()


def print_movies(rows: List[tuple]) -> None:
    # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    print("".join([add_minus() for i in range(146)]))
    print(
        "| ID  | Name{:47}| Year | Language{:7} | Version{:3} | Runtime | Size{:4} | Added{:12} | Type |".format("", "",
                                                                                                                 "", "",
                                                                                                                 ""))
    print("".join([add_minus() for i in range(146)]))
    for row in rows:
        print("| {0:3} | {1:50} | {2} | {3:15} | {4:10} | {5:6}  | {6:5} GB | {7} | {8}  |".format(row[0],
                                                                                                   cut_name(
                                                                                                       row[1]),
                                                                                                   row[2],
                                                                                                   convert_country(
                                                                                                       row[3]),
                                                                                                   row[4],
                                                                                                   convert_millis(
                                                                                                       row[5]),
                                                                                                   round(
                                                                                                       row[6] / (
                                                                                                               1024 ** 3),
                                                                                                       2),
                                                                                                   datetime.fromtimestamp(
                                                                                                       row[7]).strftime(
                                                                                                       '%Y-%m-%d, %H:%M'),
                                                                                                   row[8]))
    print("".join([add_minus() for i in range(146)]))


def print_shows(rows: List[tuple]) -> None:
    # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    print("".join([add_minus() for i in range(125)]))
    print(
        "| ID  | Name{:47}| Seasons | Episodes | Runtime{:2} | Added{:12} | Size{:5} |".format("", "", "", ""))
    print("".join([add_minus() for i in range(125)]))
    for row in rows:
        print("| {0:3} | {1:50} | {2:7} | {3:8} | {4:9} | {5} | {6:6} GB |".format(row[0], cut_name(row[1]), row[2],
                                                                               row[3], convert_millis(row[4]),
                                                                               datetime.fromtimestamp(row[6]).strftime(
                                                                                   '%Y-%m-%d, %H:%M'),
                                                                               convert_size(row[5])))
    print("".join([add_minus() for i in range(125)]))
