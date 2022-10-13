# experimental, do not use!

import subprocess
import sys
from glob import glob


try:
    files = glob(sys.argv[1] + "/*.mp4")
    print(f"Found {len(files)} videos!")
    for video in files:
        print(f"Downsizing: {video}")
        out = video.replace(".mp4", "_converted.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", video, out])
except IndexError:
    print("Put in the path to the folder you want to convert!")
