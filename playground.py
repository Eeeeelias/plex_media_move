# file for playing around with some functions
# not important
import glob
import os
from media_mover import sorted_alphanumeric
from termcolor import colored, cprint
from sys import platform

if platform == "win32":
    seperator = "\\"
else:
    seperator = "/"


def file_check(path):
    video_sizes = []
    cleaned_video_paths = []
    # do not check for movies
    if "Movies" in path or len(path) < 2:
        return path

    for video in path:
        video_sizes.append(os.path.getsize(video))
    avg_vid_size = sum(video_sizes) / len(video_sizes)

    for video in path:
        vid_size = os.path.getsize(video)
        if avg_vid_size * 0.6 > vid_size:
            cprint("[w] Video with name \"{}\" unusually small: {} MB".format(
                video.split(seperator)[-1], round(vid_size / (1024 ** 2))), "red")
            move = input(colored("[a] Do you want to [m]ove the file regardless, [s]kip it, or [d]elete it "
                                 "altogether?: ", "blue"))
            if move.lower() == "m":
                cleaned_video_paths.append(video)
            elif move.lower() == "d":
                os.remove(video)
    return cleaned_video_paths


if __name__ == '__main__':
    video_paths = glob.glob("{}".format("P:\\script_testing\\TV Shows") + "/*.mp4")
    video_paths = sorted_alphanumeric(video_paths)
    print(file_check(video_paths))

