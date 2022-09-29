import os.path
import re
import subprocess

from prompt_toolkit.completion import PathCompleter
from prompt_toolkit import prompt, HTML, print_formatted_text

import py_combine_movies
from mediainfolib import clear, seperator as sep


def give_options():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #                                                                          #
    # What would you like to do?                                               #
    # [1] {gs}combine{ge}    - combine two movies of different languages into one      #
    #                  movie with two languages                                #
    # [2] {gs}concat{ge}     - concatenate two videos into one video the sum of both   #
    # [3] {gs}cut{ge}        - cut video from x to y to get the relevant parts         #
    #                                                                          #
    ############################################################################
"""))


def example_file_print():
    print_formatted_text(HTML("""
    ############################################################################
    #                                                                          #
    # To concatenate videos please provide a file with the files of the videos #
    # you want to concatenate. The file must have this format:                 #
    #                                                                          #
    # file.txt                                                                 #
    # file \'/path/to/your/video.mp4\'                                           #
    # file \'/path/to/your/video2.mp4\'                                          #
    # file \'/path/to/your/video3.mp4\'                                          #
    #                                                                          #
    ############################################################################
    
    """))


def concat_video_name(input):
    with open(input, "r") as f:
        video = f.readline()
        video = video[6:-2]
        path, name = os.path.split(video)
        new_name = "{}{}concat_{}".format(path, sep, name)
    return new_name


def cut_video_name(input):
    path, name = os.path.split(input)
    new_name = "{}{}cut_{}".format(path, sep, name)
    return new_name


def cut_positions(start=True):
    if not start:
        print("[i] [ENTER] to go to the very end")
    position = prompt(HTML("<ansiblue>{} position in hh:mm:ss format: </ansiblue>".format(
        "Starting" if start else "Ending")))
    if not start and position == "":
        return ""
    while re.search(r"\d{2}:\d{2}:\d{2}", position) is None:
        print_formatted_text(HTML("<ansired>[w] Not the proper format!</ansired>"))
        position = prompt(HTML("<ansiblue>{} position in hh:mm:ss format: </ansiblue>".format(
            "Starting" if start else "Ending")))
    return position


def concat_videos():
    example_file_print()
    input_file = prompt(HTML("<ansiblue>Your file: </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
    while not os.path.isfile(input_file):
        print_formatted_text(HTML("<ansired> [w] Not a file! Try again.</ansired>"))
        input_file = prompt(HTML("<ansiblue>Your file: </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
        if input_file == "q":
            return
    new_file = concat_video_name(input_file)
    print("[i] New file will be: {}".format(new_file))
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", input_file, "-c", "copy", new_file])


def cut_video():
    input_file = prompt(HTML("<ansiblue>Video you want to cut: </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
    while not os.path.isfile(input_file):
        print_formatted_text(HTML("<ansired> [w] Not a file! Try again.</ansired>"))
        input_file = prompt(HTML("<ansiblue>Your file: </ansiblue>"), completer=PathCompleter()).lstrip('"').rstrip('"')
        if input_file == "q":
            return
    start = cut_positions()
    end = cut_positions(start=False)
    new_file = cut_video_name(input_file)
    print("[i] New file will be: {}".format(new_file))
    if end == "":
        subprocess.run(["ffmpeg", "-i", input_file, "-ss", start, new_file])
        return
    subprocess.run(["ffmpeg", "-i", input_file, "-ss", start, "-to", end, new_file])


def main():
    give_options()
    choice = prompt(HTML("<ansiblue>Your choice: </ansiblue>"))
    if choice in ["1", "combine", "com"]:
        py_combine_movies.main()
    elif choice in ["2", "concat", "cat"]:
        concat_videos()
    elif choice in ["3", "cut"]:
        cut_video()
    elif choice in ["q", "quit", "exit"]:
        clear()
        return
    repeat = prompt(HTML("<ansiblue>[a] Would you like to edit another video? [y/N] </ansiblue>"))
    if repeat.lower() != "y":
        clear()
        return
    else:
        main()