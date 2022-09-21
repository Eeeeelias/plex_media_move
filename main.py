import convert_ts
import media_mover
import py_combine_movies
import rename
import search_db
import setup
import os
from mediainfolib import get_config, clear
from prompt_toolkit import HTML, print_formatted_text, prompt


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
    # [2] {gs}combiner{ge}    - let's you combine two movies in different languages    #
    #                   so you have one movie with two languages.              #
    #                                                                          #
    # [3] {gs}shifting{ge}    - shift all episode numbers of a show by a given         #
    #                   amount                                                 #
    #                                                                          #
    # [4] {gs}converter{ge}   - convert folders of weird formats (like .ts) into .mp4  #
    #                                                                          #
    # [5] {gs}db search{ge}   - search through your local media database               #
    #                                                                          #
    # [i] Using this tool will use your default settings!                      #
    #                                                                          #
    ############################################################################
    
    
    """))


def check_for_setup():
    if get_config() is None:
        print("[i] No config found! Running setup...")
        setup.set_config()


def main():
    while 1:
        greetings()
        tool = prompt(HTML("<ansiblue>Your choice: </ansiblue>"))
        if tool == "1" or tool == "media mover":
            media_mover.main()
        elif tool == "2" or tool == "combiner":
            clear()
            py_combine_movies.main()
        elif tool == "3" or tool == "shifting":
            clear()
            rename.main()
        elif tool == "4" or tool == "converter":
            clear()
            convert_ts.main()
        elif tool == "5" or tool == "db search":
            clear()
            search_db.main()
        elif tool == "clear":
            clear()
        elif tool == "close" or tool == "q" or tool == "quit":
            exit(0)
        else:
            clear()


if __name__ == '__main__':
    try:
        check_for_setup()
        main()
    except KeyboardInterrupt:
        print("Exiting")
        exit(0)
