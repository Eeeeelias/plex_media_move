# This is an alternative to the combine_movies.sh script
# written in python for better compatability (e.g. windows)
import argparse
import os
import re
import subprocess
import sys
import time
from sys import platform, exit

from prompt_toolkit import HTML, print_formatted_text, PromptSession, prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.history import FileHistory

# importing is buggy?
if len(sys.argv) == 1:
    from src.mediainfolib import check_ffmpeg, get_config, get_duration, data_path, seperator as sep, FileValidator, \
        PathValidator, clear, get_video_files, logger
else:
    from mediainfolib import check_ffmpeg, get_config, get_duration, data_path, seperator as sep

conf = get_config()

parser = argparse.ArgumentParser()
parser.add_argument(
    "-g",
    dest="input1",
    help="The version of the movie with better image quality, usually English",
)
parser.add_argument(
    "-b",
    dest="input2",
    help="The version from which you only want the audio, usually German",
)
parser.add_argument(
    "-o",
    dest="offset",
    nargs="?",
    help="manual offset of the audio files in case the automatic "
         "offset doesn't work",
)
parser.add_argument("-p", dest="output", nargs="?", help="Specify the output directory")
parser.add_argument(
    "-i",
    dest="interactive",
    action="store_true",
    help="Use this flag exclusively to make " "the script interactive",
)
parser.add_argument(
    "-l",
    dest="langs",
    nargs="*",
    help="The languages of the audio streams, not using this assumes "
         "English for the first and German for the second. Usage: "
         "-l jpn de to have audio stream one be Japanese and audio"
         " stream two be German",
)

session = PromptSession(history=FileHistory(f"{data_path}{sep}.movcomb"))


def interactive():
    start = """
    ############################################################################
    #                             Combine two videos!                          #
    #                                                                          #
    #  Jurrasic Park (1993) - Ver1.mp4   |  Jurrasic Park (1993) - Ver2.mp4    #
    #  <ansigreen>§§§§§§§ Video Track 1 §§§§§§§§§</ansigreen>   |  <ansiyellow>§§§§§§§ Video Track 2 §§§§§§§§§</ansiyellow>    #
    #  <ansiblue>~~~~~~~ Audio Track 1 ~~~~~~~~~</ansiblue>   |  <ansicyan>~~~~~~~ Audio Track 2 ~~~~~~~~~</ansicyan>    #
    #                                                                          #
    # =>        | Jurrasic Park (1993).mkv        |                            #
    #           | <ansigreen>§§§§§§§ Video Track 1 §§§§§§§§§</ansigreen> |                            #
    #           | <ansiblue>~~~~~~~ Audio Track 1 ~~~~~~~~~</ansiblue> |                            #
    #           | <ansicyan>~~~~~~~ Audio Track 2 ~~~~~~~~~</ansicyan> |                            #
    #                                                                          #
    # (i) If you provide paths instead of files, the script will merge videos  #
    #     with the same name.                                                  #
    #                                                                          #
    ############################################################################ 
"""

    print_formatted_text(HTML(start))
    if os.path.isfile(os.path.expanduser("~/prev")):
        prev = prompt(
            HTML("<ansiblue>[a] Do you want to use the previous movie with a different offset? [y/N]: </ansiblue>"))

        if prev == "y":
            return get_prev(os.path.expanduser("~/prev"))
        elif prev == "q":
            return 0, 0, 0, 0, 0, 0

    movie_en = session.prompt(HTML("<ansiblue>[a] Firstly, give the path of the first movie:</ansiblue>"),
                              completer=PathCompleter()).lstrip('"').rstrip('"')
    if movie_en == 'q':
        return 0, 0, 0, 0, 0, 0
    lan_en = prompt(
        HTML("<ansiblue>[a] Please also specify the language using ISO 639-2 codes (e.g. eng, de, jpn): </ansiblue>"))
    print_formatted_text(
        "\n[i] Great, now that we have the first movie let's get the second movie from which we will only take the "
        "audio.")

    movie_de = (session.prompt(HTML("<ansiblue>[a] Please also give the path of this movie:</ansiblue>"),
                               completer=PathCompleter()).lstrip('"').rstrip('"'))

    lan_de = prompt(
        HTML("<ansiblue>[a] Again, please specify the language using ISO 639-2 codes:</ansiblue>")
    )
    print_formatted_text("[i] Almost done, just two more questions")

    destination = ""
    if conf['combiner']['default_out'] is None or conf['combiner']['ask_again']:
        destination = (
            session.prompt(
                HTML("<ansiblue>[a] Where do you want your movie to be saved ([ENTER] to put it in $PWD):</ansiblue>"),
                completer=PathCompleter()).lstrip('"').rstrip('"'))
    if destination == "":
        destination = conf['combiner']['default_out']

    offset = prompt(HTML("<ansiblue>[a] Lastly, put in the offset for the movie (e.g. 400ms). Press [ENTER] to let the "
                         "script handle this:</ansiblue>"))
    print_formatted_text("\n")
    return movie_en, movie_de, lan_en, lan_de, destination, offset


