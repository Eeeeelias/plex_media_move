import glob
import re
import os
import sys
import json
import subprocess
import time
from sys import platform
from difflib import SequenceMatcher as SM
from prompt_toolkit.validation import Validator, ValidationError
import pycountry
from prompt_toolkit import prompt, HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter
import cv2

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


class PathValidator(Validator):
    def validate(self, document):
        text = document.text
        if text and text != 'q' and not os.path.isdir(text.lstrip('"').rstrip('"')):
            raise ValidationError(message='This is not a directory!')


class FileValidator(Validator):
    def validate(self, document):
        text = document.text
        if text and text != 'q' and not os.path.isfile(text.lstrip('"').rstrip('"')):
            raise ValidationError(message='This is not a file!')


def write_config_to_file(config: dict, path: str):
    """
    Write your configuration down in a .json file.
    :param config The configuration you want to write to a file
    :param path The file path where the config should be written to
    """
    json.dump(config, open(path, 'w'))
    return


def get_config(conf_path=config_path) -> dict:
    """
    Returns the config as a dict or None if no config exists
    :return: dict
    """
    defaults = None
    if os.path.exists(conf_path):
        defaults = json.load(open(conf_path, 'r'))
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


# return all source videos that can be found, with a number indicating the amount
def get_source_files(video_folder=None) -> tuple:
    """
    Retrieves the list of files in the `source_path` specified in the `get_config()` dictionary, including files in
    subdirectories.
    Returns a tuple containing the list of files, the number of files, and the number of directories as its elements.
    The filenames in each directory are sorted alphabetically.
    """
    config = get_config()
    source_path = video_folder if video_folder else config['mover']['orig_path']
    try:
        filetypes = config['viewer']['filetypes'].split(' ')
    except KeyError:
        from src.change_config import default_configs
        default_configs(config)
        filetypes = config['viewer']['filetypes'].split(' ')
    source_files = {}
    n_files = 0
    n_paths = 0
    file_list = [path for pattern in filetypes
                 for path in glob.glob(source_path + f'{seperator}**{seperator}*' + pattern, recursive=True)]
    for path in file_list:
        if not os.path.isfile(path):
            continue
        src_path, name = os.path.split(path)
        n_files += 1
        if source_files.get(src_path) is None:
            source_files[src_path] = [name]
            n_paths += 1
        else:
            source_files.get(src_path).append(name)
    for key in source_files.keys():
        source_files[key] = sorted_alphanumeric(source_files.get(key))
    return source_files, n_files, n_paths


# return all videos of common file types
def get_video_files(path: str, subpath=None):
    full_path = path + f"{seperator}" + subpath if subpath else path
    video_files = []
    full_path = full_path.replace('[', '[[]') # character escaping
    video_files.extend(glob.glob(full_path + "/*.mp4"))
    video_files.extend(glob.glob(full_path + "/*.mkv"))
    video_files.extend(glob.glob(full_path + "/*.ts"))
    video_files.extend(glob.glob(full_path + "/*.webm"))
    return video_files


def current_files_info(c: int, files: list, max_len=36) -> list:
    display_list = []
    for i in range(c+1):
        if i > len(files) - 1:
            display_list.append(" " * max_len)
        elif os.path.isdir(files[i]):
            display_list.append(f"<ansigreen>{cut_name(files[i], max_len, pos='left')}</ansigreen>".ljust(max_len + 23))
        elif i == 16 and len(files) > 16 and max_len == 37:
            display_list.append(f". . . ({len(files[16:])} more)".ljust(max_len))
        else:
            ep = re.search(r"[Ss]\d+[Ee]\d+.*", files[i])
            if ep is not None:
                cut = len(ep.group()) if len(ep.group()) < 20 else 20
                display_list.append(f"{cut_name(files[i], max_len, pos='mid', mid=cut)}".ljust(max_len))
                continue
            display_list.append(f"{cut_name(files[i], max_len, pos='mid')}".ljust(max_len))

    return display_list


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
    try:
        duration = round(frames / fps)
    except ZeroDivisionError:
        duration = 0
    return duration


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


def clear() -> int:
    return os.system('cls' if os.name == 'nt' else 'clear')


