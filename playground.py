import glob
import os

path = "P:\\video_downloads"
video_paths = glob.glob(path + "/*.mp4") + glob.glob(path + "/*.mkv")

print(video_paths)