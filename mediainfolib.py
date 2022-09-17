import re
import subprocess
import sys
import os
import csv


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    from prompt_toolkit import prompt, HTML, print_formatted_text
    from prompt_toolkit.completion import PathCompleter
except ModuleNotFoundError:
    install("prompt_toolkit")


# checks if ffmpeg is installed on the system
def check_ffmpeg():
    try:
        status, _ = subprocess.getstatusoutput("ffmpeg -version")
        if status == 0:
            return True
        print_formatted_text(
            "[w] You don't have ffmpeg installed! Make sure it is installed and on your $PATH.\n"
            "[w] On Windows, you can install ffmpeg using: choco install ffmpeg\n"
            "[w] On Linux (with apt), type:                sudo apt install ffmpeg\n"
            "[w] Visit https://ffmpeg.org/ for more information!",
            "red",
        )
        return False
    except Exception:
        print("There was an error with ffmpeg checking, please try again.")


# returns the duration of a video file in milliseconds
def get_duration(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return round(float(result.stdout) * 1000)


# converts milliseconds to minutes and hours
def convert_millis(millis):
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60)) % 24
    return "%dh %dm" % (hours, minutes)


def completeness_check(path, infos_path):
    name_list = []
    shows_list = [x for x in os.listdir(path)]

    with open(infos_path, 'r') as csvfile:
        show_infos = csv.reader(csvfile)
        for lines in show_infos:
            name_list.append(lines[1])

    for i in shows_list:
        if i not in name_list:
            print(f"{i} not in your list!")


def get_language(filename):
    audio_info = subprocess.check_output(
        ["ffprobe", "-loglevel", "0", "-show_streams", "-select_streams", "a", filename]).decode()
    langs = re.findall(r"(?<=language=).*(?=\n)", audio_info)
    # ez windows compatibility
    return [lang.rstrip("\r") for lang in langs]


def create_database(info_shows="", info_movies=""):
    pass


def check_database_ex(path):
    return os.path.isfile(path)