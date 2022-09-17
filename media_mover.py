import argparse
import glob
import os
import re
import shutil
import time
from sys import platform
import manage_db
import fetch_show_infos
from mediainfolib import check_database_ex
from prompt_toolkit import prompt, HTML, print_formatted_text

# This script renames, organizes and moves your downloaded media files
# If you find bugs/issues or have feature requests send me a message
# It is designed for Plex shows and Audials as a recording software
# Your downloaded folder structure should look like this:
# --/downloaded
# ----/Audials
# ------/Audials TV Shows
# ------/Audials Movies
# ----someFile Episode 2.mp4
# ----someOtherFile Season 3 Episode 1.mkv
#
# Note that only .mp4 and .mkv files are being considered.
#
# Your destination folder should obviously follow the folder structure recommended by Plex.
# To read about that go here:
# https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/
# https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/


# when I did this I did not know that pathlib existed. Now I do.
# windows/linux diffs
if platform == "win32":
    seperator = "\\"
    env = "LOCALAPPDATA"
    folder = "pmm"
else:
    seperator = "/"
    env = "HOME"
    folder = ".pmm"

data_path = os.getenv(env) + seperator + folder
if not os.path.exists(data_path):
    os.mkdir(data_path)

strings_to_match = {
    "2nd Season ": "s02",
    "Season 2 ": "s02",
    "S2 ": "s02",
    "3 Episode ": "s03e0",
    "Episode ": "e0",
}


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        dest="audials",
        action="store_true",
        help="if your orig_path is an audials folder use this " "option",
    )
    parser.add_argument(
        "-o",
        dest="overwrite",
        action="store_true",
        help="define behaviour when file already exists. If"
             " this is set, files will be overwritten. "
             "Otherwise, a numbered version will be moved",
    )
    parser.add_argument("--op", dest="orig_path", help="path to the downloaded videos")
    parser.add_argument("--dp", dest="dest_path", help="path to the destination")
    parser.add_argument(
        "--sv",
        dest="special",
        nargs="*",
        help="special info about a certain show; example: Your "
             "episode (i.e. Better call saul) is named Better call "
             "Saul Episode 20 but you want to mark it season 2. "
             "Then you can write --sv Saul;2 [just one identifier "
             "is fine, using spaces will break it] to make the script "
             "aware that it's season two. You can add "
             "as many of those as you want",
    )
    return parser


def special_info(info):
    info_dict = dict()
    for item in info:
        info_dict[item.split(";")[0]] = item.split(";")[1]
    return info_dict


# overwriting protection
def file_ex_check(new_file, overwrite=False):
    if os.path.isfile(new_file):
        print_formatted_text(HTML("<ansired>[w] File already exists!</ansired>"))
        ext = re.search(r"(\.mp4)|(\.mkv)", new_file).group()
        if (
                overwrite
                or prompt(
            HTML(
                "<ansiblue>[a] Do you want to overwrite the file? [yN]: </ansiblue>"
            )
        )
                == "y"
        ):
            return 0
        i = 2
        new_file = re.sub(ext, f"_{i}" + ext, new_file)
        while os.path.isfile(new_file):
            i += 1
            new_file = re.sub(r"_\d+" + ext, f"_{i}" + ext, new_file)
        return i
    return 0


# checks if movie exists already and gives options to add version names
def movie_checker(movie_title, path, ext=".mp4"):
    movie_moves = []
    for movie in glob.glob(path + "/*"):
        title = re.sub(r"(?<=\(\d{4}\)).*", "", movie.split("\\")[-1])

        # check if there may already be versions of that movie
        if os.path.isdir(movie) and movie_title in movie:
            print_formatted_text(
                HTML(
                    '<ansired>[w] Versions of "{}" exist. Please name this version</ansired>'.format(
                        movie_title
                    )
                )
            )
            version_name = prompt(HTML("<ansiblue>[a] Version name: </ansiblue>"))
            if version_name == "":
                movie_title_version = movie_title + ext
            else:
                movie_title_version = movie_title + " - " + version_name + ext
            while os.path.isfile(movie + "/" + movie_title_version):
                version_name = prompt(
                    HTML(
                        "<ansiblue>[a] This version already exists! Give a valid name: </ansiblue>"
                    )
                )
                movie_title_version = movie_title + " - " + version_name + ext
            print_formatted_text(
                "[i] Movie is now called: {}".format(movie_title_version)
            )
            movie_moves.append(movie + "/" + movie_title_version)

        # check if the movie exists already and move both to a folder with a given version name
        elif os.path.isfile(movie) and movie_title in movie:
            print_formatted_text(
                HTML(
                    '<ansired>[w] "{}" exists already. Do you want to add the current one as a version?</ansired>'.format(
                        movie_title
                    )
                )
            )
            version_name = prompt(
                HTML(
                    "<ansiblue>[a] Put in the name of the version or press [ENTER] to skip this file: </ansiblue>"
                )
            )
            # skip if wanted
            if version_name == "":
                return []

            movie_title_version = movie_title + " - " + version_name + ext
            movie_moves.append(path + "/" + movie_title + "/" + movie_title_version)
            print("[i] Movie is now called: {}".format(movie_title_version))
            print("[i] Now please also add a version name to the existing movie")
            version_name_existing = prompt(
                HTML(
                    "<ansiblue>[a] Input the version name of the existing movie: </ansiblue>"
                )
            )
            exist_vers_name = movie_title + " - " + version_name_existing + ext
            while version_name == version_name_existing:
                version_name_existing = prompt(
                    HTML(
                        "<ansiblue>[a] Both movies can't have the same version name! Please enter a valid version name: "
                        "</ansiblue>"
                    )
                )
                exist_vers_name = movie_title + " - " + version_name_existing + ext
            print(
                '[i] The existing Version will now have "{}" added'.format(
                    version_name_existing
                )
            )
            movie_moves.append(path + "/" + movie_title + "/" + exist_vers_name)
    return movie_moves


