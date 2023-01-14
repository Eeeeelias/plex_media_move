import os.path
import re
from prompt_toolkit.validation import Validator, ValidationError

import media_mover
from src import manage_db, convert_ts, change_config
from src.mediainfolib import get_source_files, convert_size, convert_millis, get_duration, \
    seperator as sep, avg_video_size, clear, remove_video_list, get_config, write_video_list, read_existing_list, \
    cut_name, season_episode_matcher, check_database_ex, strip_show_name
from prompt_toolkit import print_formatted_text, HTML, prompt


class InputValidator(Validator):
    def validate(self, document):
        text = document.text
        if text:
            if text[:2] == "cd" and not os.path.isdir(text[3:]):
                raise ValidationError(message='This is not a directory!')
            try:
                input_parser(text)
            except AttributeError:
                if text != "help":
                    raise ValidationError(message='Not a well formed command!')


def help_window():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    bs = "<ansiblue>"
    be = "</ansiblue>"
    ys = "<ansiyellow>"
    ye = "</ansiyellow>"
    print_formatted_text(HTML(f"""
    ##################################################################################################################
    # Commands always work in the same pattern: {gs}[nrs. to consider]{ge}{bs}[function]{be}{ys}[optional info]{ye}                          #
    # For example: {gs}0-5{ge}{bs}s{be}{ys}14{ye} sets the season for the files 0 through 5 to 14                                            #
    # Supplying no nrs. to consider automatically considers all files.                                               #
    #                                                                                                                #
    # Available functions are:                                                                                       #
    # {bs}t{be} - set title, {bs}s{be} - set season, {bs}e{be} - set episode, {bs}m{be} - move files, {bs}d{be} - delete, {bs}c{be} - convert, {bs}r{be} - refresh           #
    #                                                                                                                #
    # Tip: Using {bs}d{be} without other specifiers deletes all suspiciously small files (marked in <ansired>red</ansired>)                     #
    ##################################################################################################################
    """))


def input_parser(input: str) -> tuple:
    # example input:
    # 1s2 - set episode with id 1 to season 2
    # 3-6d - delete episode 3 through 6
    # 12,5,20m - move files 12, 5 and 20
    # m - moves all files
    marker = []
    marker_set = False
    funct_and_mod = {}
    for command in input.split(";"):
        match = re.match(r"(\d+|\d+ ?- ?\d+|\d+((, ?)\d+)*)?([tsemdcrq])(.*)?", command)
        marker = match.group(1) if match.group(1) and not marker_set else marker
        marker_set = True
        funct = match.group(4)
        modifier = match.group(5) if match.group(5) else None
        funct_and_mod[funct] = modifier

    if not marker:
        return marker, funct_and_mod

    if "-" in marker:
        nums = marker.split("-")
        nums = [int(x) for x in nums]
        for x in range(nums[0] + 1, nums[-1]):
            nums.append(x)
    elif "," in marker:
        nums = marker.split(",")
        nums = [int(x) for x in nums]
    else:
        nums = [int(marker)]

    return sorted(nums), funct_and_mod


def show_all_files(ex):
    term_size = os.get_terminal_size().columns - 6
    border_bar = "    " + "#" * term_size
    empty_row = f"    #{' '.ljust(term_size - 2)}#"
    display_string = f"""{border_bar}\n"""
    name_string = int((term_size - 6 - 6 - 7 - 10 - 7) / 2) - 5
    header_string = f"    # {'Nr.'.ljust(6)}{'Filename'.ljust(name_string + 3)}{'Title'.ljust(name_string + 3)}" \
                    f"{'S.'.ljust(6)}{'Ep.'.ljust(7)}{'Size'.ljust(10)}{'Dur.'.ljust(7)} #"
    print_formatted_text(HTML(display_string), end='')
    print(header_string)
    # files info be like:
    # [vid_nr, video, media_name, "SXX", "EXX", "N", duration_vid]
    # [     0,     1,          2,     3,     4,   5,            6]
    #  [1]    Show.mp4 Show S01 E01 N 4h 33m
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
        # print the actual line
        print_formatted_text(
            HTML(f"    # <ansigreen>{f'[{file[0]}]'.ljust(6)}</ansigreen>{filename}"
                 f"{cut_name(file[2], name_string).ljust(name_string + 3)}{file[3].ljust(6)}{file[4].ljust(7)}"
                 f"{size}{convert_millis(int(file[7])).replace('&', '&amp;').ljust(7)} #"))
    display_string = f"{border_bar}\n\t"
    # clear()
    print(empty_row)
    print_formatted_text(HTML(display_string))


def set_season(num_list: list, src_path: str, season: str):
    new_files = []
    files = read_existing_list(src_path)
    try:
        season_int = int(season)
    except (ValueError, TypeError):
        season_int = 1

    for file in files:
        # if num list is empty, all values should be considered
        if int(file[0]) in num_list or num_list == []:
            # converting to an int here to get rid of leading zeroes
            file[3] = f"S0{season_int}"
        new_files.append(tuple(file))

    write_video_list(new_files, src_path)


