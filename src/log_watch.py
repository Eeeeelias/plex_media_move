import re
from mediainfolib import data_path, seperator as sep


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


def print_logs():
    pass


if __name__ == "__main__":
    logs = read_log()
    for entry in logs:
        print(entry)
