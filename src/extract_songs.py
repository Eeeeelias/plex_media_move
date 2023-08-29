# I want to extract all the songs from one long video from yt
import os
import re
import subprocess
from sys import exit
from src import mediainfolib
from src.mediainfolib import seperator as sep, data_path, get_config, FileValidator
from prompt_toolkit import print_formatted_text, PromptSession, HTML
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.history import FileHistory

session = PromptSession(history=FileHistory(f"{data_path}{sep}.exsongs"))
config = get_config()
in_path = config['mover']['orig_path']


def greeting():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    # Extract all the single songs from a long audio you downloaded from       #
    # YouTube with the help of timestamps!                                     #
    #                                                                          #
    # Make sure your input format looks like this for optimal results:         #
    #                                                                          #
    # {gs}tt:tt Song Title - Artist{ge}                                                #
    # 00:00 Valse de beaufort - Etienne Balestre                               #
    #   . . .                                                                  #
    # 2:06:27 Canción De Nova - Paco Ruiz                                      #
    #                                                                          #
    ############################################################################
    """))


def interactive():
    song_file = session.prompt(HTML("<ansiblue>Paste the .mp3 file you downloaded from youtube: </ansiblue>"),
                               completer=PathCompleter(), validator=FileValidator()).lstrip('"').rstrip('"')
    if song_file == "q":
        return [None, None, None, None]
    album = session.prompt(HTML("<ansiblue>Specify the album name ([ENTER] to take from file): </ansiblue>"))
    info = session.prompt(HTML("<ansiblue>Paste the timestamps from youtube (or give a file): </ansiblue>")).lstrip(
        '"').rstrip('"')
    print_formatted_text(HTML("[i] If the info is not in the right format the Artist might not be recognized.\n"
                              " You can specify the artist here or press [ENTER] to skip"))
    artist = session.prompt(HTML("<ansiblue>Specify the artist: </ansiblue>"))
    return song_file, album, artist, info


def songs_with_time(raw_infos, album, album_artist):
    """
    extract important information regarding songs from file
    :param album: Name of the playlist
    :param album_artist: Manually specify album artist. Sometimes useful
    :param raw_infos: List containing the time, name and artist of each song/piece
    :return: array with (in that order): Author, Name, Start, End
    """
    song_infos = []
    artist = album_artist if album_artist != "" else "Unknown"
    for line in raw_infos:
        line = line.strip("\n")
        # format: tt:tt Song name - Author
        try:
            match_groups = re.search(r"(\d+:[\d:]*\d+) (.*) [-–] (.*)", line)
            artist = match_groups.group(3) # if album_artist == "Unknown" else album_artist
            name = match_groups.group(2)
            start_track = match_groups.group(1)
        except AttributeError:
            match_groups = re.search(r"(\d+:[\d:]*\d+)[ ]+(.*)", line)
            start_track = match_groups.group(1)
            name = match_groups.group(2)
        song_infos.append([artist, name, album, start_track])

    for i, info in enumerate(song_infos):
        try:
            info.append(song_infos[i + 1][3])
        except IndexError:
            info.append("end")
    if song_infos[-1][1].lower() == "end":
        song_infos.pop(len(song_infos) - 1)
    return song_infos


def song_list(info):
    infos = []
    album = ""
    if os.path.isfile(info):
        with open(info, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip("\n")
                if line == "--STOP--":
                    break
                if len(line) > 1 and not line.startswith("#"):
                    if re.search(r"\d+:[\d:]*\d+", line) is None:
                        album = line.strip(":")
                        continue
                    infos.append(line.strip())
    else:
        infos = [i for i in info.split("\n") if len(i) > 0]
    return infos, album


# maybe in the future?
def correct_song_end(song_end):
    pass


def exec_ffmpeg(input_media, song):
    artist = song[0]
    name = song[1]
    filename = re.sub(r'[<>:"/\\|?*]', '_', name)
    album = song[2] if song[2] != "" else "Unknown album"
    start = song[3]
    end = song[4] if song[4] != "end" else str(mediainfolib.get_duration(input_media))
    output_path = os.path.split(input_media)[0] + f"{sep}{album}"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    output_name = f"{output_path}{sep}{filename}.mp3"
    ffmpeg = ["ffmpeg", "-loglevel", "error", "-i", input_media, "-map_metadata", "-1", "-ss", start, "-to", end,
              "-metadata", f"album={album}", "-metadata", f"title={name}", "-metadata", f"TPE2={artist}", "-c", "copy",
              output_name]
    subprocess.run(ffmpeg)


def main():
    greeting()
    raw_in, album, artist, raw_info = interactive()
    if not raw_in:
        return
    songs, album_auto = song_list(raw_info)
    if album == "":
        album = album_auto
    infos = songs_with_time(songs, album, artist)
    for song in infos:
        print("[i] Song:", song[1])
        exec_ffmpeg(raw_in, song)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting")
        exit(0)
