import os.path
import re

import media_mover
from src.mediainfolib import get_source_files, current_files_info, convert_size, convert_millis, get_duration, \
    seperator as sep, avg_video_size, clear, remove_video_list, get_config, write_video_list, read_existing_list
from prompt_toolkit import print_formatted_text, HTML, prompt


def input_parser(input: str) -> tuple:
    # example input:
    # 1s2 - set episode with id 1 to season 2
    # 3-6d - delete episode 3 through 6
    # 12,5,20m - move files 12, 5 and 20
    # m - moves all files

    match = re.match(r"(\d+|\d+ ?- ?\d+|\d+((, ?)\d+)*)?([a-zA-Z])(\d+)?", input)
    marker = match.group(1)
    funct = match.group(4)
    modifier = match.group(5)

    if funct is None:
        raise TypeError

    if not marker:
        return [], funct, modifier

    if "-" in marker:
        nums = marker.split("-")
        nums = [int(x) for x in nums]
        for x in range(nums[0]+1, nums[-1]):
            nums.append(x)
    elif "," in marker:
        nums = marker.split(",")
        nums = [int(x) for x in nums]
    else:
        nums = [int(marker)]

    return sorted(nums), funct, modifier


def show_all_files(files_info, avg_vid_sizes, vid_lengths=None):
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    border_bar = "#" * 98
    display_string = f"""{border_bar}\n"""
    spacing_num = len(str(len(files_info)))
    correct_counter = 0
    curr_dir = ""
    vid_lengths_new = {}
    print_formatted_text(HTML(display_string), end='')

    for i in range(len(files_info)):
        if os.path.isdir(files_info[i]) or len(files_info[i]) == 0:
            display_string = f"# ".ljust(spacing_num + 4) + current_files_info(i, files_info, 90) + " #\n"
            print_formatted_text(HTML(display_string), end='')
            correct_counter += 1
            curr_dir = files_info[i] if len(files_info[i]) > 0 else curr_dir
            continue

        file_path = f"{curr_dir}{sep}{files_info[i]}"

        size_bytes = os.path.getsize(file_path)

        size_str = f"  <ansired>{convert_size(size_bytes, unit='mb')} MB</ansired>".rjust(33) \
            if file_path in avg_vid_sizes else f"  {convert_size(size_bytes, unit='mb')} MB".rjust(14)

        duration_vid = get_duration(file_path) if not vid_lengths else vid_lengths.get(file_path)
        length_str = f"  {convert_millis(duration_vid)}".rjust(12)

        vid_lengths_new[file_path] = duration_vid
        front_spacing = spacing_num - len(str(i - correct_counter))
        display_string = f"# {gs}[{i - correct_counter}]{ge} ".ljust(29 + front_spacing) + \
                         f"{current_files_info(i, files_info, 65 - len(str(i - correct_counter)) - front_spacing)}" \
                         f"{size_str}{length_str} #\n"
        print_formatted_text(HTML(display_string), end='')

    display_string = f"{border_bar}\n\t"
    # clear()
    print_formatted_text(HTML(display_string))
    return vid_lengths_new


def set_season(num_list: list, src_path: str, season: str):
    new_files = []
    files = read_existing_list(src_path)
    if not season:
        season = 1

    for file in files:
        # if num list is empty, all values should be considered
        if file[0] in str(num_list) or num_list == []:
            file[3] = f"S0{season}"
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


def get_files():
    src_path = get_config()['mover']['orig_path']
    source_files, n_videos, n_folders = get_source_files()
    files_info = []
    avg_vid_sizes = []
    vid_nr = 0
    videos = []
    avg_vid_size = None
    for keys, values in source_files.items():
        if "Movies" not in keys and len(values) > 2:
            avg_vid_size = avg_video_size([f"{keys}{sep}{x}" for x in values])
        for video in [f"{keys}{sep}{x}" for x in values]:
            file_name = os.path.splitext(os.path.basename(video))[0]
            file_match = re.match(r"(.+) (Episode \d+|[sS]\d+[eE]\d+|\(\d{4}\))(.*)", file_name)
            media_name = file_match.group(1) if file_match else file_name

            videos.append([vid_nr, video, media_name, "SXX", "EXX", "N"])
            vid_nr += 1
            if avg_vid_size and avg_vid_size * 0.6 > os.path.getsize(video):
                videos[-1][5] = "S"
                avg_vid_sizes.append(video)
        files_info.append(keys)
        files_info.extend(values)
        files_info.append("")

    # just don't overwrite the old stuff that might've been changed
    if os.path.isfile(f"{src_path}/video_list.tmp"):
        ex_files = read_existing_list(src_path)
        new_videos = []
        for video in videos:
            found = False
            for ex_video in ex_files:
                if video[1] == ex_video[1]:
                    new_videos.append(ex_video)
                    found = True
                    break
            if not found:
                new_videos.append(video)
        videos = new_videos

    write_video_list(videos, src_path)
    return files_info, avg_vid_sizes


def main():
    # gets all the files and stores suspiciously small files in another list
    files, small_files = get_files()
    vid_lengths = show_all_files(files, small_files)
    src_path = get_config()['mover']['orig_path']
    window_draw = False
    while True:
        if window_draw:
            files, small_files = get_files()
            show_all_files(files, small_files, vid_lengths)
        action = prompt(HTML("<ansiblue>=> </ansiblue>"))
        if action.lower() == "q":
            clear()
            return
        if action.lower() == "q!":
            remove_video_list(src_path)
            exit(0)
        nums, funct, modifier = input_parser(action)
        if funct == "d":
            delete_sussy(nums, src_path, modifier)
        if funct == "s":
            set_season(nums, src_path, modifier)
        if funct == "m":
            media_mover.main()
        clear()
        window_draw = True