import argparse
import glob
import os
import re
import shutil
import sys
import time
import logging
from sys import platform
from src import manage_db, mediainfolib
from src.mediainfolib import check_database_ex, sorted_alphanumeric, fuzzy_matching, avg_video_size, read_existing_list, \
    logger
from prompt_toolkit import prompt, HTML, print_formatted_text

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

strings_to_match = {
    "2nd Season ": "S02",
    "Season 2 ": "S02",
    "Season 3 ": "S03",
    "Season 4 ": "S04",
    "Season 5 ": "S05",
    "S2 ": "S02",
    "3 Episode ": "S03E0",
    "OVA ": "E00",
    "Episode ": "E0",
}

# save fuzzy matches here so user choice is remembered for current session
matches = {}

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
    parser.add_argument("--no_db", dest="use_db", action="store_true",
                        help="Using this option will prevent the usage of the database")
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
        if overwrite or prompt(HTML("<ansiblue>[a] Do you want to overwrite the file? [y/N]: </ansiblue>")) == "y":
            return 0
        i = 2
        new_file = re.sub(ext, f"_{i}" + ext, new_file)
        while os.path.isfile(new_file):
            i += 1
            new_file = re.sub(r"_\d+" + ext, f"_{i}" + ext, new_file)
        return i
    return 0


# rewrite this entire function, it doesn't make any sense

def movie_checker(movie_title, path, ext=".mp4"):
    movie_moves = []
    invalid_exts = ['.nfo', '.jpg', '.png', '.srt', '.svg', '.txt', '.url', '.xml']
    name_version = False
    for movie in glob.glob(path + "/*"):
        if os.path.isfile(movie) and os.path.splitext(movie)[1] in invalid_exts:
            continue
        # replace or not if the current one has the exact same name as the existing one
        if os.path.isfile(movie):
            print_formatted_text(HTML('<ansired>[w] "{}" exists already. Overwrite [y], Version [v] or Ignore [n]?'
                                      '</ansired>'.format(movie_title.replace('&', '&amp;'))))
            overwrite = prompt(HTML("<ansiblue>=></ansiblue>"))
            if overwrite.lower() == "y":
                movie_moves.append(path + "/" + movie_title + ext)
                continue
            elif overwrite.lower() == "v":
                name_version = True
            else:
                return None

        if name_version:
            print_formatted_text(
                HTML('<ansired>[w] Please name this version</ansired>'.format(movie_title.replace('&', '&amp;'))))
            version_name = prompt(HTML("<ansiblue>[a] Version name: </ansiblue>"))
            if version_name == "":
                movie_title_version = movie_title + ext
            else:
                movie_title_version = movie_title + " - " + version_name + ext
            while os.path.isfile(movie + "/" + movie_title_version):
                version_name = prompt(
                    HTML("<ansiblue>[a] This version already exists! Give a valid name: </ansiblue>"))
                movie_title_version = movie_title + " - " + version_name + ext
            print_formatted_text("[i] Movie is now called: {}".format(movie_title_version.replace('&', '&amp;')))
            movie_moves.append(path + "/" + movie_title_version)
            print(movie_moves)
            time.sleep(3)

    return movie_moves


def show_checker(path):
    video_sizes = []
    cleaned_video_paths = []
    # do not check for movies or empty directories
    if "Movies" in path or len(path) < 2:
        return path

    avg_vid_size = avg_video_size(path)

    for video in path:
        vid_size = os.path.getsize(video)
        if avg_vid_size * 0.6 > vid_size:
            print_formatted_text(HTML(
                '<ansired>[w] Video with name "{}" unusually small: {} MB</ansired>'.format(
                    video.split(seperator)[-1], round(vid_size / (1024 ** 2)))))
            move = prompt(HTML(
                "<ansiblue>[a] Do you want to [m]ove the file regardless, [s]kip it or [d]elete it?: </ansiblue>"))
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


