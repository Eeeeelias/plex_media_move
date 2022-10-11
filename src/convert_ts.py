import glob
import os.path
import pathlib
import re
import subprocess
import sys
from prompt_toolkit import prompt, HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter

from src import mediainfolib


def overview():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #                                                                          #
    # Turn this:                        {gs}=> Into this:{ge}                          #
    # /your/path/                          /your/path/                         #
    #    yourShow Episode 1.ts                yourShow Episode 1.mp4           #
    #    yourShow Episode 2.mp4               yourShow Episode 2.mp4           #
    #    yourShow Episode 3.ts                yourShow Episode 3.mp4           #
    #                                                                          #
    ############################################################################
    """))


def converting(unconverted_path, filetype=".ts"):
    print(f"[i] Converting .ts files in {unconverted_path}")
    print(filetype)
    files_to_convert = glob.glob(unconverted_path + f"/*{filetype}")
    if len(files_to_convert) == 0:
        print("[i] There seem to be no videos to convert. Are you sure your inputs are proper?")
        return
    for path in files_to_convert:
        dirname, name = os.path.split(path)
        new_name = re.sub(f"{filetype}", ".mp4", os.path.basename(path))
        print(f"[i] Converting to : {pathlib.Path(dirname, new_name)}")
        subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", path, "-c", "copy", pathlib.Path(dirname, new_name)])
        print("[i] Removing original file")
        os.remove(path)


def main():
    if len(sys.argv) == 1:
        overview()
        path = prompt(HTML("<ansiblue>Put in the path of the folder containing your unconverted files: </ansiblue>"),
                      completer=PathCompleter()).lstrip('"').rstrip('"')
        if path == "q":
            mediainfolib.clear()
            return
        filetype = prompt(HTML("<ansiblue>Put in the filetype you want to convert (default: .ts): </ansiblue>"))
        if filetype == "q":
            mediainfolib.clear()
            return
        elif filetype != "":
            converting(path, filetype)
        else:
            converting(path)
    else:
        try:
            converting(sys.argv[1], sys.argv[2])
        except IndexError:
            converting(sys.argv[1])


if __name__ == '__main__':
    main()