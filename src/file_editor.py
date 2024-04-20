import os.path
import re
import time

from prompt_toolkit.validation import Validator, ValidationError

import media_mover
from src import manage_db, convert_ts
from src.mediainfolib import get_source_files, \
    seperator as sep, avg_video_size, clear, remove_video_list, get_config, write_video_list, read_existing_list, \
    season_episode_matcher, check_database_ex, strip_show_name, config_path, get_duration_cv2, \
    write_config_to_file, logger, library_names, show_exists
from prompt_toolkit import print_formatted_text, HTML, prompt
from src.window_file_editor import show_all_files


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
        match = re.match(r"(\d+|\d+ ?- ?\d+|\d+((, ?)\d+)*)?([tsemdcrxovqa])(.*)?", command)
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
            file[3] = f"S0{season_int}" if season_int < 10 else f"S{season_int}"

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


def set_extensions(config: dict, ext: str):
    curr_ext: list = config['viewer']['filetypes'].split(' ')
    curr_ext.remove(ext) if ext in curr_ext else curr_ext.append(ext)
    config['viewer']['filetypes'] = " ".join(curr_ext)
    write_config_to_file(config, config_path)


# sort the lines of the file based on the sort_by parameter
def sort_file_order(src_path: str, sort_by='default'):
    files = read_existing_list(src_path)

    if sort_by == 'default':
        files = sorted(files, key=lambda x: x[2])
    elif sort_by == 'ep':
        files = sorted(files, key=lambda x: x[4])
    elif sort_by == 'size':
        files = sorted(files, key=lambda x: x[6])
    elif sort_by == 'duration':
        files = sorted(files, key=lambda x: x[7])

    # since the list files contains the index of each item at position 0, we need to update those values
    new_files = []
    for num, line in enumerate(files):
        line[0] = num
        new_files.append(line)
    print("writing new order to file")
    write_video_list(new_files, src_path)


def delete_sussy(nums, src_path, modifier=None):
    try:
        curr_files = read_existing_list(src_path)
        num_deleted = 0
        deleted_names = []
        if len(nums) != 0:
            for num in nums:
                num_deleted += 1
                os.remove(curr_files[num][1])
                deleted_names.append(curr_files[num][1])
            return

        for file in curr_files:
            if file[5] == "S":
                num_deleted += 1
                os.remove(file[1])
                deleted_names.append(file[1])
        logger.debug(f"[viewer] Deleted {num_deleted} file(s) ({';'.join(deleted_names)})")
    except FileNotFoundError:
        return


def show_name_colour(media_name, out_path, fuzzy_threshold):
    show_type, is_certain = show_exists(media_name, out_path, fuzzy_threshold)
    found = "blue"
    if not is_certain:
        if show_type == "A" or show_type == "S":
            found = "yellow"
    else:
        found = "green"
    show_type = "S" if show_type == "N" else show_type
    return show_type, found


def get_files(src_path, out_path, list_path, fuzzy_threshold):
    source_files, n_videos, n_folders = get_source_files(src_path)
    ex_videos = read_existing_list(list_path) if os.path.isfile(f"{list_path}/video_list.tmp") else []
    vid_nr = 0
    videos = []
    avg_vid_size = None

