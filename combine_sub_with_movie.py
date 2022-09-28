import glob
import os
import subprocess
import sys
from mediainfolib import seperator as sep


def fetch_files(movie_path):
    folders = [os.path.join(movie_path, x) for x in os.listdir(movie_path) if
               os.path.isdir(os.path.join(movie_path, x))]
    rel_folder = []
    for folder in folders:
        if glob.glob(folder + "/*.de.srt") and not glob.glob(folder + "/.tmp"):
            rel_folder.append(glob.glob(folder + "/*"))
    return rel_folder


def sub_in_movie(movie_files, out_path):
    sub_de = movie_files[0]
    sub_en = movie_files[1]
    movie = movie_files[2]
    out = out_path + f"{sep}" + os.path.split(movie)[1]
    print("Movie: {}\nGer Subs: {}\nEng Subs: {}".format(os.path.split(movie)[1], os.path.split(sub_de)[1],
                                                         os.path.split(sub_en)[1]))
    ffmpeg = ["ffmpeg", "-i", movie, "-f", "srt", "-i", sub_de, "-f", "srt", "-i", sub_en, "-map", "0:0", "-map", "0:1",
              "-map", "0:2", "-map", "1:0", "-map", "2:0", "-c:v", "copy", "-c:a", "copy", "-c:s", "srt",
              "-metadata:s:s:0", "language=de", "-metadata:s:s:1", "language=en", out]
    for i in ffmpeg:
        print(i, end=" ")
    subprocess.run(ffmpeg)


if __name__ == '__main__':
    subs_to_combine = fetch_files(sys.argv[1])
    for movie in subs_to_combine:
        sub_in_movie(movie, sys.argv[2])
