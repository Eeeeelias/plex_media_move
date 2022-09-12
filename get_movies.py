import glob

for path in glob.glob('P:\\Plex Shows\\Movies\\*.mp4'):
    print(path.split(sep="\\")[-1])
