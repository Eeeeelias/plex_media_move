import glob
import os
import re
import shutil
import subprocess
import time

from src.combine_sub_with_movie import combine_subs
from src.mediainfolib import get_config, seperator as sep, get_video_files

# feel free to add to that lol
countries = {'English': 'eng', 'German': 'deu', 'French': 'fra', 'Japanese': 'jpn', 'Korean': 'kor'}


def set_sub_names(in_path: str):
    n_subs = 0
    dest = in_path + "\\"
    for j in glob.glob(in_path + f"{sep}Subs{sep}*.srt", recursive=True):
        print(j)
        # print("Curr sub:", j)
        country = re.match(r"\d+_(.*).srt", os.path.basename(j)).group(1)
        alpha = countries.get(country)
        parent_names = j.split(f"{sep}")
        name = parent_names[-2] if parent_names[-2] != 'Subs' else parent_names[-3]
        name = name + f".{alpha}.srt"
        final_dest = dest + name
        # print("Copying to:", final_dest)
        shutil.copy(j, final_dest)
        n_subs += 1
    print(f"Extracted & renamed {n_subs} subtitle(s)")
    return n_subs


def check_codec(vid: str):
    codec = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name",
                            "-of", "default=noprint_wrappers=1:nokey=1", vid], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    return codec.stdout.decode('utf-8')


def convert_h265(videos: str, out_path):
    vids = [videos]
    if os.path.isdir(videos):
        vids = [x for x in glob.glob(videos + '/*.mkv') + glob.glob(videos + '/*.mp4') if os.path.isfile(x)]

    # checking for GPU
    try:
        subprocess.check_output('nvidia-smi')
        hw_encoding = 'h264_nvenc'
    except Exception:
        hw_encoding = 'h264'

    for vid in vids:
        new_path = out_path + f"{sep}" + os.path.basename(vid)
        subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", vid, "-map", "0", "-c:v", hw_encoding, "-c:a", "copy",
                        "-pix_fmt", "yuv420p", "-c:s", "copy", new_path])


def main():
    out_path = get_config()['combiner']['default_out']
    in_path = "D:\\Downloads\\Vids\\Shuumatsu"

    vid_list = get_video_files(in_path)
    num_vids = len(vid_list)
    num_existing = len(get_video_files(out_path))
    tmp_path = in_path + "\\converted"
    n_subs = set_sub_names(in_path)
    # do something with subs so it's not useless to extract subs
    codec = check_codec(vid_list[0])
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)
    combine_subs([[x for x in glob.glob(in_path + "/*") if os.path.isfile(x)]], tmp_path)
    if codec == 'h264':
        shutil.copy(tmp_path, out_path)
    else:
        convert_h265(tmp_path, out_path)

    if num_vids != len(get_video_files(out_path)) - num_existing:
        print("Something might've gone wrong, not deleting files")
    else:
        print('Deleting old files')
        os.remove(tmp_path)
    time.sleep(10)


if __name__ == '__main__':
    main()