# returns the audio language of the given file
def get_language(filename: str) -> list:
    audio_info = subprocess.check_output(
        ["ffprobe", "-loglevel", "0", "-show_streams", "-select_streams", "a", filename]).decode()
    langs = re.findall(r"(?<=language=).*(?=\n)", audio_info)
    # ez windows compatibility
    return [lang.rstrip("\r") for lang in langs]


# checks if database exists
def check_database_ex(path: str) -> bool:
    return os.path.isfile(path)


# convert ISO 639-2 into normal names
def convert_country(alpha: str) -> str:
    alpha = alpha.split(";")
    langs = []
    # country codes are either 2 or 3 chars long
    if len(alpha[0]) > 3:
        return pycountry.languages.search_fuzzy(alpha[0])
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


# for cutting names to appropriate size with dots to indicate shortening
def cut_name(name: str, cut: int, pos='right', mid=10) -> str:
    if len(name) < cut:
        return name
    if pos == 'right':
        return name[:cut - 3] + "..."
    if pos == 'mid':
        return name[:cut - (mid + 3)] + "..." + name[-mid:]
    if pos == 'left':
        return "..." + name[len(name) - cut + 3:]


def convert_size(size, unit='gb', r=2) -> float:
    """
    Converting filesize to more understandable numbers. Takes in size as bytes and divides by 1024^3.
    :param size: The filesize in bytes
    :param unit: The unit to convert it to. Available are: gb, tb, mb
    :param r: Digits of rounding
    :return: Returns the filesize in the wanted unit rounded by r digits
    """
    size_gb = size / (1024 ** 3)
    if unit == 'tb':
        size_tb = size_gb / 1024
        return round(size_tb, r)
    if unit == 'mb':
        size_mb = size_gb * 1024
        return round(size_mb, r)
    return round(size_gb, r)


def add_minus() -> str:
    return "-"


def split_shows(seq, size):
    return (seq[i::size] for i in range(size))


def fuzzy_matching(input_dir, u_show) -> str:
    try:
        threshold = get_config()['mover']['fuzzy_match']
    except KeyError:
        print("No threshold found in config! Setting default")
        from src.change_config import add_to_config
        add_to_config({'mover': {'fuzzy_match': "0.8"}}, append=True)
        threshold = 0.8
    matched_show = None
    for show in os.listdir(input_dir):
        ratio = SM(None, show, u_show).ratio()
        if 1 > ratio > float(threshold):
            print(
                "[i] \'{}\' and \'{}\' might be the same show. ({:.0f}% similarity)".format(show, u_show, ratio * 100))
            matched_show = show
            break
    return matched_show


def avg_video_size(path) -> float:
    video_sizes = [os.path.getsize(video) for video in path]
    return sum(video_sizes) / len(video_sizes)


def strip_show_name(raw) -> str:
    name = re.sub(r"((Season \d+|\d+(nd|rd|th) Season)? Episode \d+|[sS]\d+[eE]\d+|\(\d{4}\))(.*)", "", raw).strip()
    name_dots = re.sub(r"\.", " ", name)
    # if names are written like Show.Name.S01E01.mp4
    if " " in name_dots and "  " not in name_dots:
        return name_dots.strip()
    return name


def write_video_list(videos, path) -> None:
    with open(f'{path}/video_list.tmp', 'w') as f:
        for video in videos:
            for info in video:
                f.write(str(info) + ";")
            f.write("\n")


def remove_video_list(path) -> None:
    file = f'{path}/video_list.tmp'
    if os.path.isfile(file):
        os.remove(file)


def read_existing_list(src_path: str) -> list:
    files = []
    with open(f'{src_path}/video_list.tmp', 'r') as f:
        for line in f.readlines():
            files.append(line.strip().split(";"))
            files[-1] = files[-1][:-1]
    return files


def season_episode_matcher(filename) -> tuple:
    # when it's easy lol
    match = re.match(r"(.*)[sS](\d+)[eE](\d+)", filename)
    if match:
        return int(match.group(2)), int(match.group(3))
    # where it starts getting difficult
    match_episode = re.match(r".*Episode (\d+)", filename)
    episode = match_episode.group(1) if match_episode else None
    if not episode:
        return None, None
    match_season = re.match(r".*(Season (\d+)|(\d+)(nd|rd|th) Season)", filename)
    if match_season:
        season = match_season.group(2) if match_season.group(2) else match_season.group(3)
    else:
        season = 1
    return season, episode
