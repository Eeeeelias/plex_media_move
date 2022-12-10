import glob
import re
import os
import sys
import json
import subprocess
from sys import platform
from difflib import SequenceMatcher as SM

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


# return all source videos that can be found, with a number indicating the amount
def get_source_files() -> tuple:
    """
    Retrieves the list of files in the `source_path` specified in the `get_config()` dictionary, including files in
    subdirectories.
    Returns a tuple containing the list of files, the number of files, and the number of directories as its elements.
    The filenames in each directory are sorted alphabetically.
    """
    config = get_config()
    source_path = config['mover']['orig_path']
    try:
        filetypes = config['mover']['filetypes'].split(' ')
    except KeyError:
        from src.change_config import default_configs
        default_configs(config, ('mover', 'filetypes'))
        filetypes = config['mover']['filetypes'].split(' ')
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


def current_files_info(c: int, files: list, max_len=37) -> str:
    if c > len(files) - 1:
        return " " * max_len
    if os.path.isdir(files[c]):
        return f"<ansigreen>{cut_name(files[c], max_len, pos='left')}</ansigreen>".ljust(max_len + 23)
    if c == 16 and len(files) > 16 and max_len == 37:
        return f". . . ({len(files[16:])} more)".ljust(max_len)

    ep = re.search(r"[Ss]\d+[Ee]\d+.*", files[c])
    if ep is not None:
        cut = len(ep.group()) if len(ep.group()) < 20 else 20
        return f"{cut_name(files[c], max_len, pos='mid', mid=cut)}".ljust(max_len)
    return f"{cut_name(files[c], max_len, pos='mid')}".ljust(max_len)


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


# for cutting names to appropriate size with dots to indicate shortening
def cut_name(name, cut, pos='right', mid=10) -> str:
    if len(name) < cut:
        return name
    if pos == 'right':
        return name[:cut - 3] + "..."
    if pos == 'mid':
        return name[:cut - (mid + 3)] + "..." + name[-mid:]
    if pos == 'left':
        return "..." + name[len(name) - cut + 3:]


def convert_size(size, unit='gb', r=2) -> float:
    size_gb = size / (1024 ** 3)
    if unit == 'tb':
        size_tb = size_gb / 1000
        return round(size_tb, r)
    if unit == 'mb':
        size_mb = size_gb * 1000
        return round(size_mb, r)
    return round(size_gb, r)


def add_minus() -> str:
    return "-"


def split_shows(seq, size):
    return (seq[i::size] for i in range(size))


def fuzzy_matching(input_dir, u_show) -> str:
    matched_show = None
    for show in os.listdir(input_dir):
        ratio = SM(None, show, u_show).ratio()
        if 1 > ratio > 0.8:
            print(
                "[i] \'{}\' and \'{}\' might be the same show. ({:.0f}% similarity)".format(show, u_show, ratio * 100))
            matched_show = show
            break
    return matched_show


def avg_video_size(path) -> float:
    video_sizes = [os.path.getsize(video) for video in path]
    return sum(video_sizes) / len(video_sizes)


def write_video_list(videos, path):
    with open(f'{path}/video_list.tmp', 'w') as f:
        for video in videos:
            for info in video:
                f.write(str(info) + ";")
            f.write("\n")


def remove_video_list(path):
    file = f'{path}/video_list.tmp'
    if os.path.isfile(file):
        os.remove(file)


def read_existing_list(src_path: str):
    files = []
    with open(f'{src_path}/video_list.tmp', 'r') as f:
        for line in f.readlines():
            files.append(line.strip().split(";"))
            files[-1] = files[-1][:-1]
    return files


def season_episode_matcher(filename):
    # when it's easy lol
    match = re.match(r"(.*)[sS](\d+)[eE](\d+)", filename)
    if match:
        return int(match.group(2)), int(match.group(3))
    # where it starts getting difficult
    match_simple = re.match(r".*Episode (\d+)", filename)
    if match_simple:
        return 1, int(match_simple.group(1))
