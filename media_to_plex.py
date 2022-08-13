import os
import glob
import shutil
import re
import argparse
from sys import platform

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
parser.add_argument('--op', dest='orig_path', help='path to the downloaded videos')
parser.add_argument('--dp', dest='dest_path', help='path to the destination')
parser.add_argument('--sv', dest='special', nargs='*', help='special info about a certain show; example: Your '
                                                            'episode (i.e. Better call saul) is named Better call '
                                                            'Saul Episode 20 but you want to mark it season 2. '
                                                            'Then you can write --sv Saul;2 [just one identifier '
                                                            'is fine, using spaces will break it]. You can add '
                                                            'as many of those as you want')

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


def rename_files(path, special):
    video_paths = glob.glob("{}".format(path) + "/*.mp4")
    video_paths = sorted_alphanumeric(video_paths)
    video_titles = [title.split(seperator)[-1] for title in video_paths]
    video_titles_new = []
    extra_episode_info = special_info(special)

    for title in video_titles:
        special_season = [x for x in extra_episode_info.keys() if x in title]
        if re.search('2nd Season', title) is not None:
            video_titles_new.append(title.replace('2nd Season Episode ', 's02e0'))

        elif re.search('Season 2', title) is not None:
            video_titles_new.append(title.replace('Season 2 Episode ', 's02e0'))

        elif re.search('S2', title) is not None:
            video_titles_new.append(title.replace('S2 Episode ', 's02e0'))

        elif re.search(' 3 Episode', title) is not None:
            video_titles_new.append(title.replace('3 Episode ', 's03e0'))

        elif special_season:
            video_titles_new.append(
                title.replace('Episode ', 's{}e0'.format(extra_episode_info.get(special_season[0]))))

        elif re.search('Episode', title) is not None:
            video_titles_new.append(title.replace('Episode ', 's01e0'))

        else:
            video_titles_new.append(title)
        print("Spotted: {}".format(title))
    return video_paths, video_titles_new


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


def move_files(path, video_paths, video_titles_new, plex_path):
    print('\nDestination path:', path)
    for video_path, video_title in zip(video_paths, video_titles_new):
        original_path = video_path
        os.rename(original_path, path + video_title)

        print('Video title:', video_title)

        # work on this so movies are moved to folders potentially
        if re.search('[sS][0-9]+[eE][0-9]+', video_title) is None:
            shutil.move("{}".format(path + video_title), plex_path + "/Movies/" + video_title)
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

        shutil.move("{}".format(path + video_title), show_path + video_title)
        print("Moved: {}".format(video_title))


def trash_video(path):
    video_paths = glob.glob("{}".format(path) + "/*.mp4")
    video_titles = [title.split(seperator)[-1] for title in video_paths]

    for title in video_titles:
        if re.search('Netflix', title) is not None:
            os.remove(path + "/" + title)


if __name__ == '__main__':
    args = parser.parse_args()
    orig_path = args.orig_path
    plex_path = args.dest_path
    special = args.special

    for path in [orig_path, orig_path + "/Audials/Audials TV Series", orig_path + "/Audials/Audials Movies"]:
        video_path_list, video_titles_renamed = rename_files(path, special)
        move_files(path, video_path_list, video_titles_renamed, plex_path)

    trash_video(orig_path + "/Audials/Audials Other Videos")
