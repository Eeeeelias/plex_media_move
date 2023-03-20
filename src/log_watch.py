import math
import re
import os
from typing import List
from src.mediainfolib import data_path, seperator as sep, cut_name, clear
from prompt_toolkit import HTML, print_formatted_text, prompt


def read_log():
    log_file = data_path + f"{sep}mover.log"
    entries = []
    with open(log_file, 'r') as f:
        for line in f.readlines():
            matches = re.match(r"\[(.*?)] (.*)", line)
            try:
                entries.append([matches.group(1), matches.group(2)])
            except AttributeError:
                continue
    return entries


def print_logs(media: List, length=20, filter=None):
    term_size = os.get_terminal_size().columns - 6
    top = "    " + '#' * term_size
    print(top)
    if filter and filter != "":
        media = [x for x in media if x[0] == filter]
    for i in media[len(media) - length:]:
        max_size = term_size-(len(i[0]) + 7)
        # handling input that's too long
        if len(i[1]) > max_size:
            num_cuts = math.ceil(len(i[1]) / max_size)
            curr = 0
            cuts = []
            for j in range(num_cuts):
                cuts.append(i[1][j + curr:j + max_size + curr])
                curr += max_size - 1
            print_formatted_text(HTML(f"    # <ansigreen>[{i[0]}]</ansigreen> {cuts[0].ljust(max_size)} #"))
            for j in cuts[1:]:
                print_formatted_text(HTML(f"    # {j.ljust(max_size + (len(i[0] ) + 3))} #"))
            continue
        print_formatted_text(HTML(f"    # <ansigreen>[{i[0]}]</ansigreen> {i[1].ljust(max_size)} #"))
    print(top)


def main():
    curr_length = 20
    logs = read_log()
    filter = None
    while True:
        print_logs(logs, curr_length, filter)
        inp = prompt(HTML("<ansiblue>=> </ansiblue>"))
        if inp.lower().startswith("f"):
            filter = inp.lower()[2:]
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
