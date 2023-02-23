import glob
import os
import re
import shutil
import subprocess
import sys
import time
from sys import exit
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit import print_formatted_text, PromptSession, HTML
from src.mediainfolib import seperator as sep, get_config, convert_country, data_path

session = PromptSession(history=FileHistory(f"{data_path}{sep}.subcomb"))
removable_subs = []

# feel free to add to that lol
countries = {'English': 'eng', 'German': 'deu', 'French': 'fra', 'Japanese': 'jpn', 'Korean': 'kor'}


def set_sub_names(in_path: str):
    global removable_subs
    n_subs = 0
    dest = in_path + "\\"
    for j in glob.glob(in_path + f"{sep}Subs{sep}**{sep}*.srt", recursive=True):
        # ignore files that are too small (absolute value)
        if os.path.getsize(j) < 4000:
            continue
        country = re.match(r"\d+_(.*).srt", os.path.basename(j)).group(1)
        alpha = countries.get(country)
        parent_names = j.split(f"{sep}")
        name = parent_names[-2] if parent_names[-2] != 'Subs' else parent_names[-3]
        name = name + f".{alpha}.srt"
        final_dest = dest + name
        # print("Copying to:", final_dest)
        if os.path.isfile(final_dest) and os.path.getsize(final_dest) < os.path.getsize(j):
            continue
        shutil.copy(j, final_dest)
        removable_subs.append(final_dest)
        n_subs += 1
    print(f"Extracted & renamed {n_subs} subtitle(s)")
    return n_subs


def fetch_files(movie_path):
    # only relevant for batches, but not super relevant most of the time
    # folders = [os.path.join(movie_path, x) for x in os.listdir(movie_path) if
    #            os.path.isdir(os.path.join(movie_path, x))]
    rel_folder = []
    # for folder in movie_path:
    folder = movie_path
    if os.path.isdir(movie_path + f"{sep}Subs"):
        set_sub_names(movie_path)
    if glob.glob(folder + "/*.srt") or glob.glob(folder + "/*.ass") and not glob.glob(folder + "/.tmp"):
        rel_folder.append([x for x in glob.glob(folder + "/*") if os.path.isfile(x)])
    return rel_folder


def interactive():
    relevant_files = []
    movie = session.prompt(
        HTML("<ansiblue>[a] Specify the movie you want to have subtitles for (if you give a folder the files"
             " will be taken from there): </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
    if movie == "q":
        return None
    if os.path.isdir(movie):
        return fetch_files(movie)
    sub_file = session.prompt(HTML("<ansiblue>[a] Specify a subtitle file (.srt or .ass): </ansiblue>"),
                              completer=PathCompleter()).lstrip('"').rstrip('"')
    while sub_file != "":
        while not os.path.isfile(sub_file):
            print_formatted_text(HTML("<ansired> This is not a file!</ansired>"))
            sub_file = session.prompt(HTML("<ansiblue>[a] Specify a subtitle file (.srt or .ass): </ansiblue>"),
                                      completer=PathCompleter()).lstrip('"').rstrip('"')
        relevant_files.append(sub_file)
        sub_file = session.prompt(HTML("<ansiblue>[a] Specify another subtitle file ([ENTER] to finish): </ansiblue>"),
                                  completer=PathCompleter()).lstrip('"').rstrip('"')
    relevant_files.append(movie)
    return [relevant_files]


def match_sub_with_vid(files: list):
    videos = [x for x in files[0] if x[-4:] == '.mp4' or x[-4:] == '.mkv']
    subs = [x for x in files[0] if x[-4:] == '.ass' or x[-4:] == '.srt']
    if len(videos) == 1:
        return files
    matches = []
    for video in videos:
        name = os.path.splitext(os.path.basename(video))[0]
        tmp = [video]
        # the regex removes the language and file ending
        tmp.extend([x for x in subs if name == re.sub(r"(\.[\w]{2,3}\.(srt|ass)$)", "", os.path.basename(x))])
        matches.append(tmp)
    return matches


def sub_in_movie(movie_files, out_path):
    ext = set(os.path.splitext(x)[1] for x in movie_files)
    sub_type = ".srt" if {".srt"}.issubset(ext) else ".ass"

    subs = [x for x in movie_files if sub_type in x]

    subs_with_lang = {}
    try:
        for sub in subs:
            lan = re.search(r"\.(\w+)\.[^.]+$", sub).group(1)
            subs_with_lang[lan] = sub

    except AttributeError:
        print_formatted_text(HTML("<ansired>[w] Your subtitles aren't named properly!</ansired>"))
        return
    movie = [x for x in movie_files if sub_type not in x][0]
    out = out_path + f"{sep}{os.path.splitext(os.path.basename(movie))[0]}.mkv"
    print_formatted_text(HTML("<ansimagenta>Video</ansimagenta>: {}".format(os.path.split(movie)[1])))
    inputs = ["ffmpeg", "-loglevel", "error", "-i", movie]
    maps = ["-map", "0"]
    codecs = ["-c:v", "copy", "-c:a", "copy", "-c:s", sub_type[1:]]
    metadata = []
    for i, (key, value) in enumerate(subs_with_lang.items()):
        print_formatted_text(HTML("<ansiyellow>{} Subs</ansiyellow>: {}".format(convert_country(key), os.path.split(value)[1])))
        sub = ["-f", sub_type[1:], "-i", value]
        new_map = ["-map", f"{i + 1}:s"]
        new_metadata = [f"-metadata:s:s:{i}", f"language={key}"]
        inputs.extend(sub)
        maps.extend(new_map)
        metadata.extend(new_metadata)
    ffmpeg_full = inputs + maps + codecs + metadata
    ffmpeg_full.append(out)
    # print(ffmpeg_full)
    subprocess.run(ffmpeg_full)


def combine_subs(files: list, output: str):
    subs_to_combine = match_sub_with_vid(files)
    for movie in subs_to_combine:
        sub_in_movie(movie, output)
        time.sleep(10)


def main():
    if len(sys.argv) == 1:
        try:
            output = get_config()['combiner']['default_out']
        except FileNotFoundError:
            print_formatted_text(HTML("<ansired> Couldn't find config, specify output!</ansired>"))
            output = session.prompt(HTML("<ansiblue> Output path: </ansiblue>"), completer=PathCompleter()).lstrip('"')\
                .rstrip('"')
        files = interactive()
        if files is None:
            return
    else:
        if sys.argv[1] == "-h":
            print("argument 1: path containing .srt or .ass files\nargument 2: output path")
            exit(0)
        files = fetch_files(sys.argv[1])
        output = sys.argv[2]

    combine_subs(files, output)
    global removable_subs
    if len(removable_subs) > 0:
        for i in removable_subs:
            os.remove(i)
    return


if __name__ == '__main__':
    main()