def show_checker(path):
    video_sizes = []
    cleaned_video_paths = []
    # do not check for movies or empty directories
    if "Movies" in path or len(path) < 2:
        return path

    for video in path:
        video_sizes.append(os.path.getsize(video))
    avg_vid_size = sum(video_sizes) / len(video_sizes)

    for video in path:
        vid_size = os.path.getsize(video)
        if avg_vid_size * 0.6 > vid_size:
            print_formatted_text(
                HTML(
                    '<ansired>[w] Video with name "{}" unusually small: {} MB</ansired>'.format(
                        video.split(seperator)[-1], round(vid_size / (1024 ** 2))
                    )
                )
            )
            move = prompt(
                HTML(
                    "<ansiblue>[a] Do you want to [m]ove the file regardless, [s]kip it or [d]elete it?: </ansiblue>"
                )
            )
            if move.lower() == "" or move.lower() == "s":
                continue
            elif move.lower() == "d":
                os.remove(video)
                print_formatted_text(
                    "[i] Deleted {}".format(video.split(seperator)[-1])
                )
                continue
        cleaned_video_paths.append(video)
    return cleaned_video_paths


def rename_files(path, special):
    video_paths = glob.glob(path + "/*.mp4") + glob.glob(path + "/*.mkv")
    video_titles_new = []
    if len(video_paths) < 1:
        return video_paths, video_titles_new
    clean_paths = show_checker(sorted_alphanumeric(video_paths))
    video_titles = [title.split(seperator)[-1] for title in clean_paths]
    extra_episode_info = special_info(special)
    print_formatted_text("\n[i] Origin path: {}".format(path))

    for title in video_titles:
        print_formatted_text("[i] Found: {}".format(title))

        special_season = [x for x in extra_episode_info.keys() if x in title]
        if special_season:
            title = title.replace(
                "Episode ", "s0{}e0".format(extra_episode_info.get(special_season[0]))
            )

        for possible_match in strings_to_match.keys():
            if re.search(possible_match, title) is not None:
                title = title.replace(possible_match, strings_to_match[possible_match])

        # mind the space at the beginning
        if re.search(r" [eE]\d{2,4}", title) is not None:
            # possible that e might be upper case
            title = title.replace("e0", "s01e0").replace("E0", "s01e0")
            video_titles_new.append(title)
        else:
            video_titles_new.append(title)
    print_formatted_text("\n")
    return clean_paths, video_titles_new


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(data, key=alphanum_key)


