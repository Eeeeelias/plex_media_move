import os
import re
import random
import sqlite3

from src import mediainfolib, setup, manage_db, show_stats, generate_report
from src.mediainfolib import seperator, clear, cut_name
from prompt_toolkit import prompt, HTML, print_formatted_text
from src.db_infos import media_size, best_quality, database_size, total_watchtime, oldest_movie, worst_quality, \
    num_videos
from sys import exit


def give_options(info):
    info_line = cut_name(info, 74)
    empty_space = ' ' * (74 - len(info_line))
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #{info_line}{empty_space}#
    #                                                                          #
    # What would you like to do?                                               #
    # Search:  [1] {gs}shows{ge}    [2] {gs}movies{ge}    [3] {gs}custom search{ge}                    #
    # Execute: [4] {gs}deletion{ge} [5] {gs}SQL{ge}       [6] {gs}reindex db{ge}                       #
    # Show:    [7] {gs}stats{ge}    [8] {gs}report{ge}                                         #
    #                                                                          #
    ############################################################################
    """.replace("&", "&amp;")))


# could add like oldest entry, most episodes, etc.
def info_line(db_path):
    try:
        return random.choice([media_size, best_quality, worst_quality,
                              database_size, total_watchtime, oldest_movie, num_videos])(db_path)
    except:
        return " [i] No cool infos! :("


def search_other(db_path):
    movies_vals = {"id": int, "name": str, "year": int, "language": str, "version": str, "runtime": str, "size": int,
                   "modified": float, "type": str}
    shows_vals = {"id": int, "name": str, "seasons": int, "episodes": int, "runtime": int, "modified": float,
                  "size": int}
    anime_vals = {"id": int, "name": str, "seasons": int, "episodes": int, "runtime": int, "modified": float,
                  "size": int}
    sql = "SELECT * FROM {} WHERE {}{}'{}' ORDER BY {} {}"
    db = "movies"
    col = ""
    col_val = ""
    order = ""
    desc = "DESC"
    inp1 = prompt(HTML("<ansiblue>Do you want to look through your [s]hows or [m]ovies? </ansiblue>")).lower()
    correct_vals = shows_vals if inp1 == "s" else movies_vals
    inp2 = prompt(HTML("(Valid values are: {})\n<ansiblue>What do you want to search by? </ansiblue>".format(
        ", ".join(correct_vals.keys())))).lower()
    while inp2 not in correct_vals:
        inp2 = prompt(HTML("<ansiblue>This is not a valid option!</ansiblue>\nOptions are: {}\n => ".format(
            ", ".join(correct_vals.keys())))).lower()
    inp3 = prompt(HTML("<ansiblue>Now specify the value you're searching for (for integer based values, you can do "
                       "e.g. >4 to search for all entries with values greater than 4): </ansiblue>")).lower()
    inp4 = prompt(HTML("<ansiblue>What do you want to order by? Valid are the same values from above: </ansiblue>"))
    while inp4 not in correct_vals:
        inp4 = prompt(HTML("<ansiblue>This is not a valid option!\nOptions are: {} </ansiblue>".format(
            ", ".join(correct_vals.keys())))).lower()
    inp5 = prompt(
        HTML("<ansiblue>Do you want to sort the entries in [a]scending or [d]escending order? </ansiblue>")).lower()
    if inp1 == "s":
        db = "shows"
    col = inp2
    # check inp3 here for metric and col val:
    if correct_vals[col] != str:
        try:
            metric = re.sub(r"\d+", "", inp3)
            col_val = re.search(r"\d+", inp3).group()
        except AttributeError:
            print_formatted_text(
                HTML("<ansired>The value you're searching for does not work in this context</ansired>"))
            return "", ""
    else:
        metric = " like "
        col_val = f"%{inp3}%"
    if metric == "":
        metric = "="
    order = inp4
    if inp5 == "a":
        desc = "ASC"
    return manage_db.get_specific(db_path, sql.format(db, col, metric, col_val, order, desc)), db


def main():
    conf = mediainfolib.get_config()
    db_path = conf['database']['db_path'] + f"{seperator}media_database.db"
    # print("Looking at: {}".format(db_path))
    while 1:
        try:
            db_table = ""
            give_options(info_line(db_path))
            inp = prompt(HTML("<ansiblue>=> </ansiblue>")).lower()
            if inp == "1" or inp == "s" or inp == "shows":
                show = prompt(HTML("<ansiblue>Put in a name for your search: </ansiblue>"))
                res = manage_db.get_shows(search=show, db_path=db_path)
                db_table = "shows"
            elif inp == "2" or inp == "m" or inp == "movies":
                movie = prompt(HTML("<ansiblue>Put in a name for your movie search: </ansiblue>"))
                res = manage_db.get_movies(search=movie, db_path=db_path, order='id')
                db_table = "movies"
            elif inp == "3" or inp == "c" or inp == "custom":
                res, db_table = search_other(db_path)
                if res == "":
                    continue
            elif inp == "4" or inp == "d" or inp == "deletion":
                table = prompt(HTML("<ansiblue>Choose the database you want to delete from (shows or movies): "
                                    "</ansiblue>"))
                while not (table == "movies" or table == "shows"):
                    table = prompt(HTML("<ansiblue>This is not a valid option! Try again: </ansiblue>"))
                id = prompt(HTML("<ansiblue>Give the id of the entry you want to delete: </ansiblue>"))
                manage_db.delete_entry(table, db_path, int(id))
                continue
            elif inp == "5" or inp == "o" or inp == "SQL":
                res = None
                sql = prompt(HTML("<ansiblue>Put in your custom SQL query: </ansiblue>"))
                print(manage_db.custom_sql(db_path, sql))
            elif inp == "6" or inp == "r" or inp == "reindex db":
                res = None
                if not os.path.exists(db_path):
                    setup.redo_db()
                    continue
                setup.redo_db(reindex=True)
            elif inp == "6r":
                if not os.path.exists(db_path):
                    setup.redo_db()
                    continue
                setup.redo_db(reindex=False)
                return
            elif inp in ["7", "stats"]:
                show_stats.all_stats(db_path)
                continue
            elif inp in ["8", "report"]:
                generate_report.main()
                continue
            elif inp == "q":
                mediainfolib.clear()
                return
            else:
                clear()
                continue
            print(manage_db.prettify_out(db_table, res))
            next = prompt(HTML("<ansiblue>Would you like to make another search? [y/N] </ansiblue>"))
            if next.lower() == "n":
                clear()
                return
            elif next.lower() == "q":
                return
            elif next.lower() == "quit" or next.lower() == "stop":
                exit(0)
            elif next.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
        except KeyboardInterrupt:
            print("\nFinishing")
            exit(0)
        except sqlite3.OperationalError:
            print_formatted_text(HTML("<ansired>Database error. Make sure your database exists!</ansired>"))


if __name__ == '__main__':
    main()
