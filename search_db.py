import os
import re

from prompt_toolkit import prompt, HTML, print_formatted_text

import manage_db
from media_mover import data_path
from mediainfolib import seperator

db_path = data_path + f"{seperator}media_database.db"


def search_other():
    movies_vals = {"id": int, "name": str, "year": int, "language": str, "version": str, "runtime": str, "size": int,
                   "modified": float, "type": str}
    shows_vals = {"id": int, "name": str, "seasons": int, "episodes": int, "runtime": int, "modified": float,
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
        inp2 = prompt(HTML("<ansiblue>This is not a valid option!</ansiblue>\nOptions are: {}\n Your choice: ".format(
            ", ".join(correct_vals.keys())))).lower()
    inp3 = prompt(HTML("<ansiblue>Now specify the value you're searching for: </ansiblue>")).lower()
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
            print_formatted_text(HTML("<ansired>The value you're searching for does not work in this context</ansired>"))
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


print("Looking at: {}".format(db_path))
while 1:
    try:
        inp = prompt(
            HTML("<ansiblue>Would you like to look for a [s]how, a [m]ovie or a [c]ustom search? </ansiblue>")).lower()
        if inp == "s":
            show = prompt(HTML("<ansiblue>Put in a name for your search: </ansiblue>"))
            res = manage_db.get_shows(search=show, db_path=db_path)
            manage_db.print_shows(res)
        elif inp == "m":
            movie = prompt(HTML("<ansiblue>Put in a name for your movie search: </ansiblue>"))
            res = manage_db.get_movies(search=movie, db_path=db_path, order='id', desc=False)
            manage_db.print_movies(res)
        elif inp == "c":
            res, db_table = search_other()
            if res == "":
                continue
            if db_table == "movies":
                manage_db.print_movies(res)
            elif db_table == "shows":
                manage_db.print_shows(res)
        else:
            continue
        next = prompt(HTML("<ansiblue>Would you like to make another search? [y/N] </ansiblue>"))
        if next.lower() == "n":
            exit(0)
        elif next.lower() == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
    except KeyboardInterrupt:
        print("\nFinishing")
        exit(0)
