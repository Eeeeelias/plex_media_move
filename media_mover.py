import os
import glob
import shutil
import re
import argparse
from sys import platform
import time

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


# Test Episode 1.mp4
def file_ex_check(new_file, overwrite=False):
    if os.path.isfile(new_file):
        print("WARNING: File already exists!")
        if not overwrite:
            i = 2
            new_file = re.sub(".mp4", "_{}.mp4".format(i), new_file)
            while os.path.isfile(new_file):
                new_file = re.sub(r"_\d*.mp4", "_{}.mp4".format(i), new_file)
                i += 1
            return i
    return 0


def rename_files(path, special):
    video_paths = glob.glob("{}".format(path) + "/*.mp4")
    video_paths = sorted_alphanumeric(video_paths)
    video_titles = [title.split(seperator)[-1] for title in video_paths]
    video_titles_new = []
    extra_episode_info = special_info(special)

    for title in video_titles:
        print("Spotted: {}".format(title))

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
        print('\nOrigin path:', path)
    for video_path, video_title in zip(video_paths, video_titles_new):
        print('Video title:', video_title)

        if re.search('[sS][0-9]+[eE][0-9]+', video_title) is None:
            # If the movie is a specific version of that movie, make a new folder and put the movie in there
            # as other versions of that movie might get added
            if re.search(r'(?<=\(\d{4}\)) -.*(?=.mp4)', video_title) is not None:
                movie_title = re.sub(r'(?<=\(\d{4}\)) -.*', '', video_title)
                if not os.path.exists(plex_path + "/Movies/" + movie_title):
                    os.makedirs(plex_path + "/Movies/" + movie_title)
                    print('Made new folder:', movie_title)
                # insert check for file existence here?
                # make options available....as input modular
                new_path = plex_path + "/Movies/" + movie_title + "/" + video_title
                duplicate_num = file_ex_check(new_path, args.overwrite)
                if duplicate_num != 0:
                    new_path = re.sub(".mp4", "_{}.mp4".format(duplicate_num), new_path)
                    time.sleep(5)
                shutil.move(video_path, new_path)
            # this part sucks but I'll redo it with more options!
            else:
                new_path = plex_path + "/Movies/" + video_title
                duplicate_num = file_ex_check(new_path, args.overwrite)
                if duplicate_num != 0:
                    new_path = re.sub(".mp4", "_{}.mp4".format(duplicate_num), new_path)
                    time.sleep(5)
                shutil.move(video_path, new_path)
            print('Moved (Movie):', new_path.split("/")[-1])
            continue

        show_name = re.sub(' [sS][0-9]+[eE][0-9]+.*', '', string=video_title)
        season = re.search(r'\d(?=[eE]\d{1,4})', video_title).group()
        show_path = plex_path + "/TV Shows/" + show_name + "/Season {}/".format(season)

        # make folder for show if it doesn't exist
        if not os.path.exists(plex_path + "/TV Shows/" + show_name):
            print('New Show, making new folder ({})'.format(show_name))
            os.makedirs(plex_path + "/TV Shows/" + show_name)

        # make folder for season if it doesn't exist
        if not os.path.exists(show_path):
            print('New Season, making new folder ({}, Season {})'.format(show_name, season))
            os.makedirs(show_path)
        # if file exists (file_ex_check returns false) add 2 to the file
        duplicate_num = file_ex_check(show_path + video_title, args.overwrite)
        if duplicate_num != 0:
            video_title = re.sub(".mp4", "_{}.mp4".format(duplicate_num), video_title)
            time.sleep(5)
        shutil.move(video_path, show_path + video_title)
        print("Moved (TV-Show): {}".format(video_title))

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
        print('Everything done!')
    except FileNotFoundError:
        print("Please make sure your paths are written correctly! Remove trailing \\ if you added them.")
        exit(1)
    except TypeError:
        print("There was an error with some of the values you put in! Please double-check those and send me a message"
              " if that doesn't help!")
        exit(1)
