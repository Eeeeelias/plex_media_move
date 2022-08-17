import argparse
import glob
import os
import re
import shutil
import time
from sys import platform

from termcolor import cprint, colored

# This script renames, organizes and moves your downloaded media files
# If you find bugs/issues or have feature requests send me a message
# It is designed for Plex shows and Audials as a recording software
# Your downloaded folder structure should look like this:
# --/downloaded
# ----/Audials
# ------/Audials TV Shows
# ------/Audials Movies
# ----someFile Episode 2.mp4
# ----someOtherFile Season 3 Episode 1.mp4
#
# Note that only .mp4 files are being considered.
#
# Your destination folder should obviously follow the folder structure recommended by Plex.
# To read about that go here:
# https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/
# https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/


parser = argparse.ArgumentParser()
parser.add_argument('-a', dest='audials', action='store_true', help='if your orig_path is an audials folder use this '
                                                                    'option')
parser.add_argument('-o', dest='overwrite', action='store_true', help='define behaviour when file already exists. If'
                                                                      ' this is set, files will be overwritten. '
                                                                      'Otherwise, a numbered version will be moved')
parser.add_argument('--op', dest='orig_path', help='path to the downloaded videos')
parser.add_argument('--dp', dest='dest_path', help='path to the destination')
parser.add_argument('--sv', dest='special', nargs='*', help='special info about a certain show; example: Your '
                                                            'episode (i.e. Better call saul) is named Better call '
                                                            'Saul Episode 20 but you want to mark it season 2. '
                                                            'Then you can write --sv Saul;2 [just one identifier '
                                                            'is fine, using spaces will break it] to make the script '
                                                            'aware that it\'s season two. You can add '
                                                            'as many of those as you want')

strings_to_match = {'2nd Season ': 's02',
                    'Season 2 ': 's02',
                    'S2 ': 's02',
                    '3 Episode ': 's03e0',
                    'Episode ': 'e0'}

# set path\\file seperator, thanks windows
if platform == 'win32':
    seperator = "\\"
else:
    seperator = "/"


def special_info(info):
    info_dict = dict()
    for item in info:
        info_dict[item.split(';')[0]] = item.split(';')[1]
    return info_dict


# overwriting protection
def file_ex_check(new_file, overwrite=False):
    if os.path.isfile(new_file):
        cprint("[W] File already exists!", "red")
        if not overwrite:
            i = 2
            new_file = re.sub(".mp4", "_{}.mp4".format(i), new_file)
            while os.path.isfile(new_file):
                i += 1
                new_file = re.sub(r"_\d+.mp4", "_{}.mp4".format(i), new_file)
            return i
    return 0


# checks if movie exists already and gives options to add version names
def movie_checker(movie_title, path):
    movie_moves = []
    for movie in glob.glob(path + "/*"):
        title = re.sub(r"(?<=\(\d{4}\)).*", "", movie.split("\\")[-1])
        # check if there may already be versions of that movie
        if os.path.isdir(movie) and movie_title in movie:
            cprint("[W] Versions of \"{}\" exist. Please name this version".format(movie_title), "red")
            version_name = input(colored("[A] Version name: ", "blue"))
            movie_title_version = movie_title + " - " + version_name + ".mp4"
            while os.path.isfile(movie + "/" + movie_title_version):
                version_name = input(colored("[A] This version already exists! Give a valid name: ", "blue"))
                movie_title_version = movie_title + " - " + version_name + ".mp4"
            cprint("[I] Movie is now called: {}".format(movie_title_version))
            movie_moves.append(movie + "/" + movie_title_version)
        # check if the movie exists already and move both to a folder with a given version name
        elif os.path.isfile(movie) and movie_title in movie:
            cprint("[W] \"{}\" exists already. Do you want to add the current one as a version?".format(movie_title),
                   "red")
            version_name = input(colored("[A] Put in the name of the version or press [ENTER] to skip this file: ", "blue"))
            if version_name != "":
                movie_title_version = movie_title + " - " + version_name + ".mp4"
                movie_moves.append(path + "/" + movie_title + "/" + movie_title_version)
                print("[I] Movie is now called: {}".format(movie_title_version))
                print("[I] Now please also add a version name to the existing movie")
                version_name_existing = input(colored("[A] Input the version name of the exisisting movie: ", "blue"))
                exist_vers_name = movie_title + " - " + version_name_existing + ".mp4"
                while version_name == version_name_existing:
                    version_name_existing = input(colored("[A] Both movies can't have the same version name! Please enter a "
                                                  "valid version name: ", "blue"))
                print("[I] The existing Version will now have \"{}\" added".format(version_name_existing))
                movie_moves.append(path + "/" + movie_title + "/" + exist_vers_name)
    return movie_moves


