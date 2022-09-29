import math
import mediainfolib
import numpy as np
import manage_db
from manage_db import get_count_ids


def sigmoid(x):

    if x >= 0:
        z = math.exp(-x)
        sig = 1 / (1 + z)
        return sig
    else:
        z = math.exp(x)
        sig = z / (1 + z)
        return sig


def quality_score(episodes: int, duration: int, size: int):
    size_per_episode = size / episodes
    dur_episode = duration/episodes
    score = size_per_episode / dur_episode
    return score


def media_size(db: str):
    show_size = manage_db.custom_sql(db, "SELECT SUM(size) FROM main.shows")[0][0]
    movie_size = manage_db.custom_sql(db, "SELECT SUM(size) FROM main.movies")[0][0]
    size_tb = mediainfolib.convert_size(show_size + movie_size, tb=True)
    if size_tb > 1:
        return f" [i] Your Media library is {size_tb} TB! (woah that's big)"
    else:
        return f" [i] Your Media library is {size_tb} TB! (so tiny hihi)"


def best_quality(db: str, worst=False):
    db_results = manage_db.get_shows("", db)
    scores = {}
    for show in db_results:
        name = show[1]
        episodes = show[3]
        duration = show[4]
        size = show[5]
        scores[name] = quality_score(episodes, duration, size)

    data = np.array(list(scores.values()))
    normalized_scores = (data - data.min()) / (data.max() - data.min())
    for i, j in zip(scores.keys(), normalized_scores):
        scores[i] = j

    max_qual = ["N/A", -1]
    worst_qual = ["N/A", 2]
    for key, val in scores.items():
        if val > max_qual[1]:
            max_qual = [key, val]
        if val < worst_qual[1]:
            worst_qual = [key, val]
    if worst:
        return f" [i] '{worst_qual[0]}' has the lowest quality in your library!"
    return f" [i] '{max_qual[0]}' has the highest quality in your library!"


def database_size(db: str):
    return " [i] {} shows and {} movies in your database.".format(get_count_ids("shows", db)[0],
                                                                  get_count_ids("movies", db)[0])


def total_watchtime(db: str):
    show_wt = manage_db.custom_sql(db, "SELECT SUM(runtime) FROM main.shows")[0][0]
    movie_wt = manage_db.custom_sql(db, "SELECT SUM(runtime) FROM main.movies")[0][0]
    total_wt = mediainfolib.convert_millis((show_wt * 1000) + movie_wt, day=True)
    return f" [i] You could watch through all your media in {total_wt}!"


def oldest_movie(db: str):
    oldest = manage_db.custom_sql(db, "SELECT name,MIN(year) FROM main.movies GROUP BY year")[0]
    name = mediainfolib.cut_name(oldest[0], 72 - 46)
    return f" [i] The oldest movie you have is from {oldest[1]} ({name})!"
