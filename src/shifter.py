import glob
import os
import re
from pathlib import Path
from sys import argv
from prompt_toolkit import prompt, HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter

from src import mediainfolib
from src.mediainfolib import sorted_alphanumeric, PathValidator, seperator as sep, logger


def overview():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    bs = "<grey><i>"
    be = "</i></grey>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #                                                                          #
    # With this tool you are able to shift episode numbers to fit a certain    #
    # numbering. It goes like this:                                            #
    #                                                                          #           
    #  {bs}Unordered{be}                     |     => {gs}Start at 1:{ge}                      #
    # /path/to/yourShow/             |       /path/to/yourShow/                #
    #   yourShow s01e05.mp4          |          yourShow s01e01.mp4            #
    #   yourShow s01e06.mp4          |          yourShow s01e02.mp4            #
    #   yourShow s01e10.mp4          |          yourShow s01e06.mp4            #
    #                                                                          #
    ############################################################################
    """))


def shift_numbers(file, off, start=1):
    dirname, name = os.path.split(file)
    episode_nr = re.search(r"(?<=[eE])\d+", name).group()
    episode_nr_int = int(episode_nr)
    if off == float('-inf'):
        off = episode_nr_int - start
    new_name = re.sub(r"(?<=[eE])\d+", "0" + str(episode_nr_int - off) + "_shift", name)
    os.rename(file, Path(dirname, new_name))
    print(f"Old Name: {name}")
    print(f"New Name: {re.sub(r'_shift', '', new_name)}\n")
    return start + 1, off


def rename_weird_format(rename_path):
    # Renaming some specific weird format
    for path in glob.glob(rename_path + "/*.mp4"):
        new_path = ""
        if re.search(r"Watch ", path) is not None:
            new_path = re.sub(r"Watch ", "", path)
        if re.search(r"(?<=S0\dE\d{2}).+", path) is not None:
            new_path = re.sub(r"(?<=[sS]0\d[eE]\d{2}).+", ".mp4", new_path)
        if new_path != "":
            os.rename(path, new_path)
            print("Renamed:", path)


def rename_other_weird_format(rename_path):
    for path in glob.glob(rename_path + "/*.mp4"):
        base_path, base_name = os.path.split(path)
        new_name = re.sub(r"\((\d) x (\d+)\).*(\.[^.]+$)", r"s0\g<1>e0\g<2>\g<3>", base_name)
        os.rename(path, Path(base_path, new_name))
        print("Renamed:", path)


def loop_shift(path, num_shift):
    offset = float('-inf')
    num_files = 0
    for file in sorted_alphanumeric([x for x in glob.glob(path + f"{sep}*") if os.path.isfile(x)]):
        num_shift, offset = shift_numbers(file, start=num_shift, off=offset)
        num_files += 1
    for file in [x for x in glob.glob(path + f"{sep}*") if os.path.isfile(x)]:
        name = re.sub(r"_shift", "", os.path.basename(file))
        os.rename(file, Path(os.path.dirname(file), name))
    logger.info(f"[shifting] Shifting {num_shift} files in {path} by {offset}")
    print("[i] Everything done!")


def main():
    if len(argv) == 1:
        overview()
        in_path = prompt(HTML("<ansiblue>Put in the path where your files that need shifting are: </ansiblue>"),
                         completer=PathCompleter(), validator=PathValidator()).lstrip('"').rstrip('"')
        if in_path == "q":
            mediainfolib.clear()
            return
        start_pos = prompt(HTML("<ansiblue>Put in the position at which your episodes need to start: </ansiblue>"))
        if start_pos == "q":
            mediainfolib.clear()
            return
        loop_shift(in_path, int(start_pos))
    else:
        try:
            if argv[1] == '-r':
                rename_weird_format(argv[2])
            if argv[1] == '-r2':
                rename_other_weird_format(argv[2])
            if argv[1] == '-s':
                loop_shift(argv[2], int(argv[3]))
        except IndexError:
            print("You haven't supplied enough arguments. Please put in the right arguments")
        except TypeError:
            print("Make sure all arguments are put in properly")
        except ValueError:
            print("Make sure all arguments are put in properly")


if __name__ == '__main__':
    main()
