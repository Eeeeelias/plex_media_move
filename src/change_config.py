from src.mediainfolib import get_config, config_path, clear
from prompt_toolkit import prompt, print_formatted_text, HTML
from src import setup


def greetings():
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #                                                                          #
    # Select the config option you want to change:                             #
    #                                                                          #
    # [1] {gs}media mover{ge}                                                          #
    # [2] {gs}combiner{ge}                                                             #
    # [3] {gs}database{ge}                                                             #
    #                                                                          #
    ############################################################################


    """))


def default_window(curr_config):
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    window = "    ############################################################################\n" \
             "    #                                                                          #\n" \
             "    # Your current config:                                                     #\n"
    for key, value in curr_config.items():
        if type(value) == bool:
            value = "False" if value == 0 else "True"
        window += f"    # {gs}{key:11}{ge} - {value:58} #\n"
    window += "    #                                                                          #\n" \
              "    ############################################################################\n"
    print_formatted_text(HTML(window))


def change_value(config, program):
    default_window(config[program])
    change = prompt(HTML("<ansiblue>Option you want to change: </ansiblue>"))
    if change == "q":
        return config
    while change not in config[program].keys():
        print_formatted_text(HTML("<ansired>[w] Not a valid option!</ansired>"))
        change = prompt(HTML("<ansiblue>Option you want to change: </ansiblue>"))
    print(f"[i] Changing {change}")
    value = prompt(HTML("<ansiblue>New value: </ansiblue>"))
    if value.lower() in ["true", "false"]:
        value = True if value.lower() == "true" else False
    config[program][change] = value
    return config


def main():
    config = get_config()
    new_config = config
    while 1:
        greetings()
        choice = prompt(HTML("<ansiblue>Your choice: </ansiblue>"))
        if choice in ["1", "media mover", "mover"]:
            new_config = change_value(config, 'mover')
        elif choice in ["2", "combiner"]:
            new_config = change_value(config, 'combiner')
        elif choice in ["3", "database", "db"]:
            new_config = change_value(config, 'database')
        elif choice in ["q", "quit", "exit"]:
            return
        setup.write_config_to_file(new_config, config_path)
        clear()
        print("[i] Changed config!")
