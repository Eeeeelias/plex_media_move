# This is an alternative to the combine_movies.sh script
# written in python for better compatability (e.g. windows)
import argparse
import re
import subprocess
import time
from sys import platform

parser = argparse.ArgumentParser()
parser.add_argument("-g", dest="input1", help="The version of the movie with better image quality, usually English")
parser.add_argument("-b", dest="input2", help="The version from which you only want the audio, usually German")
parser.add_argument("-o", dest="offset", nargs="?", help="manual offset of the audio files in case the automatic "
                                                         "offset doesn't work")
parser.add_argument("-p", dest="output", nargs="?", help="Specify the output directory")

if platform == "win32":
    seperator = "\\"
else:
    seperator = "/"


def get_duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return round(float(result.stdout) * 1000)


if __name__ == '__main__':
    args = parser.parse_args()
    dur_en = get_duration(args.input1)
    dur_de = get_duration(args.input2)
    diff = dur_en - dur_de
    if args.offset is not None:
        offset = args.offset
    else:
        print("[i] No offset given, using time diff")
        offset = f"{diff}ms"

    combined_name = re.sub(r"(?<=\(\d{4}\)) -.*", ".mkv", args.input1.split(seperator)[-1])

    if args.output is not None:
        combined_name = args.output + seperator + combined_name

    print(f"[i] Input 1: {args.input1}, video length: {dur_en}ms")
    print(f"[i] Input 2: {args.input2}, video length: {dur_de}ms")
    print(f"[i] File will be written to: {combined_name}")
    print(f"[i] Time difference: {diff}ms, offsetting by: {offset}")

    time.sleep(3)

    subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", args.input1, "-itsoffset", offset, "-i", args.input2,
                    "-map", "0:0", "-map", "0:a", "-map", "1:a", "-metadata:s:a:0", "language=en", "-metadata:s:a:1",
                    "language=de", "-c", "copy", combined_name])
    print("[i] Success!")
    exit(0)
