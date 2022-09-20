import glob
import os
import re
from pathlib import Path
from sys import argv
from prompt_toolkit import prompt, HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter


def overview():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #                                                                          #
    # Whith this tool you are able to shift episode numbers to fit a certain   #
    # numbering. It goes like this:                                            #           
    #                                                                          #
    # /path/to/yourShow/                                                       #
    #   yourShow s01e05.mp4                                                    #
    #   yourShow s01e06.mp4                                                    #
    #   yourShow s01e10.mp4                                                    #
    #                                                                          #
    # => {gs}Start at 1:{ge}                                                           #
    # /path/to/yourShow/                                                       #
    #   yourShow s01e01.mp4                                                    #
    #   yourShow s01e02.mp4                                                    #
    #   yourShow s01e06.mp4                                                    #
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


def loop_shift(path, num_shift):
    offset = float('-inf')
    for file in glob.glob(path + "/*.mp4"):
        num_shift, offset = shift_numbers(file, start=num_shift, off=offset)
    for file in glob.glob(path + "/*.mp4"):
        name = re.sub(r"_shift", "", os.path.basename(file))
        os.rename(file, Path(os.path.dirname(file), name))
    print("[i] Everything done!")


def main():
    if len(argv) == 1:
        in_path = prompt(HTML("<ansiblue>Put in the path where your files that need shifting are: </ansiblue>"),
                         completer=PathCompleter()).lstrip('"').rstrip('"')
        start_pos = prompt(HTML("<ansiblue>Put in the position at which your episodes need to start: </ansiblue>"))
        loop_shift(in_path, int(start_pos))
    else:
        try:
            if argv[1] == '-r':
                rename_weird_format(argv[2])
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
