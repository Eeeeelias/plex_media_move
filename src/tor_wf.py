import glob
import os
import re
import shutil
import subprocess
import time

import prompt_toolkit
from prompt_toolkit import HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter

from src.combine_sub_with_movie import combine_subs
from src.mediainfolib import get_config, seperator as sep, get_video_files, PathValidator

# feel free to add to that lol
countries = {'English': 'eng', 'German': 'deu', 'French': 'fra', 'Japanese': 'jpn', 'Korean': 'kor'}


def greetings():
    return prompt_toolkit.prompt(HTML("<ansiblue>=> </ansiblue>"), completer=PathCompleter(), validator=PathValidator())\
        .lstrip('"').lstrip('"')


def set_sub_names(in_path: str):
    n_subs = 0
    dest = in_path + "\\"
    for j in glob.glob(in_path + f"{sep}Subs{sep}**{sep}*.srt", recursive=True):
        # check to make sure only the bigger file gets taken
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
    try:
        codec = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name",
                                "-of", "default=noprint_wrappers=1:nokey=1", vid], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        return codec.stdout.decode('utf-8').strip()
    except IndexError:
        return None


def hw_encoding():
    try:
        subprocess.check_output('nvidia-smi')
        hw_encode = 'h264_nvenc'
    except Exception:
        hw_encode = 'h264'
    return hw_encode


def convert_h265(videos: str, out_path):
    vids = [videos]
    if os.path.isdir(videos):
        vids = [x for x in get_video_files(videos) if os.path.isfile(x)]

    print(f"Converting {len(vids)} videos")
    # checking for GPU
    hw_encode = hw_encoding()
    for vid in vids:
        print_formatted_text(HTML(f"<ansiyellow>Converting</ansiyellow>: {os.path.basename(vid)}"))
        new_path = out_path + f"{sep}" + os.path.basename(vid)
        subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", vid, "-map", "0", "-c:v", hw_encode, "-c:a", "copy",
                        "-pix_fmt", "yuv420p", "-c:s", "copy", new_path])


def hdr_to_sdr(video: str, out_path):
    """
    Converts an (ideally) 4K HDR video to 1080p SDR in H264 encoding
    :param video: String to the input video
    :param out_path: path where the converted video should be saved
    :return: None
    """
    out = out_path + sep + re.sub("HDR", "SDR", os.path.basename(video))
    res = "1920:1080"
    codec = hw_encoding()
    ffmpeg = ['ffmpeg', '-hwaccel', 'cuda', '-i', video, "-map", "0", '-vf',
              f'zscale=t=linear,tonemap=hable,zscale=p=709:t=709:m=709,scale={res}', "-c:v", codec,
              "-pix_fmt", "yuv420p", "-c:a", "copy", "-c:s", "copy", out]
    subprocess.run(ffmpeg)


def main():
    out_path = get_config()['combiner']['default_out']
    in_path = greetings()

    vid_list = get_video_files(in_path)
    num_vids = len(vid_list)
    num_existing = len(get_video_files(out_path))
    tmp_path = in_path
    n_subs = set_sub_names(in_path)
    # do something with subs so it's not useless to extract subs
    codec = check_codec(vid_list[0])
    if n_subs > 0:
        tmp_path += "\\converted"
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
        shutil.rmtree(tmp_path)


if __name__ == '__main__':
    main()
