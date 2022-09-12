import shutil
from sys import platform

strings_to_match = {
    "2nd Season ": "s02",
    "Season 2 ": "s02",
    "S2 ": "s02",
    "3 Episode ": "s03e0",
    "Episode ": "e0",
}

# set path\\file seperator, thanks windows
if platform == "win32":
    seperator = "\\"
else:
    seperator = "/"


if __name__ == "__main__":
    stre = "de"
    stre.append("sef")
    print(stre)

    orig_path = "P:\\video_downloads"
    plex_path = "P:\\video_downloads"

    # shutil.move("P:\\video_downloads\\Test (2016).mp4", "P:\\script_testing\\Movies")
