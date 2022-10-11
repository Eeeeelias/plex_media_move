import glob
import os
import re
import subprocess
import sys

from prompt_toolkit import print_formatted_text, PromptSession, HTML
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.history import FileHistory

from src.mediainfolib import seperator as sep, get_config, convert_country, data_path

session = PromptSession(history=FileHistory(f"{data_path}{sep}.subcomb"))


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
    relevant_files = []
    movie = session.prompt(
        HTML("<ansiblue>[a] Specify the movie you want to have subtitles for (if you give a folder the files"
             " will be taken from there): </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
    if os.path.isdir(movie):
        return fetch_files(movie)
    sub_file = session.prompt(HTML("<ansiblue>[a] Specify a subtitle file (.srt): </ansiblue>"),
                              completer=PathCompleter()).lstrip('"').rstrip('"')
    while sub_file != "":
        while not os.path.isfile(sub_file):
            print_formatted_text(HTML("<ansired> This is not a file!</ansired>"))
            sub_file = session.prompt(HTML("<ansiblue>[a] Specify a subtitle file (.srt): </ansiblue>"),
                                      completer=PathCompleter()).lstrip('"').rstrip('"')
        relevant_files.append(sub_file)
        sub_file = session.prompt(HTML("<ansiblue>[a] Specify another subtitle file ([ENTER] to finish): </ansiblue>"),
                                  completer=PathCompleter()).lstrip('"').rstrip('"')
    relevant_files.append(movie)
    return [relevant_files]


# needs to be changed!
def sub_in_movie(movie_files, out_path):
    subs = [x for x in movie_files if ".srt" in x]
    subs_with_lang = {}
    try:
        for sub in subs:
            lan = re.search(r"(?<=\.).*(?=\.)", sub).group()
            subs_with_lang[lan] = sub

    except AttributeError:
        print_formatted_text(HTML("<ansired>[w] Your subtitles aren't named properly!</ansired>"))
        return
    movie = [x for x in movie_files if ".srt" not in x][0]
    out = out_path + f"{sep}{os.path.splitext(os.path.basename(movie))[0]}.mkv"
    print("Movie: {}".format(os.path.split(movie)[1]))
    inputs = ["ffmpeg", "-loglevel", "warning", "-i", movie]
    maps = ["-map", "0"]
    codecs = ["-c:v", "copy", "-c:a", "copy", "-c:s", "srt"]
    metadata = []
    for i, (key, value) in enumerate(subs_with_lang.items()):
        print("{} Subs: {}".format(convert_country(key), os.path.split(value)[1]))
        sub = ["-f", "srt", "-i", value]
        new_map = ["-map", f"{i + 1}:s"]
        new_metadata = [f"-metadata:s:s:{i}", f"language={key}"]
        inputs.extend(sub)
        maps.extend(new_map)
        metadata.extend(new_metadata)
    ffmpeg_full = inputs + maps + codecs + metadata
    ffmpeg_full.append(out)
    subprocess.run(ffmpeg_full)


def main():
    if len(sys.argv) == 1:
        try:
            output = get_config()['combiner']['default_out']
        except FileNotFoundError:
            print_formatted_text(HTML("<ansired> Couldn't find config, specify output!</ansired>"))
            output = session.prompt(HTML("<ansiblue> Output path: </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip(
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