def get_movie_year(filename):
    filename_with_year = filename
    filename_split = os.path.splitext(filename)
    if re.search(r"\(\d{4}\)", filename_split[0]) is None:
        year = prompt(HTML(f'<ansiblue>[a] \"{filename_split[0]}\" appears to not have a proper year! Please specify '
                           f'the year the movie came out: </ansiblue>'))
        if re.search(r"\d{4}", year) is None:
            year = 1900
        # get rid of () in case Audials adds it (i.e. when it can't find the year for a movie)
        filename_clear = re.sub(r" \(\)", "", filename_split[0])
        filename_with_year = filename_clear + f" ({year})" + filename_split[1]
    return filename_with_year


def rename_files(path, special):
    video_paths = glob.glob(path + "/*.mp4") + glob.glob(path + "/*.mkv")
    video_titles_new = []
    if len(video_paths) < 1:
        return video_paths, video_titles_new
    clean_paths = show_checker(sorted_alphanumeric(video_paths))
    video_titles = [os.path.basename(title) for title in clean_paths]
    extra_episode_info = special_info(special)
    if os.path.isfile(f"{path}/video_list.tmp"):
        possible_special = read_existing_list(path)
        if len(set([x[3] for x in possible_special if x != "SXX"])) > 0:
            extras = []
            for poss in possible_special:
                if poss[3] != "SXX" and poss[3] != "NaN":
                    extras.append(f"{os.path.basename(poss[1])};{int(poss[3][1:])}")
            extra_episode_info.update(special_info(extras))
    print_formatted_text("\n[i] Origin path: {}".format(path))

    for title in video_titles:
        print_formatted_text("[i] Found: {}".format(title))
        special_season = [x for x in extra_episode_info.keys() if x in title]
        if special_season:
            title = title.replace("Episode ", "S0{}E0".format(extra_episode_info.get(special_season[0])))

        for possible_match in strings_to_match.keys():
            if re.search(possible_match, title) is not None:
                title = title.replace(possible_match, strings_to_match[possible_match])

        # mind the space at the beginning
        if re.search(r" [eE]\d{2,4}", title) is not None:
            # possible that e might be upper case
            title = title.replace("e0", "S01E0").replace("E0", "S01E0")
            video_titles_new.append(title)
        else:
            title_with_year = title
            if re.search(r"[sS]\d+[eE]\d+", title) is None:
                title_with_year = get_movie_year(title)
            video_titles_new.append(title_with_year)
    print_formatted_text("\n")
    return clean_paths, video_titles_new


def viewer_rename(num_list, src_path, modifier):
    paths = []
    names = []
    libraries = []
    files = read_existing_list(src_path)

    for file in files:
        # if num list is empty, all values should be considered
        if int(file[0]) in num_list or num_list == []:
            ext = os.path.splitext(file[1])[1]
            paths.append(file[1])
            libraries.append(file[10])
            if file[3] != "NaN":
                if file[9] == "Y":
                    names.append(f"{file[2]} {file[3]}{file[4]} - {file[8]}{ext}")
                else:
                    names.append(f"{file[2]} {file[3]}{file[4]}{ext}")
            else:
                name_with_year = get_movie_year(os.path.basename(file[2])) + os.path.splitext(file[1])[1]
                names.append(f"{name_with_year}")
    return paths, names, libraries


def get_show_name_season(show_dir, video_title):
    orig_show_name = re.sub(" [sS][0-9]+[eE][0-9]+.*", "", string=video_title)
    orig_season = re.search(r"\d+(?=[eE]\d{1,4})", video_title).group()
    new_show_name = orig_show_name
    new_season = orig_season
    fuzzy_match, ratio = fuzzy_matching(show_dir, orig_show_name)
    if fuzzy_match is not None and ratio < 1:
        print(
            "[i] \'{}\' and \'{}\' might be the same show. ({:.0f}% similarity)".format(fuzzy_match, orig_show_name, ratio * 100))
        if fuzzy_match in matches.keys():
            return matches[fuzzy_match], new_season
        keep_original = prompt(HTML("<ansiblue>[a] Do you want to keep the original name? [y/N] </ansiblue>")).lower()
        if keep_original == "n":
            new_show_name = fuzzy_match
            keep_season = prompt(HTML(f"<ansiblue>[a] Do you want to keep the season? (Current: {orig_season})\n"
                                      f"[ENTER] to keep, digit to override: </ansiblue>")).lower()
            if keep_season.isdigit():
                # making sure the leading zero is there
                new_season = keep_season if keep_season.startswith("0") else f"0{keep_season}"
        matches[fuzzy_match] = new_show_name
    return new_show_name, new_season


