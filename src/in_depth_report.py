import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

from src.db_infos import best_quality
from src.mediainfolib import data_path, seperator as sep
from src import manage_db, mediainfolib


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
    if not os.path.isdir(data_path + f"{sep}plots"):
        os.mkdir(data_path + f"{sep}plots")
    plt.savefig(data_path + f"{sep}plots/me_o_t.jpg")
    plt.clf()
    # x = date2num(datetime.strptime('2019-09-01', '%Y-%m-%d'))
    # plt.axvline(x=x, color='r', linestyle='--')
    # plt.annotate(f'September 2019', xy=(x, cumulative_sum_s.max()), xytext=(x*1.001, cumulative_sum_s.max()*1.05))


def distribution_episodes(db: str):
    data_shows = manage_db.custom_sql(db, 'SELECT id, episodes FROM main.shows')
    df = pd.DataFrame(data_shows, columns=['id', 'n_episodes'])
    plt.hist(df['n_episodes'], bins=20, color='blue', alpha=0.5)
    plt.xlabel('Number of episodes')
    plt.ylabel('Number of shows')
    plt.savefig(data_path + f"{sep}plots/dis_ep.jpg")
    plt.clf()
    max_episodes = manage_db.custom_sql(db, 'SELECT max(episodes), name FROM main.shows')
    counts = Counter(df['n_episodes'])
    return f'The show with the most episodes you have is \'{max_episodes[0][1]}\' with {max_episodes[0][0]} episodes!' \
           f' Most shows however have {counts.most_common(1)[0][0]} episodes! In fact, there are ' \
           f'{counts.most_common(1)[0][1]} of them. '


def release_movie(db: str):
    data_movies = manage_db.custom_sql(db, "SELECT id, year FROM main.movies")
    df = pd.DataFrame(data_movies, columns=['id', 'year'])
    plt.hist(df['year'], bins=20, color='green', alpha=0.5)
    plt.xlabel('Release year')
    plt.ylabel('Number of movies')
    plt.savefig(data_path + f"{sep}plots/re_mo.jpg")
    plt.clf()
    counts = Counter(df['year'])
    return counts.most_common(1)[0]


def word_analysis(db: str):
    data_shows = manage_db.custom_sql(db, 'SELECT name FROM main.shows')
    data_movies = manage_db.custom_sql(db, 'SELECT name FROM main.movies')
    words = " ".join([x[0] for x in data_shows]) + " ".join([x[0] for x in data_movies])
    words = words.split(" ")
    useless_words = ['the', 'to', 'a', 'der', 'das', 'und', 'of', 'no', 'in', 'und', 'and', '-', 'des', '&', 'die',
                     'wo', 'ni', 'wa', 'von', 'on', 'ist', 'ein']
    words = [x.lower() for x in words if x.lower() not in useless_words]
    counts = Counter(words)
    df = pd.DataFrame.from_dict(counts, orient='index', columns=['value'])
    df.reset_index(inplace=True)
    df.columns = ['word', 'frequency']
    df_filtered: pd.DataFrame = df.sort_values(by=['frequency'], ascending=False).loc[df['frequency'] > 5]
    return df_filtered.head(5).to_numpy().tolist()


def scores_analysis(db: str):
    scores = best_quality(db, all_scores=True)
    df = pd.DataFrame.from_dict(scores, orient='index', columns=['value'])
    df.reset_index(inplace=True)
    df.columns = ['show', 'norm_score']
    plt.scatter(df.index, df['norm_score'], alpha=0.5)
    for i, row in df.iterrows():
        if row['norm_score'] > 0.6:
            plt.annotate(row['show'], (i, row['norm_score']), xytext=(5, 5), textcoords='offset points')
    plt.xlabel('TV Shows')
    plt.ylabel('Score')
    plt.savefig(data_path + f"{sep}plots/sc_an.jpg")
    plt.clf()


def media_to_filesize(db: str):
    data_movies = manage_db.custom_sql(db, 'SELECT size, modified FROM main.movies')
    df = pd.DataFrame(data_movies, columns=['size', 'date'])
    df['date'] = df['date'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))
    df['size'] = [mediainfolib.convert_size(x, unit='gb') for x in df['size']]
    cumsum_size = df['size'].cumsum()
    df = df.sort_values(by=['date'])
    df = df.reset_index(drop=True)
    median_size = df['size'].median()
    plt.plot(df.index, cumsum_size, label='actual growth')
    plt.plot(df.index, median_size * df.index, '--', color='r', label='estimated growth')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df.set_index('date', inplace=True)
    yearly_first_rows = df.groupby(df.index.year).idxmin()
    df = df.reset_index(drop=False)
    iter_year = yearly_first_rows[-3:].iterrows() if len(yearly_first_rows) > 4 else yearly_first_rows.iterrows()
    for year in iter_year:
        date = year[1]['size']
        x_val = df.index[df['date'] == date][0]
        plt.axvline(x=x_val, color='gray', linestyle='--', linewidth=1)
        plt.annotate(year[1]['size'].year, xy=(x_val, cumsum_size.tail(1)), xycoords='data', xytext=(-28, 0),
                     textcoords='offset points')
    plt.xlabel('# of Movies')
    plt.ylabel('Library size in GB')
    plt.legend()
    plt.savefig(data_path + f"{sep}plots/m_t_f.jpg")
    plt.clf()


def filetype_size(db: str):
    data_movies = manage_db.custom_sql(db, 'SELECT type, size FROM main.movies')
    df = pd.DataFrame(data_movies, columns=['type', 'size'])
    df['size'] = [mediainfolib.convert_size(x, unit='gb') for x in df['size']]
    df['type'] = pd.Categorical(df['type'])
    df.boxplot(column='size', by='type', grid=False, widths=0.7)
    plt.title('')
    plt.suptitle('')
    plt.xlabel('Movie filetype')
    plt.ylabel('Filesize in GB')
    plt.savefig(data_path + f"{sep}plots/ft_s.jpg")
    plt.clf()
