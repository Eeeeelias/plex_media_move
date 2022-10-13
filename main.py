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


def check_for_setup():
    from src import setup
    if get_config() is None:
        print("[i] No config found! Running setup...")
        setup.set_config()


def main():
    while 1:
        greetings()
        tool = prompt(HTML("<ansiblue>=> </ansiblue>"))
        if tool in ["1",  "media mover"]:
            clear()
            media_mover.main()
        elif tool in ["2", "combine", "video edits"]:
            clear()
            ffmpeg_edits.main()
        elif tool in ["3", "shifting"]:
            clear()
            rename.main()
        elif tool in ["4", "converter"]:
            clear()
            convert_ts.main()
        elif tool in ["5", "db search"]:
            clear()
            search_db.main()
        elif tool == "c":
            clear()
            change_config.main()
        elif tool in ["close", "q", "quit", "exit"]:
            exit(0)
        else:
            clear()


if __name__ == '__main__':
    from src.mediainfolib import get_config, clear
    try:
        check_for_setup()
        from src import ffmpeg_edits, convert_ts, search_db, rename, change_config
        import media_mover
        from prompt_toolkit import HTML, print_formatted_text, prompt
        from sys import exit
        main()
    except KeyboardInterrupt:
        print("Exiting")
        exit(0)
