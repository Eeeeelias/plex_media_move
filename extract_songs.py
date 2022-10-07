# I want to extract all the songs from one long video from yt
import os
import re
import subprocess
import sys
from prompt_toolkit import prompt, HTML, print_formatted_text

import mediainfolib


def songs_with_time(raw_infos, album_artist="Unknown"):
    """
    extract important information regarding songs from file
    :param album_artist: Manually specify album artist. Sometimes useful
    :param raw_infos: List containing the time, name and artist of each song/piece
    :return: array with (in that order): Author, Name, Start, End
    """
    song_infos = []
    for line in raw_infos:
        line = line.strip("\n")
        # format: tt:tt Song name - Author
        try:
            match_groups = re.search(r"(\d+:[\d:]*\d+) (.*) [-–] (.*)", line)
            artist = match_groups.group(3)
            name = match_groups.group(2)
            start_track = match_groups.group(1)
        except AttributeError:
            match_groups = re.search(r"(\d+:[\d:]*\d+) (.*)", line)
            start_track = match_groups.group(1)
            name = match_groups.group(2)
            artist = album_artist
        song_infos.append([artist, name, start_track])

    for i, info in enumerate(song_infos):
        try:
            info.append(song_infos[i + 1][2])
        except IndexError:
            info.append("end")
    return song_infos


def song_list(info):
    infos = []
    if os.path.isfile(info):
        with open(info, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                infos.append(line)
    else:
        test = prompt(HTML("<ansiblue>Paste the timestamps from youtube: </ansiblue>"))
        infos = [i for i in test.split("\n") if len(i) > 0]
    return infos


# maybe in the future?
def correct_song_end(song_end):
    pass


def exec_ffmpeg(input_media, song):
    artist = song[0]
    name = song[1]
    output_name = os.path.split(input_media)[0] + mediainfolib.seperator + name + ".mp3"
    start = song[2]
    end = song[3] if song[3] != "end" else str(mediainfolib.get_duration(input_media))
    ffmpeg = ["ffmpeg", "-loglevel", "warning", "-i", input_media, "-map_metadata", "-1", "-ss", start, "-to", end,
              "-metadata", f"title={name}", "-metadata", f"TPE2={artist}", "-c", "copy", output_name]
    subprocess.run(ffmpeg)


def main():
    infos = songs_with_time(song_list("interactive"))
    for song in infos:
        print("[i] Song:", song[1])
        exec_ffmpeg(sys.argv[2], song)


if __name__ == '__main__':
    main()
