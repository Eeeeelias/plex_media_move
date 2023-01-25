import glob
import os
import re
import shutil
import subprocess

from src.combine_sub_with_movie import combine_subs
from src.mediainfolib import get_config

# feel free to add to that lol
countries = {'English': 'eng', 'German': 'deu', 'French': 'fra', 'Japanese': 'jpn', 'Korean': 'kor'}


def set_sub_names(in_path: str):
    dest = in_path + "\\"
    for j in glob.glob(in_path + "/Subs/**/*.srt"):
        # print("Curr sub:", j)
        country = re.match(r"\d+_(.*).srt", os.path.basename(j)).group(1)
        alpha = countries.get(country)
        name = j.split("\\")[-2] + f".{alpha}.srt"
        final_dest = dest + name
        # print("Copying to:", final_dest)
        shutil.copy(j, final_dest)


def check_codec(vid: str):
    codec = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name",
                            "-of", "default=noprint_wrappers=1:nokey=1", vid], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    return codec.stdout.decode('utf-8')


def convert_h265(videos: str):
    pass


def main():
    out_path = get_config()['combiner']['default_out']
    in_path = "D:\\Downloads\\Vids\\Represent.S01.FRENCH.1080p.WEBRip.x265-RARBG"
    tmp_path = in_path + "\\converted"
    set_sub_names(in_path)
    codec = check_codec((glob.glob(in_path + "/*.mp4") + glob.glob(in_path + "/*.mkv"))[0])
    print(codec)
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)
    combine_subs([[x for x in glob.glob(in_path + "/*") if os.path.isfile(x)]], tmp_path)
    if codec == 'h264':
        shutil.copy(tmp_path, out_path)
    else:
        convert_h265(tmp_path)


if __name__ == '__main__':
    main()
