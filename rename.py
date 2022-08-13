import glob
import os
import re

# Renaming some specific weird format

for path in glob.glob('P:\\video_downloads\\*.mp4'):
    new_path = re.sub(r'Watch ', '', path)
    new_path = re.sub(r'(?<=S0\dE\d{2}).+', '.mp4', new_path)
    os.rename(path, new_path)
