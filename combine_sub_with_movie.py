import glob
import os
import re
import subprocess
import sys

from prompt_toolkit import print_formatted_text, prompt, HTML
from prompt_toolkit.completion import PathCompleter

from mediainfolib import seperator as sep, get_config, convert_country


def fetch_files(movie_path):
    # only relevant for batches, but not super relevant most of the time
    # folders = [os.path.join(movie_path, x) for x in os.listdir(movie_path) if
    #            os.path.isdir(os.path.join(movie_path, x))]
    rel_folder = []
    # for folder in movie_path:
    folder = movie_path
    if glob.glob(folder + "/*.srt") and not glob.glob(folder + "/.tmp"):
        rel_folder.append(glob.glob(folder + "/*"))
    return rel_folder


def interactive():
    movie = prompt(HTML("<ansiblue>[a] Specify the movie you want to have subtitles for (if you give a folder the files"
                        " will be taken from there): </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
    if os.path.isdir(movie):
        return fetch_files(movie)
    sub_de = prompt(HTML("<ansiblue>[a] Specify the first subtitle file (.srt): </ansiblue>"),
                    completer=PathCompleter()).lstrip('"').rstrip('"')
    while not os.path.isfile(sub_de):
        print_formatted_text(HTML("<ansired> This is not a file!</ansired>"))
        sub_de = prompt(HTML("<ansiblue>[a] Specify the first subtitle file (.srt): </ansiblue>"),
                        completer=PathCompleter()).lstrip('"').rstrip('"')
    sub_en = prompt(HTML("<ansiblue>[a] Specify the second subtitle file (.srt): </ansiblue>"),
                    completer=PathCompleter()).lstrip('"').rstrip('"')
    while not os.path.isfile(sub_en):
        print_formatted_text(HTML("<ansired> This is not a file!</ansired>"))
        sub_de = prompt(HTML("<ansiblue>[a] Specify the second subtitle file (.srt): </ansiblue>"),
                        completer=PathCompleter()).lstrip('"').rstrip('"')
    return [[sub_de, sub_en, movie]]


def sub_in_movie(movie_files, out_path):
    sub_de = movie_files[0]
    sub_en = movie_files[1]
    try:
        lan_de = re.search(r"(?<=\.).*(?=\.)", sub_de).group()
        lan_en = re.search(r"(?<=\.).*(?=\.)", sub_en).group()
    except AttributeError:
        print_formatted_text(HTML("<ansired>[w] Your subtitles aren't named properly!</ansired>"))
        return
    movie = movie_files[2]
    out = out_path + f"{sep}" + os.path.split(movie)[1]
    print("Movie: {}\n"
          "{} Subs: {}\n"
          "{} Subs: {}".format(os.path.split(movie)[1], convert_country(lan_de), os.path.split(sub_de)[1],
                               convert_country(lan_en), os.path.split(sub_en)[1]))
    ffmpeg = ["ffmpeg", "-loglevel", "warning", "-i", movie, "-f", "srt", "-i", sub_de, "-f", "srt", "-i", sub_en,
              "-map", "0:0", "-map", "0:1", "-map", "0:2", "-map", "1:0", "-map", "2:0", "-c:v", "copy", "-c:a", "copy",
              "-c:s", "srt", "-metadata:s:s:0", f"language={lan_de}", "-metadata:s:s:1", f"language={lan_en}", out]
    subprocess.run(ffmpeg)


def main():
    if len(sys.argv) == 1:
        try:
            output = get_config()['combiner']['default_out']
        except FileNotFoundError:
            print_formatted_text(HTML("<ansired> Couldn't find config, specify output!</ansired>"))
            output = prompt(HTML("<ansiblue> Output path: </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip(
                '"')
        subs_to_combine = interactive()
    else:
        if sys.argv[1] == "-h":
            print("argument 1: path containing .srt files\nargument 2: output path")
            exit(0)
        subs_to_combine = fetch_files(sys.argv[1])
        output = sys.argv[2]

    for movie in subs_to_combine:
        sub_in_movie(movie, output)
    return


if __name__ == '__main__':
    main()
