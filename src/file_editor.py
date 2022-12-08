import os.path

from src.mediainfolib import get_source_files, current_files_info, convert_size, convert_millis, get_duration,\
    seperator as sep, avg_video_size, clear
from prompt_toolkit import print_formatted_text, HTML, prompt


def show_all_files():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    files_info = []
    source_files, n_videos, n_folders = get_source_files()
    avg_vid_sizes = {}
    for keys, values in source_files.items():
        if "Movies" not in keys and len(values) > 2:
            avg_vid_sizes[keys] = avg_video_size([f"{keys}{sep}{x}" for x in values])
        files_info.append(keys)
        files_info.extend(values)
        files_info.append("")
    border_bar = "#" * 98
    display_string = f"""{border_bar}\n"""

    spacing_num = len(str(len(files_info)))
    correct_counter = 0
    curr_dir = ""

    for i in range(len(files_info)):
        if os.path.isdir(files_info[i]) or len(files_info[i]) == 0:
            display_string += f"# ".ljust(spacing_num+4) + current_files_info(i, files_info, 90) + " #\n"
            correct_counter += 1
            curr_dir = files_info[i] if len(files_info[i]) > 0 else curr_dir
            continue

        file_path = f"{curr_dir}{sep}{files_info[i]}"

        size_bytes = os.path.getsize(file_path)
        size_str = f"  <ansired>{convert_size(size_bytes, unit='mb')} MB</ansired>".rjust(33) \
            if avg_vid_sizes.get(curr_dir) is not None and avg_vid_sizes.get(curr_dir) * 0.6 > size_bytes \
            else f"  {convert_size(size_bytes, unit='mb')} MB".rjust(14)

        length = f"  {convert_millis(get_duration(file_path))}".rjust(12)

        front_spacing = spacing_num - len(str(i - correct_counter))
        display_string += f"# {gs}[{i - correct_counter}]{ge} ".ljust(29 + front_spacing) + \
                          f"{current_files_info(i, files_info, 65 - len(str(i - correct_counter)) - front_spacing)}" \
                          f"{size_str}{length} #\n"

    display_string += f"{border_bar}\n\t"
    clear()
    print_formatted_text(HTML(display_string))


def main():
    print("Loading...")
    show_all_files()
    while True:
        action = prompt(HTML("<ansiblue>=> </ansiblue>"))
        if action.lower() == "q":
            return
        if action.lower() == "q!":
            exit(0)
