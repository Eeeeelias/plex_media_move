import os
import subprocess
import sys
import traceback


def greetings():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #                                                                          #
    # This little tool helps you sort, convert, combine or fix your media      #
    # files so you can easily give them to Plex or Jellyfin.                   #           
    # Just select what you want to do:                                         # 
    #                                                                          #
    #                                                                          #
    # [1] {gs}media mover{ge} - moves your media files to your plex folder             #
    #                                                                          #
    # [2] {gs}video edits{ge} - combine, concatenate or cut videos                     #
    #                                                                          #
    # [3] {gs}shifting{ge}    - shift all episode numbers of a show by a given         #
    #                   amount                                                 #
    #                                                                          #
    # [4] {gs}converter{ge}   - convert folders of weird formats (like .ts) into .mp4  #
    #                                                                          #
    # [5] {gs}db search{ge}   - search through your local media database               #
    #                                                                          #
    # [6] {gs}file view{ge}   - view and modify all found files                        #
    #                                                                          #
    # [i] Press [c] to change your config                                      #
    #                                                                          #
    ############################################################################
    
    
    """))


def greetings_big():
    files_info = []
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    source_files, n_videos, n_folders = get_source_files()
    top_info = f"Found {n_videos} video(s) in {n_folders} folder(s):".ljust(36)
    for keys, values in source_files.items():
        files_info.append(keys)
        files_info.extend(values)
        files_info.append("")
    display_files = current_files_info(18, files_info)
    print_formatted_text(HTML(f"""
    ###################################################################################################################
    #                                                                          # {top_info} #
    # This little tool helps you sort, convert, combine or fix your media      #                                      #
    # files so you can easily give them to Plex or Jellyfin.                   # {display_files[0]} #
    # Just select what you want to do:                                         # {display_files[1]} #
    #                                                                          # {display_files[2]} #
    #                                                                          # {display_files[3]} #
    # [1] {gs}media mover{ge} - moves your media files to your plex folder             # {display_files[4]} #
    #                                                                          # {display_files[5]} #
    # [2] {gs}video edits{ge} - combine, concatenate or cut videos                     # {display_files[6]} #
    #                                                                          # {display_files[7]} #
    # [3] {gs}shifting{ge}    - shift all episode numbers of a show by a given         # {display_files[8]} #
    #                   amount                                                 # {display_files[9]} #
    #                                                                          # {display_files[10]} #
    # [4] {gs}converter{ge}   - convert video files using ffmpeg                       # {display_files[11]} #
    #                                                                          # {display_files[12]} #
    # [5] {gs}db search{ge}   - search through your local media database               # {display_files[13]} #
    #                                                                          # {display_files[14]} #
    # [6] {gs}file view{ge}   - view and modify all found files                        # {display_files[15]} #
    #                                                                          # {display_files[16]} #
    # [i] Press [c] to change your config                                      # {display_files[17]} #
    #                                                                          # {display_files[18]} #
    ###################################################################################################################


    """.replace("&", "&amp;")))


def check_for_setup():
    from src import setup
    if get_config() is None:
        print("[i] No config found! Running setup...")
        setup.set_config()


def exit_rm():
    remove_video_list(get_config()['mover']['orig_path'])
    exit(0)


def get_options():
    from src import ffmpeg_edits, search_db, shifter, change_config, file_editor, log_watch, ffmpeg_convert
    import media_mover
    # define a dictionary mapping tool names to functions
    tools = {
        "1": media_mover.main,
        "mm": media_mover.main,
        "2": ffmpeg_edits.main,
        "combine": ffmpeg_edits.main,
        "ve": ffmpeg_edits.main,
        "3": shifter.main,
        "sf": shifter.main,
        "4": ffmpeg_convert.main,
        "cv": ffmpeg_convert.main,
        "5": search_db.main,
        "db": search_db.main,
        "c": change_config.main,
        "6": file_editor.main,
        "fw": file_editor.main,
        "log": log_watch.main,
        "close": exit_rm,
        "q": exit_rm,
        "quit": exit_rm,
        "exit": exit_rm,
    }
    return tools


def main():
    startup = True
    tools = {}
    while True:
        if os.get_terminal_size().columns >= 120:
            greetings_big()
        else:
            greetings()
        if startup:
            tools = get_options()
            startup = False
        tool = prompt(HTML("<ansiblue>=> </ansiblue>"))
        # check if the user entered a valid tool name
        if tool in tools:
            clear()
            tools[tool]()
        else:
            clear()


if __name__ == '__main__':
    try:
        from src.mediainfolib import get_config, clear, get_source_files, current_files_info, remove_video_list
        while 1:
            try:
                import time
                from prompt_toolkit import HTML, print_formatted_text, prompt
                from sys import exit
                check_for_setup()
                main()
            except KeyboardInterrupt:
                print("Exiting")
                remove_video_list(get_config()['mover']['orig_path'])
                exit()
            except Exception as e:
                print(traceback.print_exc())
                print("If this continues to show up, please message me or open an issue on Github!")
    except ModuleNotFoundError:
        requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", requirements_file])
        print("Restarting!")
        subprocess.check_call([sys.executable, __file__])
        sys.exit()