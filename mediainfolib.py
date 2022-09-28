import re
import subprocess
import sys
import os
from sys import platform
import json
try:
    import pycountry
    from prompt_toolkit import prompt, HTML, print_formatted_text
    from prompt_toolkit.completion import PathCompleter
    import cv2
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pycountry", "prompt_toolkit", "opencv-python"])

global seperator
if platform == "win32":
    seperator = "\\"
    env = "LOCALAPPDATA"
    folder = "pmm"
else:
    seperator = "/"
    env = "HOME"
    folder = ".pmm"

data_path = os.getenv(env) + seperator + folder
if not os.path.exists(data_path):
    os.mkdir(data_path)
config_path = data_path + f"{seperator}config.json"


def get_config() -> dict:
    """
    Returns the config as a dict or None if no config exists
    :return: dict
    """
    defaults = None
    if os.path.exists(config_path):
        defaults = json.load(open(config_path, 'r'))
    return defaults


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


def get_duration(filename) -> int:
    """
    Returns the duration of a video file in milliseconds
    :param filename: path to the video file
    :return: duration in milliseconds
    """
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


# returns the duration of a video file in seconds
def get_duration_cv2(filename) -> int:
    """
    Returns the duration of a video file in seconds
    :param filename: path to the video file
    :return: duration in seconds
    """
    data = cv2.VideoCapture(filename)
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)
    return round(frames / fps)


def convert_seconds(secs) -> str:
    """
    Converts seconds into hours and minutes
    :param secs: seconds
    :return: string of form XXh YYm
    """
    minutes = (secs / 60) % 60
    hours = (secs / (60 * 60))
    return "%dh %dm" % (hours, minutes)


def convert_millis(millis, day=False) -> str:
    """
    Converts milliseconds into hours and minutes
    :param day: Set if return string should include days
    :param millis: seconds
    :return: string of form XXh YYm
    """
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60))
    if day:
        hours = hours % 24
        days = (millis / (1000 * 60 * 60 * 24))
        return "%d days and %d hours" % (days, hours)
    return "%dh %dm" % (hours, minutes)


def sorted_alphanumeric(data) -> list:
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(data, key=alphanum_key)


def clear():
    return os.system('cls' if os.name == 'nt' else 'clear')


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
def cut_name(name, cut) -> str:
    if len(name) >= cut:
        return name[:cut-3] + "..."
    else:
        return name


def convert_size(size, tb=False) -> float:
    size_gb = size / (1024 ** 3)
    if tb:
        size_tb = size_gb / 1000
        return round(size_tb, 2)
    return round(size_gb, 2)


def add_minus() -> str:
    return "-"


def split_shows(seq, size):
    return (seq[i::size] for i in range(size))