def get_prev(path):
    vals = {}
    with open(path, "r") as f:
        for line in f.readlines():
            vals[line.split("\t")[0]] = line.split("\t")[1].strip("\n")
        f.close()
    print_formatted_text(
        f'Using:\nMovie1: {vals["mv_en"]}\nMovie2: {vals["mv_de"]}\nLanguage1: {vals["ln_en"]}\nLanguage2: {vals["ln_de"]}\nDestination: {vals["dst"]}'
    )
    vals["off"] = prompt(HTML("<ansiblue>[a] Okay great, now please specify a new offset: </ansiblue>"))
    return (
        vals["mv_en"],
        vals["mv_de"],
        vals["ln_en"],
        vals["ln_de"],
        vals["dst"],
        vals["off"],
    )


def delete_movies(movie_en, movie_de):
    delete = prompt(HTML("<ansiblue>[a] Do you want to delete the two versions you just combined? [y/N]: </ansiblue>"))
    if delete.lower() == "y":
        print_formatted_text(HTML("[i] Now deleting movies..."))
        time.sleep(2)
        os.remove(movie_en)
        os.remove(movie_de)
        os.remove(os.path.expanduser("~/prev"))
    return


def match_videos(movie_en, movie_de) -> dict:
    if not os.path.isdir(movie_de) and not os.path.isdir(movie_en):
        return {movie_en: movie_de}
    matches = dict()
    movie_de_files = get_video_files(movie_de)
    for i in get_video_files(movie_en):
        base_name = os.path.splitext(os.path.basename(i))[0]
        try:
            match = [x for x in movie_de_files if base_name in x][0]
            matches[i] = match
        except IndexError:
            print_formatted_text(f"[w] Could not find a match for {i} in {movie_de}")
            continue
    return matches


def run_ffmpeg_combine(movie_en, movie_de, lan_en, lan_de, offset, combined_name, verbose=False):
    ffmpeg = ["ffmpeg", "-loglevel", "error", "-i", movie_en, "-itsoffset", str(offset), "-i", movie_de, "-map",
              "0:0", "-map", "0:a", "-map", "0:s?", "-map", "1:a", "-metadata:s:a:0", f"language={lan_en}", "-metadata:s:a:1",
              f"language={lan_de}",
              "-c", "copy", combined_name]
    if verbose:
        print(" ".join(ffmpeg))
    subprocess.run(ffmpeg)


def main():
    args = parser.parse_args()
    destination = ""
    combined_name = ""
    if not check_ffmpeg():
        exit(1)
    if args.interactive or len(sys.argv) == 1:
        clear()
        movie_en, movie_de, lan_en, lan_de, destination, offset = interactive()
        if movie_en == 0:
            return
        with open(os.path.expanduser("~/prev"), "w") as f:
            f.write(f"mv_en\t{movie_en}\n")
            f.write(f"mv_de\t{movie_de}\n")
            f.write(f"ln_en\t{lan_en}\n")
            f.write(f"ln_de\t{lan_de}\n")
            f.write(f"dst\t{destination}")
            f.close()
    else:
        try:
            movie_en = args.input1
            movie_de = args.input2
            if args.langs is None:
                lan_en = "en"
                lan_de = "de"
            else:
                lan_en = args.langs[0]
                lan_de = args.langs[1]
            if args.offset is not None:
                offset = args.offset
            else:
                offset = ""
        except TypeError:
            print("Please make sure you put in all necessary arguments!")
            exit(1)
            return

    # print ffmpeg command
    v = False
    for i, j in match_videos(movie_en, movie_de).items():
        dur_en = get_duration(i)
        dur_de = get_duration(j)
        diff = dur_en - dur_de
        if offset != "" and offset[-1] == 'v':
            v = True
            offset = offset[:-1]
        if len(offset) < 2:
            print("[i] No offset given, using time diff")
            offset = f"{diff}ms"

        if re.search(r"[sS]\d{2}[eE]\d{2}", i.split(sep)[-1]) is None:
            combined_name = re.sub(r"(?<=\(\d{4}\)).*", ".mkv", i.split(sep)[-1])
        combined_name = re.sub(r".mp4", ".mkv", i.split(sep)[-1])

        if args.output is not None:
            combined_name = args.output + sep + combined_name
        if destination != "":
            combined_name = destination + sep + combined_name

        print(f"[i] Input 1: {i}, video length: {dur_en}ms, language: {lan_en}")
        print(f"[i] Input 2: {j}, video length: {dur_de}ms, language: {lan_de}")
        print(f"[i] File will be written to: {combined_name}")
        print(f"[i] Time difference: {diff}ms, offsetting by: {offset}")

        time.sleep(3)
        print("[i] Combining videos. This might take a while...")
        logger.debug(f"[combiner] Combining: {i} with {j} using an offset of {offset}ms")
        run_ffmpeg_combine(i, j, lan_en, lan_de, offset, combined_name, verbose=v)

    if args.input1 is None:
        print("[i] Success? Check for sync issues. Now starting the movie...")
        time.sleep(1.5)
        try:
            if not os.path.isdir(movie_en):
                os.startfile(combined_name)
                delete_movies(movie_en, movie_de)
        except FileNotFoundError:
            print_formatted_text(
                HTML("<ansired>[w] Something went wrong when combining the files. File could not be found.</ansired>"))
            exit(1)
    else:
        print("[i] Files combined!")
    if args.interactive or len(sys.argv) == 1:
        if prompt(HTML("<ansiblue>Do you want try again? [y/N] </ansiblue>")).lower() == "y":
            main()
        else:
            return
    else:
        exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting")
        exit(0)