# TODO: ensure that file numbering stays the same after reordering
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
                    # update show type and certainty color if the title has changed
                    show_type, certainty_color = show_name_colour(ex[2], out_path, fuzzy_threshold)
                    if ex[12] == 'a':
                        ex[10] = show_type
                    ex[11] = certainty_color
                    videos.append(ex)
                    break
            if found:
                continue
            file_name = os.path.splitext(os.path.basename(video))[0]
            media_name = strip_show_name(file_name)
            duration_vid = get_duration_cv2(video)
            size_vid = os.path.getsize(video)
            season, episode = season_episode_matcher(os.path.basename(video), duration=duration_vid)
            ep_str = f"E{episode}" if episode else f"NaN"
            s_str = f"S{season}" if season else f"NaN"
            episode_name = file_name.split(" - ")[-1].strip() if len(file_name.split(" - ")) > 1 else None
            if episode_name:
                episode_name = episode_name.split("(")[0].strip() if len(episode_name.split("(")) > 1 else episode_name
            # check if media_name exists and if it does, what type of show it is and how certain the match is
            show_type, certainty_color = show_name_colour(media_name, out_path, fuzzy_threshold)

            # turn off episode names by default
            videos.append([vid_nr, video, media_name, s_str, ep_str, "N", size_vid, duration_vid, episode_name, "N", show_type, certainty_color, 'a'])
            vid_nr += 1
            if avg_vid_size and avg_vid_size * 0.6 > os.path.getsize(video):
                videos[-1][5] = "S"

    # fixing up the numbering
    if ex_videos:
        for i, video in enumerate(videos):
            video[0] = i

    write_video_list(videos, list_path)


def toggle_episode_names(num_list: list, src_path: str, modifier: str):
    new_files = []
    files = read_existing_list(src_path)

    for i, file in enumerate(files):
        if int(file[0]) in num_list or num_list == []:
            if not modifier:
                file[9] = "N" if file[9] == "Y" else "Y"
            else:
                file[8] = modifier
                file[9] = "Y"
        new_files.append(tuple(file))

    write_video_list(new_files, src_path)


def set_anime(num_list: list, src_path: str, modifier: str):
    new_files = []
    files = read_existing_list(src_path)

    for i, file in enumerate(files):
        if int(file[0]) in num_list or num_list == []:
            file[10] = "A" if file[10] == "S" else "S"
            file[12] = "m"
        new_files.append(tuple(file))

    write_video_list(new_files, src_path)


def main():
    print("Loading...")
    conf = get_config()
    src_path = conf['mover']['orig_path']
    out_path = conf['mover']['dest_path']
    vid_path = conf['viewer']['default_view']
    # TODO: make sure this exists
    try:
        fuzzy_threshold = conf['mover']['fuzzy_match']
    except KeyError:
        fuzzy_threshold = 0.8
    funcs = {
        'd': delete_sussy,
        's': set_season,
        'e': set_ep_numbers,
        't': set_title,
        'c': convert_ts.viewer_convert,
        'm': media_mover.viewer_rename,
        'x': set_extensions,
        'o': toggle_episode_names,
        'a': set_anime
    }
    get_files(vid_path, out_path, src_path, fuzzy_threshold)
    clear()
    show_all_files(read_existing_list(src_path))
    window_draw = False
    while True:
        if window_draw:
            get_files(vid_path, out_path, src_path, fuzzy_threshold)
            ex = read_existing_list(src_path)
            show_all_files(ex)
        window_draw = True
        action = prompt(HTML("<ansiblue>=> </ansiblue>"), validator=InputValidator())
        if action.lower() == "help":
            help_window()
            action = prompt(HTML("<ansiblue>=> </ansiblue>"), validator=InputValidator())
        elif action.lower() == "r":
            clear()
            continue
        elif action.lower() == "q":
            clear()
            return
        elif action.lower() == "q!":
            remove_video_list(src_path)
            exit(0)
        # ability to change dirs
        elif action.lower().split(" ")[0] == "cd":
            if not os.path.isdir(action[3:]):
                clear()
                print_formatted_text(HTML("<ansired>    Not a directory!</ansired>"))
                continue
            vid_path = action[3:]
            clear()
            continue
        elif action.lower().startswith('x'):
            set_extensions(conf, action[1:])
            clear()
            continue
        elif action.lower().startswith("v"):
            sort_file_order(src_path, action[1:])

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
                    paths, names, libraries = media_mover.viewer_rename(nums, src_path, modifier)
                    libraries = [library_names(conf['mover']['dest_path'], x) for x in libraries]
                    moved = media_mover.move_files(paths, names, conf['mover']['dest_path'], libraries, conf['mover']['overwrite'])
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