def move_files(video_paths, video_titles_new, plex_path, libraries, overwrite) -> set[str]:
    moved_videos = set()
    if len(video_paths) > 0:
        logger.debug(f"\n[mover] {time.strftime('%Y-%m-%d %H:%M:%S')} - received {len(video_paths)} files to move")
    for video_path, video_title, library in zip(video_paths, video_titles_new, libraries):
        logger.info("[mover] Original title: {}".format(os.path.basename(video_path)))
        # Taking care of movies here
        if re.search("[sS][0-9]+[eE][0-9]+", video_title) is None:
            # delete the file extension
            movie_title = re.sub(r"(?<=\(\d{4}\)).*", "", video_title)
            try:
                ext = re.search(r"(\.mp4)|(\.mkv)", video_title).group()
            except AttributeError:
                # get the file extension from the file itself
                ext = os.path.splitext(video_path)[1]
            if not os.path.exists(plex_path + "/Movies/" + movie_title):
                os.mkdir(plex_path + "/Movies/" + movie_title)
            # If the movie is a specific version of that movie, make a new folder and put the movie in there
            # as other versions of that movie might get added
            if re.search(r"(?<=\(\d{4}\)) -.*(?=(.mp4)|(.mkv))", video_title) is not None:
                if overwrite:
                    logger.info("[mover] Overwriting existing version of movie if it exists")
                    new_path = plex_path + "/Movies/" + f"{movie_title}/" + video_title
                    shutil.copy(video_path, new_path)
                    moved_videos.add(new_path)
                    continue
                new_path = plex_path + "/Movies/" + movie_title + "/" + video_title
                duplicate_num = file_ex_check(new_path, overwrite)
                if duplicate_num != 0:
                    new_path = re.sub(ext, f"_{duplicate_num}" + ext, new_path)
                    time.sleep(2)
                shutil.move(video_path, new_path)
                moved_videos.add(new_path)
            else:
                movie_paths = movie_checker(movie_title, f"{plex_path}/Movies/{movie_title}", ext=ext)

                # something about this is not smart
                if movie_paths is None:
                    continue
                if len(movie_paths) > 0:
                    new_path = movie_paths[0]
                else:
                    new_path = f"{plex_path}/Movies/{movie_title}/{video_title}"

                if len(movie_paths) == 1:
                    shutil.move(video_path, movie_paths[0])
                    moved_videos.add(movie_paths[0])
                elif len(movie_paths) == 2:
                    os.makedirs(plex_path + "/Movies/{}".format(movie_title))
                    shutil.move(plex_path + "/Movies/{}".format(video_title), movie_paths[1])
                    moved_videos.add(movie_paths[1])
                    logger.info("[mover] Moved (Movie): {}".format(movie_paths[1].split("/")[-1]))
                    shutil.move(video_path, movie_paths[0])
                    moved_videos.add(movie_paths[0])
                else:
                    shutil.move(video_path, new_path)
                    moved_videos.add(new_path)
            logger.info("[mover] Moved (Movie): {}".format(new_path.split("/")[-1]))
            continue

        # check for show name similarity here and change if needed?
        show_name, season = get_show_name_season(plex_path + f"/{library}/", video_title)

        # add this so the changed show name is in the file name for consistency
        video_title = re.sub(r"[sS]\d+(?=[eE]\d)", f"S{season}", video_title)
        orig_show_name = re.sub(" [sS][0-9]+[eE][0-9]+.*", "", string=video_title)
        video_title = re.sub(orig_show_name, show_name, video_title)

        show_path = plex_path + f"/{library}/" + show_name + "/Season {}/".format(season)
        # for db check
        show_path_without_season = plex_path + f"{seperator}{library}{seperator}" + show_name

        # make folder for show if it doesn't exist
        if not os.path.exists(plex_path + f"/{library}/" + show_name):
            logger.info("[mover] New Show, making new folder ({})".format(show_name))
            os.makedirs(plex_path + f"/{library}/" + show_name)

        # make folder for season if it doesn't exist
        if not os.path.exists(show_path):
            logger.info("[mover] New Season, making new folder ({}, Season {})".format(show_name, season))
            os.makedirs(show_path)

        # if file exists (file_ex_check returns false) add 2 to the file
        duplicate_num = file_ex_check(show_path + video_title, overwrite)
        if duplicate_num != 0:
            ext = re.search(r"(\.mp4)|(\.mkv)", video_title).group()
            video_title = re.sub(ext, "_{}".format(duplicate_num) + ext, video_title)
            time.sleep(2)
        shutil.move(video_path, show_path + video_title)
        moved_videos.add(show_path_without_season)
        logger.info("[mover] Moved (TV-Show): {}".format(video_title))
    return moved_videos