def rename_files(path, special):
    video_paths = glob.glob("{}".format(path) + "/*.mp4")
    video_paths = sorted_alphanumeric(video_paths)
    video_titles = [title.split(seperator)[-1] for title in video_paths]
    video_titles_new = []
    extra_episode_info = special_info(special)

    for title in video_titles:
        cprint("[I] Spotted: {}".format(title))

        special_season = [x for x in extra_episode_info.keys() if x in title]
        if special_season:
            title = title.replace('Episode ', 's{}e0'.format(extra_episode_info.get(special_season[0])))

        for possible_match in strings_to_match.keys():
            if re.search(possible_match, title) is not None:
                title = title.replace(possible_match, strings_to_match[possible_match])

        # mind the space at the beginning
        if re.search(r' [eE]\d{2,4}', title) is not None:
            # possible that e might be upper case
            title = title.replace('e0', 's01e0').replace('E0', 's01e0')
            video_titles_new.append(title)
        else:
            video_titles_new.append(title)

    return video_paths, video_titles_new


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


def move_files(path, video_paths, video_titles_new, plex_path):
    if len(video_titles_new) > 0:
        cprint('\n[I] Origin path: {}'.format(path))
    for video_path, video_title in zip(video_paths, video_titles_new):
        cprint('[I] Video title:{}'.format(video_title))

        if re.search('[sS][0-9]+[eE][0-9]+', video_title) is None:
            movie_title = re.sub(r'(?<=\(\d{4}\)).*', '', video_title)
            # If the movie is a specific version of that movie, make a new folder and put the movie in there
            # as other versions of that movie might get added
            if re.search(r'(?<=\(\d{4}\)) -.*(?=.mp4)', video_title) is not None:
                if not os.path.exists(plex_path + "/Movies/" + movie_title):
                    os.makedirs(plex_path + "/Movies/" + movie_title)
                    cprint('[I] Made new folder:', movie_title)
                # insert check for file existence here?
                new_path = plex_path + "/Movies/" + movie_title + "/" + video_title
                duplicate_num = file_ex_check(new_path, args.overwrite)
                if duplicate_num != 0:
                    new_path = re.sub(".mp4", "_{}.mp4".format(duplicate_num), new_path)
                    time.sleep(2)
                shutil.move(video_path, new_path)
            # this part sucks but I'll redo it with more options!
            else:
                movie_paths = movie_checker(movie_title, plex_path + "/Movies")

                if len(movie_paths) > 0:
                    new_path = movie_paths[0]
                else:
                    new_path = plex_path + "/Movies/" + video_title

                if len(movie_paths) == 1:
                    shutil.move(video_path, movie_paths[0])
                elif len(movie_paths) == 2:
                    os.makedirs(plex_path + "/Movies/{}".format(movie_title))
                    shutil.move(plex_path + "/Movies/{}".format(video_title),
                                movie_paths[1])
                    cprint('[I] Moved (Movie): {}'.format(movie_paths[1].split("/")[-1]))
                    shutil.move(video_path, movie_paths[0])
                else:
                    shutil.move(video_path, new_path)
            cprint('[I] Moved (Movie): {}'.format(new_path.split("/")[-1]))
            continue

        show_name = re.sub(' [sS][0-9]+[eE][0-9]+.*', '', string=video_title)
        season = re.search(r'\d+(?=[eE]\d{1,4})', video_title).group()
        show_path = plex_path + "/TV Shows/" + show_name + "/Season {}/".format(season)

        # make folder for show if it doesn't exist
        if not os.path.exists(plex_path + "/TV Shows/" + show_name):
            cprint('[I] New Show, making new folder ({})'.format(show_name))
            os.makedirs(plex_path + "/TV Shows/" + show_name)

        # make folder for season if it doesn't exist
        if not os.path.exists(show_path):
            cprint('[I] New Season, making new folder ({}, Season {})'.format(show_name, season))
            os.makedirs(show_path)
        # if file exists (file_ex_check returns false) add 2 to the file
        duplicate_num = file_ex_check(show_path + video_title, args.overwrite)
        if duplicate_num != 0:
            video_title = re.sub(".mp4", "_{}.mp4".format(duplicate_num), video_title)
            time.sleep(2)
        shutil.move(video_path, show_path + video_title)
        cprint("[I] Moved (TV-Show): {}".format(video_title))


def trash_video(path):
    video_paths = glob.glob("{}".format(path) + "/*.mp4")
    video_titles = [title.split(seperator)[-1] for title in video_paths]

    for title in video_titles:
        if re.search('Netflix', title) is not None:
            os.remove(path + "/" + title)


if __name__ == '__main__':
    try:
        args = parser.parse_args()
        orig_path = args.orig_path
        plex_path = args.dest_path
        special = args.special
        if special is None:
            special = []

        if args.audials:
            paths = [orig_path, orig_path + "/Audials TV Series", orig_path + "/Audials Movies"]
        else:
            paths = [p for p in glob.glob(orig_path + "/**/", recursive=True)]

        for path in paths:
            video_path_list, video_titles_renamed = rename_files(path, special)
            move_files(path, video_path_list, video_titles_renamed, plex_path)

        trash_video(orig_path + "/Audials/Audials Other Videos")
        cprint('[I] Everything done!')
    except FileNotFoundError:
        cprint("[W] Please make sure your paths are written correctly! Remove trailing \\ if you added them.", "red")
        exit(1)
    except TypeError:
        cprint(
            "[I] There was an error with some of the values you put in! Please double-check those and send me a message"
            " if that doesn't help!", "red")
        exit(1)
