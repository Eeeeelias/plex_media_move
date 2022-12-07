import os.path

from src.mediainfolib import get_source_files, current_files_info, convert_size, convert_millis, get_duration, seperator as sep
from prompt_toolkit import print_formatted_text, HTML, prompt


def show_all_files():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    files_info = []
    source_files, n_videos, n_folders = get_source_files()
    for keys, values in source_files.items():
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
        size = f"  {convert_size(os.path.getsize(file_path), unit='mb')} MB".rjust(14)
        length = f"  {convert_millis(get_duration(file_path))}".rjust(12)
        # Name Show____0h 50m____1234.34 MB

        front_spacing = spacing_num - len(str(i - correct_counter))
        display_string += f"# {gs}[{i - correct_counter}]{ge} ".ljust(29 + front_spacing) + \
                          current_files_info(i, files_info, 65 - len(str(i - correct_counter)) - front_spacing) + \
                          size + length + " #\n"

    display_string += f"{border_bar}\n\t"
    print_formatted_text(HTML(display_string))



def main():
    show_all_files()
    while True:
        action = prompt(HTML("<ansiblue>=> </ansiblue>"))
        if action.lower() == "q":
            return
        if action.lower() == "q!":
            exit(0)
