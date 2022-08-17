import re
import os
import glob

movie_title = "YATM"
path = "C:\\Users\\gooog\\Desktop\\Movies"
movie_moves = []
for movie in glob.glob(path + "\\*"):
    print(movie)
    title = re.sub(r"(?=\(\d{4}\)).*", "", movie.split("\\")[-1])
    if os.path.isdir(movie) and movie_title in movie:
        print("Versions of this movie exist. Please name this version")
        version_name = input("Version name: ")
        movie_title_version = movie_title + " - " + version_name + ".mp4"
        movie_moves.append(movie + "\\" + movie_title_version)
    elif os.path.isfile(movie) and movie_title in movie:
        print("This movie exists already. Do you want to add the current one as a version?")
        version_name = input("Press [ENTER] to skip this file or put in the name of the version: ")
        if version_name != "":
            movie_title_version = movie_title + " - " + version_name + ".mp4"
            movie_moves.append(path + "\\" + movie_title + "\\" + movie_title_version)
            print("Now please also add a version name to the existing movie")
            exist_version_name = movie_title + " - " + input("Input the version name of the exisisting movie: ") + ".mp4"
            movie_moves.append(path + "\\" + movie_title + "\\" + exist_version_name)

print(movie_moves)