def move_files(video_paths, video_titles_new, plex_path):
    for video_path, video_title in zip(video_paths, video_titles_new):
        print_formatted_text(
            "[i] Original title: {}".format(video_path.split(seperator)[-1])
        )

        if re.search("[sS][0-9]+[eE][0-9]+", video_title) is None:
            movie_title = re.sub(r"(?<=\(\d{4}\)).*", "", video_title)
            ext = re.search(r"(\.mp4)|(\.mkv)", video_title).group()
            # If the movie is a specific version of that movie, make a new folder and put the movie in there
            # as other versions of that movie might get added
            if (
                    re.search(r"(?<=\(\d{4}\)) -.*(?=(.mp4)|(.mkv))", video_title)
                    is not None
            ):
                if args.overwrite:
                    print_formatted_text("[i] Overwriting existing version of movie")
                    shutil.move(video_path, plex_path + "/Movies/" + video_title)
                    continue
                if not os.path.exists(plex_path + "/Movies/" + movie_title):
                    os.makedirs(plex_path + "/Movies/" + movie_title)
                    print_formatted_text("[i] Made new folder: {}".format(movie_title))
                # insert check for file existence here?
                new_path = plex_path + "/Movies/" + movie_title + "/" + video_title
                duplicate_num = file_ex_check(new_path, args.overwrite)
                if duplicate_num != 0:
                    new_path = re.sub(ext, f"_{duplicate_num}" + ext, new_path)
                    time.sleep(2)
                shutil.move(video_path, new_path)
            else:
                movie_paths = movie_checker(movie_title, plex_path + "/Movies", ext=ext)

                if len(movie_paths) > 0:
                    new_path = movie_paths[0]
                else:
                    new_path = plex_path + "/Movies/" + video_title

                if len(movie_paths) == 1:
                    shutil.move(video_path, movie_paths[0])
                elif len(movie_paths) == 2:
                    os.makedirs(plex_path + "/Movies/{}".format(movie_title))
                    shutil.move(
                        plex_path + "/Movies/{}".format(video_title), movie_paths[1]
                    )
                    print_formatted_text(
                        "[i] Moved (Movie): {}".format(movie_paths[1].split("/")[-1])
                    )
                    shutil.move(video_path, movie_paths[0])
                else:
                    shutil.move(video_path, new_path)
            print_formatted_text(
                "[i] Moved (Movie): {}".format(new_path.split("/")[-1])
            )
            continue

        show_name = re.sub(" [sS][0-9]+[eE][0-9]+.*", "", string=video_title)
        season = re.search(r"\d+(?=[eE]\d{1,4})", video_title).group()
        show_path = plex_path + "/TV Shows/" + show_name + "/Season {}/".format(season)

        # make folder for show if it doesn't exist
        if not os.path.exists(plex_path + "/TV Shows/" + show_name):
            print_formatted_text(
                "[i] New Show, making new folder ({})".format(show_name)
            )
            os.makedirs(plex_path + "/TV Shows/" + show_name)

        # make folder for season if it doesn't exist
        if not os.path.exists(show_path):
            print_formatted_text(
                "[i] New Season, making new folder ({}, Season {})".format(
                    show_name, season
                )
            )
            os.makedirs(show_path)
        # if file exists (file_ex_check returns false) add 2 to the file
        duplicate_num = file_ex_check(show_path + video_title, args.overwrite)
        if duplicate_num != 0:
            ext = re.search(r"(\.mp4)|(\.mkv)", video_title).group()
            video_title = re.sub(ext, "_{}".format(duplicate_num) + ext, video_title)
            time.sleep(2)
        shutil.move(video_path, show_path + video_title)
        print_formatted_text("[i] Moved (TV-Show): {}".format(video_title))


def trash_video(path):
    video_paths = glob.glob("{}".format(path) + "/*.mp4")
    video_titles = [title.split(seperator)[-1] for title in video_paths]

    for title in video_titles:
        if re.search("Netflix", title) is not None:
            os.remove(path + "/" + title)


if __name__ == "__main__":
    try:
        parser = make_parser()
        args = parser.parse_args()
        orig_path = args.orig_path.rstrip(seperator)
        plex_path = args.dest_path.rstrip(seperator)
        special = [] if args.special is None else args.special
        if args.audials:
            paths = [
                orig_path,
                orig_path + "/Audials TV Series",
                orig_path + "/Audials Movies",
            ]
        else:
            paths = [
                p
                for p in glob.glob(orig_path + "/**/", recursive=True)
                if not os.path.isfile(p + "/.ignore")
            ]
        db_path = data_path + f"{seperator}media_database.db"
        if not check_database_ex(db_path):
            print_formatted_text("[i] Database not found! Creating...")
            info_shows, info_movies = fetch_show_infos.fetch_all(plex_path)
            manage_db.create_database(db_path, info_shows, info_movies)

        trash_video(orig_path + "/Audials/Audials Other Videos")
        for path in paths:
            video_path_list, video_titles_renamed = rename_files(path, special)
            move_files(video_path_list, video_titles_renamed, plex_path)

        print_formatted_text("[i] Everything done!")
    except FileNotFoundError:
        print_formatted_text(
            "<ansired>[w] Please make sure your paths are written correctly! Couldn't find files</ansired>",
        )
        exit(1)
    except TypeError:
        print_formatted_text(
            "<ansired>[w] There was an error with some of the values you put in! Please double-check those and send "
            "me a message "
            " if that doesn't help! </ansired>"
        )
        exit(1)
    except AttributeError:
        print_formatted_text("<ansired>[w] Make sure you put in the proper arguments! </ansired>")
