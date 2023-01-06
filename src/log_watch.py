import re
import os
from typing import List
from src.mediainfolib import data_path, seperator as sep, cut_name, clear
from prompt_toolkit import HTML, print_formatted_text, prompt


def read_log():
    log_file = data_path + f"{sep}mover.log"
    changed_files = []
    with open(log_file, 'r') as f:
        orig = None
        new = None
        time = None
        media_type = None
        for line in f.readlines():
            matches = re.match(r"\[i] Original title: (.*)|\[i] Moved \((.*)\): (.*)|\[i] (\d{4}-\d+-\d+ \d+:\d+:\d+)",
                               line)
            if not matches:
                continue
            if matches.group(4):
                time = matches.group(4)
            if matches.group(1):
                orig = matches.group(1)
            if matches.group(2):
                media_type = matches.group(2)
            if matches.group(3):
                new = matches.group(3)
            if orig and new and media_type and time:
                changed_files.append([orig, new, media_type, time])
                orig, new, media_type = None, None, None
    return changed_files


def print_logs(media: List, length = 20):
    term_size = os.get_terminal_size().columns - 6
    type_size = 7
    time_size = 19
    old_size = int((term_size - type_size - time_size) / 2) - 6
    new_size = int((term_size - type_size - time_size) / 2) - 7
    top = "    " +'#' * term_size
    test = f"    # <ansigreen>{'Original Name'.ljust(old_size)}</ansigreen> | <ansigreen>{'New Name'.ljust(new_size)}</ansigreen> | <ansigreen>{'Type'.ljust(type_size)}</ansigreen> | <ansigreen>{'Time'.ljust(time_size)}</ansigreen> #"
    print(top)
    print_formatted_text(HTML(test))
    for i in media[len(media) - length:]:
        print(f"    # {cut_name(i[0], old_size, pos='mid').ljust(old_size)} | {cut_name(i[1], new_size, pos='mid').ljust(new_size)} | {i[2].ljust(type_size)} | {i[3]} #")
    print(top)


def main():
    curr_length = 20
    logs = read_log()
    while True:
        print_logs(logs, curr_length)
        inp = prompt(HTML("<ansiblue>=> </ansiblue>"))
        if inp.lower() == "m":
            curr_length += 20
        if inp.lower() == "a":
            curr_length = len(logs)
        if inp.lower() == "l":
            curr_length = int(curr_length / 2)
        if inp.lower() == "q":
            clear()
            return
        clear()
