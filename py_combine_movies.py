# This is an alternative to the combine_movies.sh script
# written in python for better compatability (e.g. windows)
import argparse
import re
import subprocess
import time
from sys import platform
from termcolor import colored, cprint
import os

parser = argparse.ArgumentParser()
parser.add_argument("-g", dest="input1", help="The version of the movie with better image quality, usually English")
parser.add_argument("-b", dest="input2", help="The version from which you only want the audio, usually German")
parser.add_argument("-o", dest="offset", nargs="?", help="manual offset of the audio files in case the automatic "
                                                         "offset doesn't work")
parser.add_argument("-p", dest="output", nargs="?", help="Specify the output directory")
parser.add_argument("-i", dest="interactive", action="store_true", help="Use this flag exclusively to make "
                                                                                   "the script interactive")
if platform == "win32":
    seperator = "\\"
else:
    seperator = "/"


def check_ffmpeg():
    try:
        status, _ = subprocess.getstatusoutput("ffmpeg -version")
        if status == 0:
            return True
        return False
    except Exception:
        print("There was an error with ffmpeg checking, please try again.")


def interactive():
    start = """
    [i] ===================================================================== [i]
    [i]                        Movie Combine                                  [i]
    [i] ===================================================================== [i]
    [i] This script will help you combine two movies to have a smaller movie  [i]
    [i] with two audio streams and one video. Its intended use is to merge    [i]
    [i] movies that just differ in their audio language so to save on storage [i]
    [i] space. For example:                                                   [i]
    [i] Jurassic Park (1993) - English.mp4 and                                [i]
    [i] Jurassic Park (1993) - Deutsch.mp4 to                                 [i]
    [i] =>  Jurassic Park (1993).mkv (1 video stream, 2 audio streams)        [i]
    [i]                                                                       [i]
    [i] Now, let's get right to it!                                           [i]
    [i] ===================================================================== [i] 
    """

    cprint(start)
    movie_en = input(colored("[a] Firstly, give the path of the first movie:", "blue")).lstrip("\"").rstrip("\"")

    while not os.path.isfile(movie_en):
        movie_en = input(colored("[a] This is not a file! Make sure you spelled the path correctly:", "blue")).lstrip(
            "\"").rstrip("\"")

    lan_en = input(colored("[a] Please also specify the language using ISO 639-2 codes (e.g. eng, de, jpn): ", "blue"))
    cprint("\n[i] Great, now that we have the first movie let's get the second movie from which we will only take the "
           "audio.")

    movie_de = input(colored("[a] Please also give the path of this movie:", "blue")).lstrip("\"").rstrip("\"")

    while not os.path.isfile(movie_de):
        movie_de = input(colored("[a] This is not a file! Make sure you spelled the path correctly:", "blue")).lstrip(
            "\"").rstrip("\"")

    lan_de = input(colored("[a] Again, please specify the language using ISO 639-2 codes:", "blue"))
    cprint("[i] Almost done, just two more questions")
    destination = input(colored("[a] Where do you want your movie to be saved ([ENTER] to put it in $PWD):", "blue"))
    offset = input(
        colored("[a] Lastly, put in the offset for the movie. Press [ENTER] to let the script handle this:", "blue"))
    cprint("\n")
    return movie_en, movie_de, lan_en, lan_de, destination, offset


def get_duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return round(float(result.stdout) * 1000)


if __name__ == '__main__':
    args = parser.parse_args()
    destination = ""
    if not check_ffmpeg():
        cprint("[w] You don't have ffmpeg installed! Make sure it is installed and on your $PATH.\n"
               "[w] On Windows, you can install ffmpeg using: choco install ffmpeg\n"
               "[w] On Linux (with apt), type:                sudo apt install ffmpeg\n"
               "[w] Visit https://ffmpeg.org/ for more information!", "red")
        exit(1)
    if args.interactive:
        try:
            movie_en, movie_de, lan_en, lan_de, destination, offset = interactive()
        except KeyboardInterrupt:
            print("Aborting...")
            exit(0)
    else:
        movie_en = args.input1
        movie_de = args.input2
        lan_en = "en"
        lan_de = "de"
        if args.offset is not None:
            offset = args.offset
        else:
            offset = ""

    dur_en = get_duration(movie_en)
    dur_de = get_duration(movie_de)
    diff = dur_en - dur_de
    if offset == "":
        print("[i] No offset given, using time diff")
        offset = f"{diff}ms"

    combined_name = re.sub(r"(?<=\(\d{4}\)) -.*", ".mkv", movie_en.split(seperator)[-1])

    if args.output is not None:
        combined_name = args.output + seperator + combined_name
    if destination != "":
        combined_name = destination + seperator + combined_name

    print(f"[i] Input 1: {movie_en}, video length: {dur_en}ms")
    print(f"[i] Input 2: {movie_de}, video length: {dur_de}ms")
    print(f"[i] File will be written to: {combined_name}")
    print(f"[i] Time difference: {diff}ms, offsetting by: {offset}")

    time.sleep(3)
    print("[i] Combining movies. This might take a while...")
    subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", movie_en, "-itsoffset", offset, "-i", movie_de,
                    "-map", "0:0", "-map", "0:a", "-map", "1:a", "-metadata:s:a:0", f"language={lan_en}",
                    "-metadata:s:a:1", f"language={lan_de}", "-c", "copy", combined_name])
    print("[i] Success!")
    exit(0)
