import datetime
import os.path

from src.mediainfolib import data_path, seperator as sep, get_config
from shutil import copy


def make_analyses(db_path: str):
    import src.in_depth_report as idr
    plots = [idr.media_over_time, idr.release_movie, idr.media_to_filesize, idr.scores_analysis, idr.filetype_size,
             idr.distribution_episodes, idr.shows_to_size]
    sig_ep = []
    for anal in plots:
        sig_ep.append(anal(db_path))
    words = idr.word_analysis(db_path)
    return sig_ep, words


def read_html(path: str) -> str:
    with open(path, 'r') as f:
        return "".join(f.readlines())


def add_values(html: str, values: tuple) -> str:
    sig_ep = values[0]
    words = values[1]
    html_fin = html.format(sig_ep[5], sig_ep[1], words[0][0], words[0][1], words[1][0], words[1][1], words[2][0],
                           words[2][1], words[3][0], words[3][1], words[4][0], words[4][1])
    return html_fin


def write_html(out_path: str, html: str) -> None:
    with open(out_path, 'w') as f:
        f.write(html)


def main():
    print("Generating...")
    real_path = os.path.split(os.path.realpath(__file__))[0]
    if not os.path.isdir(data_path + f"{sep}icons/"):
        os.mkdir(data_path + f"{sep}icons/")
    # janky way of getting the correct file path.
    copy(real_path[:-3] + "icons/pmm_logo_green.png",
         data_path + f"{sep}icons/pmm_logo_green.png")
    database_path = get_config()['database']['db_path'] + f"{sep}media_database.db"
    sig_ep, words = make_analyses(database_path)
    html = read_html(real_path + "/template.html")
    fin_html = add_values(html, (sig_ep, words))
    if not os.path.isdir(data_path + f"{sep}reports/"):
        os.mkdir(data_path + f"{sep}reports/")
    time = datetime.datetime.now().strftime("%Y-%m-%d")
    write_html(data_path + f"{sep}/reports/report_{time}.html", fin_html)
    os.startfile(data_path + f"{sep}/reports/report_{time}.html")
    return
