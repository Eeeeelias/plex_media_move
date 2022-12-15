import os


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
    print_formatted_text(HTML(f"""
    ###################################################################################################################
    #                                                                          # {top_info} #
    # This little tool helps you sort, convert, combine or fix your media      #                                      #
    # files so you can easily give them to Plex or Jellyfin.                   # {current_files_info(0, files_info)} #
    # Just select what you want to do:                                         # {current_files_info(1, files_info)} #
    #                                                                          # {current_files_info(2, files_info)} #
    #                                                                          # {current_files_info(3, files_info)} #
    # [1] {gs}media mover{ge} - moves your media files to your plex folder             # {current_files_info(4, files_info)} #
    #                                                                          # {current_files_info(5, files_info)} #
    # [2] {gs}video edits{ge} - combine, concatenate or cut videos                     # {current_files_info(6, files_info)} #
    #                                                                          # {current_files_info(7, files_info)} #
    # [3] {gs}shifting{ge}    - shift all episode numbers of a show by a given         # {current_files_info(8, files_info)} #
    #                   amount                                                 # {current_files_info(9, files_info)} #
    #                                                                          # {current_files_info(10, files_info)} #
    # [4] {gs}converter{ge}   - convert folders of weird formats (like .ts) into .mp4  # {current_files_info(11, files_info)} #
    #                                                                          # {current_files_info(12, files_info)} #
    # [5] {gs}db search{ge}   - search through your local media database               # {current_files_info(13, files_info)} #
    #                                                                          # {current_files_info(14, files_info)} #
    # [6] {gs}file view{ge}   - view and modify all found files                        # {current_files_info(15, files_info)} #
    #                                                                          # {current_files_info(16, files_info)} #
    # [i] Press [c] to change your config                                      # {current_files_info(17, files_info)} #
    #                                                                          # {current_files_info(18, files_info)} #
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


def main():
    # define a dictionary mapping tool names to functions
    tools = {
        "1": media_mover.main,
        "media mover": media_mover.main,
        "2": ffmpeg_edits.main,
        "combine": ffmpeg_edits.main,
        "video edits": ffmpeg_edits.main,
        "3": rename.main,
        "shifting": rename.main,
        "4": convert_ts.main,
        "converter": convert_ts.main,
        "5": search_db.main,
        "db search": search_db.main,
        "c": change_config.main,
        "6": file_editor.main,
        "file editor": file_editor.main,
        "close": exit_rm,
        "q": exit_rm,
        "quit": exit_rm,
        "exit": exit_rm,
    }

    while True:
        if os.get_terminal_size().columns >= 120:
            greetings_big()
        else:
            greetings()
        tool = prompt(HTML("<ansiblue>=> </ansiblue>"))
        # check if the user entered a valid tool name
        if tool in tools:
            clear()
            tools[tool]()
        else:
            clear()


if __name__ == '__main__':
    from src.mediainfolib import get_config, clear, get_source_files, current_files_info, remove_video_list
    try:
        check_for_setup()
        from src import ffmpeg_edits, convert_ts, search_db, rename, change_config, file_editor
        import media_mover
        from prompt_toolkit import HTML, print_formatted_text, prompt
        from sys import exit
        main()
    except KeyboardInterrupt:
        print("Exiting")
        remove_video_list(get_config()['mover']['orig_path'])
        exit()
