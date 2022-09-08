import glob
import os.path
import re
import subprocess
import sys
import pathlib

print(f"[i] Converting .ts files in {sys.argv[1]}")
for path in glob.glob(sys.argv[1] + "/*.ts"):
    dirname, name = os.path.split(path)
    new_name = re.sub(r".ts", ".mp4", os.path.basename(path))
    print(f"[i] Converting to: {pathlib.Path(dirname, new_name)}")
    subprocess.run(["ffmpeg", "-loglevel", "warning", "-i", path, "-c", "copy", pathlib.Path(dirname, new_name)])
    print("[i] Removing original file")
    os.remove(path)
