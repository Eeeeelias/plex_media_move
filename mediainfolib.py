import re
import subprocess
import sys
import os
import csv
from sys import platform

try:
    import pycountry
    from prompt_toolkit import prompt, HTML, print_formatted_text
    from prompt_toolkit.completion import PathCompleter
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requirements.txt"])

global seperator
if platform == "win32":
    seperator = "\\"
    env = "LOCALAPPDATA"
    folder = "pmm"
else:
    seperator = "/"
    env = "HOME"
    folder = ".pmm"


# checks if ffmpeg is installed on the system
def check_ffmpeg() -> bool:
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
def get_duration(filename) -> int:
    try:
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
        duration = round(float(result.stdout) * 1000)
    except ValueError:
        return 0
    return duration


# converts milliseconds to minutes and hours
def convert_millis(millis) -> str:
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60))
    return "%dh %dm" % (hours, minutes)


# check if files were skipped
def completeness_check(path, infos_path) -> None:
    name_list = []
    shows_list = [x for x in os.listdir(path)]

    with open(infos_path, 'r') as csvfile:
        show_infos = csv.reader(csvfile)
        for lines in show_infos:
            name_list.append(lines[1])

    for i in shows_list:
        if i not in name_list:
            print(f"{i} not in your list!")


# returns the audio language of the given file
def get_language(filename) -> list:
    audio_info = subprocess.check_output(
        ["ffprobe", "-loglevel", "0", "-show_streams", "-select_streams", "a", filename]).decode()
    langs = re.findall(r"(?<=language=).*(?=\n)", audio_info)
    # ez windows compatibility
    return [lang.rstrip("\r") for lang in langs]


# checks if database exists
def check_database_ex(path) -> bool:
    return os.path.isfile(path)


# convert ISO 639-2 into normal names
def convert_country(alpha: str) -> str:
    alpha = alpha.split(";")
    langs = []
    if alpha[0] != "und":
        try:
            for al in alpha:
                if len(al) == 2:
                    langs.append(pycountry.languages.get(alpha_2=al).name)
                    break
                langs.append(pycountry.languages.get(alpha_3=al).name)
                return ";".join(langs)
        except AttributeError:
            return "Undefined"
    return "Undefined"


# for database pretty print
def cut_name(name):
    if len(name) >= 50:
        return name[:47] + "..."
    else:
        return name


def convert_size(size):
    return round(size / (1024 ** 3), 2)