def set_ep_numbers(num_list: list, src_path: str, ep: str):
    new_files = []
    files = read_existing_list(src_path)
    try:
        ep_int = int(ep)
    except (TypeError, ValueError):
        ep_int = 1

    i = 0
    for file in files:
        if int(file[0]) in num_list or num_list == []:
            file[4] = f"E0{int(ep_int) + i}"
            i += 1
        new_files.append(tuple(file))
    write_video_list(new_files, src_path)


def set_title(num_list: list, src_path: str, title: str):
    new_files = []
    files = read_existing_list(src_path)
    if not title:
        print_formatted_text(HTML("<ansired> No title provided!</ansired>"))
        return

    for i, file in enumerate(files):
        if int(file[0]) in num_list or num_list == []:
            file[2] = title.strip() if title != "\d" else strip_show_name(os.path.basename(file[1]))
        new_files.append(tuple(file))

    write_video_list(new_files, src_path)


def delete_sussy(nums, src_path, modifier=None):
    try:
        curr_files = read_existing_list(src_path)
        if len(nums) != 0:
            for num in nums:
                os.remove(curr_files[num][1])
            return

        for file in curr_files:
            if file[5] == "S":
                os.remove(file[1])

    except FileNotFoundError:
        return


def get_files(src_path, list_path):
    source_files, n_videos, n_folders = get_source_files(src_path)
    ex_videos = read_existing_list(list_path) if os.path.isfile(f"{list_path}/video_list.tmp") else []
    vid_nr = 0
    videos = []
    avg_vid_size = None

    for keys, values in source_files.items():
        # just getting the average show file size
        if "Movies" not in keys and len(values) > 2:
            avg_vid_size = avg_video_size([f"{keys}{sep}{x}" for x in values])
        # actually going through each directory
        for video in [f"{keys}{sep}{x}" for x in values]:
            # checking through the existing videos first, to use those values if possible
            found = False
            for ex in ex_videos:
                if video == ex[1]:
                    found = True
                    videos.append(ex)
                    break
            if found:
                continue
            file_name = os.path.splitext(os.path.basename(video))[0]
            media_name = strip_show_name(file_name)
            duration_vid = get_duration(video)
            size_vid = os.path.getsize(video)
            season, episode = season_episode_matcher(os.path.basename(video))
            ep_str = f"E0{episode}" if episode else f"NaN"
            s_str = f"S0{season}" if season else f"NaN"

            videos.append([vid_nr, video, media_name, s_str, ep_str, "N", size_vid, duration_vid])
            vid_nr += 1
            if avg_vid_size and avg_vid_size * 0.6 > os.path.getsize(video):
                videos[-1][5] = "S"

    # fixing up the numbering
    if ex_videos:
        for i, video in enumerate(videos):
            video[0] = i

    write_video_list(videos, list_path)


def main():
    print("Loading...")
    conf = get_config()
    src_path = conf['mover']['orig_path']
    vid_path = conf['viewer']['default_view']
    funcs = {
        'd': delete_sussy,
        's': set_season,
        'e': set_ep_numbers,
        't': set_title,
        'c': convert_ts.viewer_convert,
        'm': media_mover.viewer_rename,
    }
    get_files(vid_path, src_path)
    clear()
    show_all_files(read_existing_list(src_path))
    window_draw = False
    while True:
        if window_draw:
            get_files(vid_path, src_path)
            ex = read_existing_list(src_path)
            show_all_files(ex)
        window_draw = True
        action = prompt(HTML("<ansiblue>=> </ansiblue>"), validator=InputValidator())
        if action.lower() == "help":
            help_window()
            action = prompt(HTML("<ansiblue>=> </ansiblue>"), validator=InputValidator())
        if action.lower() == "r":
            clear()
            continue
        if action.lower() == "q":
            clear()
            return
        if action.lower() == "q!":
            remove_video_list(src_path)
            exit(0)

        # ability to change dirs
        if action.lower().split(" ")[0] == "cd":
            if not os.path.isdir(action[3:]):
                clear()
                print_formatted_text(HTML("<ansired>    Not a directory!</ansired>"))
                continue
            vid_path = action[3:]
            clear()
            continue

        # if none of the above apply, check for function
        try:
            nums, funcs_dict = input_parser(action)
        except AttributeError:
            clear()
            print_formatted_text(
                HTML("<ansired>    Not a well formed command! Use  \"help\" to get more info</ansired>"))
            continue
        for funct_name, modifier in funcs_dict.items():
            funct = funcs.get(funct_name)
            if funct:
                if funct_name == "m":
                    paths, names = media_mover.viewer_rename(nums, src_path, modifier)
                    moved = media_mover.move_files(paths, names, conf['mover']['dest_path'], conf['mover']['overwrite'])
                    data_path = conf['database']['db_path']
                    db_path = data_path + f"{sep}media_database.db"
                    if check_database_ex(db_path):
                        manage_db.update_database(moved, db_path)
                else:
                    funct(nums, src_path, modifier)
            else:
                clear()
                print_formatted_text(HTML("<ansired>    Not a valid command!</ansired>"))
                break
        clear()