def trash_video(path):
    video_paths = glob.glob("{}".format(path) + "/*.mp4")
    video_titles = [title.split(seperator)[-1] for title in video_paths]

    for title in video_titles:
        if re.search("Netflix", title) is not None:
            os.remove(path + "/" + title)


def main():
    try:
        parser = make_parser()
        args = parser.parse_args()
        conf = mediainfolib.get_config()
        use_db = True
        if conf:
            db_path = conf['database']['db_path'] + f"{seperator}media_database.db"
        else:
            print_formatted_text("[i] Consider running setup.py to set up default values and a database!")
            db_path = ""
        # setting variables with argparse if supplied, else from config
        if len(sys.argv) > 1:
            orig_path = args.orig_path.rstrip(seperator)
            plex_path = args.dest_path.rstrip(seperator)
            use_db = False if args.use_db else True
            special = [] if args.special is None else args.special
            overwrite = True if args.overwrite else False
            if args.audials:
                paths = [
                    orig_path,
                    orig_path + "/Audials TV Series",
                    orig_path + "/Audials Movies",
                ]
            else:
                paths = [p for p in glob.glob(orig_path + f"/**/", recursive=True)
                         if not os.path.isfile(p + "/.ignore")]
        else:
            orig_path = conf['mover']['orig_path']
            plex_path = conf['mover']['dest_path']
            _special = conf['mover']['special'].split(" ")
            special = [] if _special[0] == '' else _special
            overwrite = conf['mover']['overwrite']
            paths = [p for p in glob.glob(orig_path + f"/**/", recursive=True) if not os.path.isfile(p + "/.ignore")]
        trash_video(orig_path + "/Audials/Audials Other Videos")
        for path in paths:
            video_path_list, video_titles_renamed = rename_files(path, special)
            moved_files = move_files(video_path_list, video_titles_renamed, plex_path, ["TV Shows"]*len(video_path_list), overwrite)
            if check_database_ex(db_path) and use_db:
                manage_db.update_database(moved_files, db_path)

        print_formatted_text("[i] Everything done!")
    except FileNotFoundError:
        print_formatted_text(HTML(
            "<ansired>[w] Please make sure your paths are written correctly! Couldn't find files</ansired>")
        )
        exit(1)
    except TypeError:
        # traceback.print_exc()
        if conf:
            for value in conf['mover'].values():
                if value is None:
                    print_formatted_text(
                        HTML("<ansired>[w] You don't have the relevant infos in your config!</ansired>"))
                    return
        print_formatted_text(HTML(
            "<ansired>[w] There was an error with some of the values you put in! Please double-check those and send "
            "me a message if that doesn't help! </ansired>")
        )
        exit(1)
    except AttributeError as e:
        print(e)
        print_formatted_text(HTML("<ansired>[w] Make sure you put in the proper arguments! </ansired>"))
    except KeyboardInterrupt:
        print_formatted_text("[i] Stopping")
        exit(0)


if __name__ == "__main__":
    main()
