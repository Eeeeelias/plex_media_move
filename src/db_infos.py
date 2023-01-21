import math
from datetime import datetime

import numpy as np
from matplotlib.dates import date2num

from src import mediainfolib, manage_db
from src.manage_db import get_count_ids
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter


def sigmoid(x):

    if x >= 0:
        z = math.exp(-x)
        sig = 1 / (1 + z)
        return sig
    else:
        z = math.exp(x)
        sig = z / (1 + z)
        return sig


def _quality_score(episodes: int, duration: int, size: int):
    try:
        size_per_episode = size / episodes
        dur_episode = duration/episodes
        score = size_per_episode / dur_episode
    except ZeroDivisionError:
        return 0
    return score


def media_size(db: str):
    show_size = manage_db.custom_sql(db, "SELECT SUM(size) FROM main.shows")[0][0]
    movie_size = manage_db.custom_sql(db, "SELECT SUM(size) FROM main.movies")[0][0]
    size_tb = mediainfolib.convert_size(show_size + movie_size, unit='tb')
    if size_tb > 2:
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
        scores[name] = _quality_score(episodes, duration, size)

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


def worst_quality(db: str):
    return best_quality(db, worst=True)


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


def num_videos(db: str):
    num_shows = manage_db.custom_sql(db, "SELECT SUM(episodes) FROM main.shows")[0][0]
    num_movies = manage_db.custom_sql(db, "SELECT COUNT(id) FROm main.movies")[0][0]
    return f" [i] You have {num_movies + num_shows} video files in your library!"


def media_over_time(db: str):
    data_shows = manage_db.custom_sql(db, "SELECT id, modified FROM main.shows")
    data_movies = manage_db.custom_sql(db, "SELECT id, modified FROM main.movies")
    df = pd.DataFrame(data_shows, columns=['id_s', 'modified'])
    df2 = pd.DataFrame(data_movies, columns=['id_m', 'modified'])
    df['id_s'] = 's' + df['id_s'].astype(str)
    df2['id_m'] = 'm' + df2['id_m'].astype(str)
    df['date'] = df['modified'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))
    df2['date'] = df2['modified'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))
    merged_df = pd.concat([df[['id_s', 'date']], df2[['id_m', 'date']]], axis=0)
    merged_df['date'] = pd.to_datetime(merged_df['date'])
    merged_df = merged_df.groupby('date').count().reset_index()
    cumulative_sum_m = merged_df['id_m'].cumsum()
    cumulative_sum_s = merged_df['id_s'].cumsum()
    # Plotting
    last_idx = len(cumulative_sum_s) - 1
    plt.plot(merged_df['date'], cumulative_sum_s, label='Shows')
    plt.annotate(f'{cumulative_sum_s[last_idx]:.0f}', xy=(merged_df['date'][last_idx], cumulative_sum_s[last_idx]),
                 xytext=(merged_df['date'][last_idx] - pd.DateOffset(days=180), cumulative_sum_s[last_idx]))

    last_idx = len(cumulative_sum_m) - 1
    plt.plot(merged_df['date'], cumulative_sum_m, label='Movies')
    plt.annotate(f'{cumulative_sum_m[last_idx]:.0f}', xy=(merged_df['date'][last_idx], cumulative_sum_m[last_idx]),
                 xytext=(merged_df['date'][last_idx] - pd.DateOffset(days=180), cumulative_sum_m[last_idx]))
    plt.xlabel('Date')
    plt.ylabel('Amount of Media in the DB')
    plt.legend()
    plt.show()

    # x = date2num(datetime.strptime('2019-09-01', '%Y-%m-%d'))
    # plt.axvline(x=x, color='r', linestyle='--')
    # plt.annotate(f'September 2019', xy=(x, cumulative_sum_s.max()), xytext=(x*1.001, cumulative_sum_s.max()*1.05))


def distribution_episodes(db: str):
    data_shows = manage_db.custom_sql(db, 'SELECT id, episodes FROM main.shows')
    df = pd.DataFrame(data_shows, columns=['id', 'n_episodes'])
    plt.hist(df['n_episodes'], bins=20, color='blue', alpha=0.5)
    plt.xlabel('Number of episodes')
    plt.ylabel('Number of shows')
    plt.show()
    max_episodes = manage_db.custom_sql(db, 'SELECT max(episodes), name FROM main.shows')
    counts = Counter(df['n_episodes'])
    print(f'The show with the most episodes you have is \'{max_episodes[0][1]}\' with {max_episodes[0][0]} episodes! '
          f'Most shows however have {counts.most_common(1)[0][0]} episodes! '
          f'(There are {counts.most_common(1)[0][1]} of them)')


def release_movie(db: str):
    data_movies = manage_db.custom_sql(db, "SELECT id, year FROM main.movies")
    df = pd.DataFrame(data_movies, columns=['id', 'year'])
    plt.hist(df['year'], bins=20, color='green', alpha=0.5)
    plt.xlabel('Release year')
    plt.ylabel('Number of movies')
    plt.show()

    counts = Counter(df['year'])
    print(f'Most movies you have were released in {counts.most_common(1)[0][0]}. '
          f'There are exactly {counts.most_common(1)[0][1]} of them!')


def movie_langs(db: str):
    pass


# uninteresting
def movie_size(db: str):
    data_movies = manage_db.custom_sql(db, "SELECT id, size FROM main.movies")
    df = pd.DataFrame(data_movies, columns=['id', 'size'])
    df['size'] = [mediainfolib.convert_size(x) for x in df['size']]
    mean = df["size"].mean()
    std = df["size"].std()
    df.loc[np.abs(df["size"] - mean) > 3 * std, "size"] = np.nan
    print(df['size'])
    plt.hist(df['size'], bins=20, color='red', alpha=0.5)
    plt.xlabel('Size of the movie')
    plt.ylabel('Number of movies')
    plt.show()
