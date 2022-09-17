import os.path
import sqlite3
from datetime import datetime
from sqlite3 import Error
from typing import List

from mediainfolib import convert_millis, convert_country, cut_movie_name


def create_connection(db_file):
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
        return 0
    return 1


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
        print(f"[i] Show {show[1]} added!")
    for movie in info_movies:
        last_movie_id = add_to_db(connection, "movie", movie)
        print(f"[i] Movie {movie[1]} added!")
    print(f"[i] {last_show_id} Shows now in the database!")
    print(f"[i] {last_movie_id} Movies now in the database!")


def update_database(additions: List):
    pass


def add_minus():
    return "-"


def get_item(search, db_path) -> None:
    sql = f"SELECT * FROM movies WHERE name like '%{search}%' ORDER BY name"
    conn = create_connection(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    print("".join([add_minus() for i in range(146)]))
    print(
        "| ID  | Name{:47}| Year | Language{:7} | Version    | Runtime | Size     | Added{:12} | Type |".format("", "" ,""))
    print("".join([add_minus() for i in range(146)]))
    for row in rows:
        print("| {0:3} | {1:50} | {2} | {3:15} | {4:10} | {5:6}  | {6:5} GB | {7} | {8}  |".format(row[0],
                                                                                               cut_movie_name(row[1]),
                                                                                               row[2],
                                                                                               convert_country(row[3]),
                                                                                               row[4],
                                                                                               convert_millis(row[5]),
                                                                                               round(
                                                                                                   row[6] / (1024 ** 3),
                                                                                                   2),
                                                                                               datetime.fromtimestamp(
                                                                                                   row[7]).strftime(
                                                                                                   '%Y-%m-%d, %H:%M'),
                                                                                               row[8]))
    print("".join([add_minus() for i in range(146)]))
