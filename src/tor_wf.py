import glob
import os
import re
import shutil
import subprocess
import time

import prompt_toolkit
from prompt_toolkit import HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter

import src.mediainfolib
from src.combine_sub_with_movie import combine_subs
from src.mediainfolib import get_config, seperator as sep, get_video_files, write_config_to_file, clear, cut_name

# feel free to add to that lol
countries = {'English': 'eng', 'German': 'deu', 'French': 'fra', 'Japanese': 'jpn', 'Korean': 'kor'}


def input_parser(input: str, conf: dict):
    in_vals = re.match(r"(\w*) (.*)", input)
    conf.update({in_vals.group(1): in_vals.group(2).strip("\"")})
    return conf


def greetings(conv_conf: dict):
    header = "    ############################################################################    \n" + \
             "    #                                                                          #    \n"
    values = "    # Your current config:                                                     #    \n"
    for i, j in conv_conf.items():
        if i == 'input' and os.path.isdir(j):
            j += f" ({len(get_video_files(j))} video(s) found)"
        values = values + f"    # <ansigreen>{i.ljust(12)}</ansigreen> {cut_name(str(j), 59).ljust(59)} #    \n"
    print_formatted_text(HTML(header + values + header[::-1][1:]))


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


def check_codec(vid: str, type='v'):
    try:
        codec = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", f"{type}:0", "-show_entries", "stream=codec_name",
             "-of", "default=noprint_wrappers=1:nokey=1", vid], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return list(set(codec.stdout.decode('utf-8').strip().split("\r\n")))[0]
    except IndexError:
        return None


def ffprobe_info(vid: str):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,pix_fmt,bit_rate",
         "-of", "default=noprint_wrappers=1:nokey=1", vid], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    result = result.stdout.decode('utf-8').strip().split("\r\n")
    # result should be [codec_name, width, height, pix_fmt, bit_rate, codec_name, bit_rate, ...]
    return result[:6]


def hw_encoding():
    try:
        subprocess.check_output('nvidia-smi')
        return True
    except Exception:
        return False


def convert_h265(videos: str, out_path: str):
    vids = [videos]
    if os.path.isdir(videos):
        vids = [x for x in get_video_files(videos) if os.path.isfile(x)]

    print(f"Converting {len(vids)} videos")
    # checking for GPU
    hw_encode = "h264_nvenc" if hw_encoding() else "h264"
    for vid in vids:
        print_formatted_text(HTML(f"<ansiyellow>Converting</ansiyellow>: {os.path.basename(vid)}"))
        new_path = out_path + f"{sep}" + os.path.basename(vid)
        subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", vid, "-map", "0", "-c:v", hw_encode, "-c:a", "copy",
                        "-pix_fmt", "yuv420p", "-c:s", "copy", new_path])


def hdr_to_sdr(video: str, out_path: str):
    """
    Converts an (ideally) 4K HDR video to 1080p SDR in H264 encoding
    :param video: String to the input video
    :param out_path: path where the converted video should be saved
    :return: None
    """
    out = out_path + sep + re.sub("HDR", "SDR", os.path.basename(video))
    res = "1920:1080"
    codec = "h264_nvenc" if hw_encoding() else "h264"
    ffmpeg = ['ffmpeg', '-hwaccel', 'cuda', '-i', video, "-map", "0", '-vf',
              f'zscale=t=linear,tonemap=hable,zscale=p=709:t=709:m=709,scale={res}', "-c:v", codec,
              "-pix_fmt", "yuv420p", "-c:a", "copy", "-c:s", "copy", out]
    subprocess.run(ffmpeg)


# resolution, codec, streams, filetype
def init_conversion(config: dict, vid=None):
    video = config['mover']['orig_path'] if vid is None else vid
    out_path = config['combiner']['default_out']
    infos = ffprobe_info(video) if os.path.isfile(video) else ffprobe_info(get_video_files(video)[0])
    if len(infos) < 6:
        print_formatted_text(HTML("<ansired>ffprobe could not be invoked properly!</ansired>"))
        infos = ['Error', 'Error', 'Error', 'Error', 'Error', 'Error']
    conversion_config = {'input': video, 'output': out_path, 'resolution': f'{infos[1]}:{infos[2]} (original)',
                         'vcodec': infos[0] + " (original)", 'acodec': infos[5] + " (original)",
                         'bitrate': infos[4] + " (original)", 'filetype': '.mkv', 'vstreams': 'all',
                         'astreams': 'all', 'sstreams': 'all', 'hw_encode': hw_encoding()}
    # add possibility to save config
    return conversion_config


def convert_general(config: dict, in_file: str):
    ffmpeg_command = ['ffmpeg', '-loglevel', 'warning', '-i', in_file]
    # mapping streams
    for i in ['v', 'a', 's']:
        if config.get(f'{i}streams') == 'all':
            ffmpeg_command.extend(['-map', f'0:{i}?'])
            continue
        for j in config.get(f'{i}streams').split(','):
            ffmpeg_command.extend(['-map', f'0:{i}:{j}'])

    # setting the right codecs
    for i in ['v', 'a']:
        codec = config.get(f'{i}codec') if 'original' not in config.get(f'{i}codec') else 'copy'
        codec += "_nvenc" if config.get('hw_encode') and i == 'v' else ""
        ffmpeg_command.extend([f'-c:{i}', codec])
        if codec.startswith('h264'):
            ffmpeg_command.extend(['-pix_fmt', 'yuv420p'])
        if i == 'v' and "(original)" not in config.get('bitrate'):
            ffmpeg_command.extend(['-b:v', config.get('bitrate')])
    ffmpeg_command.extend(['-c:s', 'copy'])

    # setting output name
    name = os.path.splitext(os.path.basename(in_file))[0]
    ffmpeg_command.append(config.get('output') + sep + name + config.get('filetype'))
    try:
        print(ffmpeg_command)
        subprocess.run(ffmpeg_command)
    except Exception as e:
        print(e)
        return


def main():
    config = get_config()
    out_path = config['combiner']['default_out']
    conversion_conf = init_conversion(config)
    greetings(conversion_conf)
    confirm = prompt_toolkit.prompt(HTML("<ansiblue>=> </ansiblue>"))
    curr_input = conversion_conf['input']
    while confirm != 'ok':
        clear()
        if confirm == 'q':
            return
        conversion_conf = input_parser(confirm, conversion_conf)
        if conversion_conf['input'] != curr_input:
            curr_input = conversion_conf['input']
            conversion_conf = init_conversion(config, conversion_conf['input'])
        greetings(conversion_conf)
        confirm = prompt_toolkit.prompt(HTML("<ansiblue>=> </ansiblue>"))
    if os.path.isfile(conversion_conf.get('input')):
        convert_general(conversion_conf, conversion_conf.get('input'))
        return
    for path in get_video_files(conversion_conf.get('input')):
        print('Converting', path)
        convert_general(conversion_conf, path)
    return


if __name__ == '__main__':
    main()

    """
    in_path = conversion_conf.get('input')
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
        shutil.rmtree(tmp_path) """
