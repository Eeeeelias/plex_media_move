import time
import os
from prompt_toolkit import print_formatted_text, HTML
from src.mediainfolib import convert_seconds, convert_size, cut_name


def show_all_files(ex):
    term_size = os.get_terminal_size().columns - 6
    border_bar = "    " + "#" * term_size
    empty_row = f"    #{' '.ljust(term_size - 2)}#"
    display_string = f"""{border_bar}\n"""
    # name string is for filename and show name, and will be cut or extended based on size of terminal
    name_string = int((term_size - 6 - 6 - 7 - 10 - 7 - 5) / 2) - 5 - 2

    ep_header = " - Episode Name" if any([e[8] for e in ex if e[8] != "None" and e[9] == "Y"]) else ""


    header_string = f"    # {'Nr.'.ljust(6)}{'Filename'.ljust(name_string + 4)}{f'Title{ep_header}'.ljust(name_string + 3)}" \
                    f"{'S.'.ljust(6)}{'Ep.'.ljust(7)}{'Size'.ljust(10)}{'Dur.'.ljust(8)}{'EN.'.ljust(5)}{'A'.ljust(3)} #"
    print_formatted_text(HTML(display_string), end='')
    print(header_string)
    # files info be like:
    # [vid_nr, video, media_name, "SXX", "EXX", "N", Size, duration_vid, episode_name, enable_ep_name]
    # [     0,     1,          2,     3,     4,   5,    6,            7,            8,              9]
    #  [1]    Show.mp4 Show S01 E01 N 4h 33m (hidden) Y
    prev = ""
    for file in ex:
        if prev != os.path.split(file[1])[0]:
            prev = os.path.split(file[1])[0]
            print(empty_row)

        size = f'{int(convert_size(int(file[6]), unit="mb"))} MB'.ljust(10)
        size = f'<ansired>{size}</ansired>' if file[5] != "N" else size
        fileext = os.path.splitext(os.path.basename(file[1]))[1]

        filename = f'<ansiyellow>{cut_name(os.path.basename(file[1]), name_string, pos="mid").ljust(name_string + 3)}' \
                   f'</ansiyellow>' if fileext != '.mp4' and fileext != '.mkv' else \
            f'{cut_name(os.path.basename(file[1]), name_string, pos="mid").ljust(name_string + 3)}'

        ep_name = "" if file[8] == "None" or file[9] != "Y" else f" - {file[8]}"

        # print the actual line
        text = f"    # <ansigreen>{f'[{file[0]}]'.ljust(6)}</ansigreen>{filename}" \
                 f"{cut_name(file[2] + ep_name, name_string).ljust(name_string + 3)}" \
                 f"{file[3].ljust(6)}{file[4].ljust(7)}" \
                 f"{size}{convert_seconds(int(file[7])).ljust(8)} {file[9].ljust(4)} {file[10].ljust(3)} #"
        try:
            print_formatted_text(HTML(text.replace("&", "&amp;")))
        except:
            print_formatted_text(HTML("<ansired>Error</ansired>"))
    display_string = f"{border_bar}\n\t"
    # clear()
    print(empty_row)
    print_formatted_text(HTML(display_string))