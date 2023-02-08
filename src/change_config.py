from src.mediainfolib import get_config, config_path, clear, write_config_to_file
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
    # [4] {gs}viewer{ge}                                                               #
    #                                                                          #
    ############################################################################


    """))


def default_window(curr_config):
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    window = \
        "\n    ############################################################################\n" \
        "    #                                                                          #\n" \
        "    # Your current config:                                                     #\n"
    for key, value in curr_config.items():
        if type(value) == bool:
            value = "False" if not value else "True"
        if value is None:
            value = "None"
        value = value.replace("&", "&amp;")
        window += f"    # {gs}{key:12}{ge} - {value:57} #\n"
    window += \
        "    #                                                                          #\n" \
        "    ############################################################################\n"
    print_formatted_text(HTML(window))


def ensure_bool(curr, change):
    if type(curr) != bool:
        return True
    else:
        if change.lower() in ["true", "false"]:
            return True
    return False


def change_value(config, program):
    default_window(config[program])
    change = prompt(HTML("<ansiblue>Option you want to change: </ansiblue>")).lstrip('"').rstrip('"')
    if change == "q":
        return config, False
    while change not in config[program].keys():
        print_formatted_text(HTML("<ansired>[w] Not a valid option!</ansired>"))
        change = prompt(HTML("<ansiblue>Option you want to change: </ansiblue>")).lstrip('"').rstrip('"')
        if change == "q":
            return config, False
    print(f"[i] Changing {change}")
    value = prompt(HTML("<ansiblue>New value: </ansiblue>"))
    while not ensure_bool(config[program][change], value):
        print_formatted_text(HTML("<ansired>[w] Not a valid input! Must be True or False.</ansired>"))
        value = prompt(HTML("<ansiblue>New value: </ansiblue>")).lstrip('"').rstrip('"')
    if value.lower() in ["true", "false"]:
        value = True if value.lower() == "true" else False
    config[program][change] = value
    return config, True


# this is stupid, use add_to_config()
def default_configs(config: dict):
    config['mover'].pop('filetypes')
    config.update({'viewer': {'default_view': config['mover']['orig_path'], 'filetypes': '.mkv .mp4 .ts'}})
    write_config_to_file(config, config_path)


def add_to_config(options: dict, append=False):
    from src.mediainfolib import get_config
    curr_conf = get_config()
    for opt, vals in options.items():
        if not append:
            curr_conf.update({opt: vals})
        else:
            curr_val = curr_conf.get(opt)
            curr_val.update(vals)
            curr_conf.update({opt: curr_val})
    write_config_to_file(curr_conf, config_path)
    return True


def main():
    config = get_config()
    new_config = config
    changed = False
    while 1:
        greetings()
        choice = prompt(HTML("<ansiblue>=> </ansiblue>"))
        if choice in ["1", "media mover", "mover"]:
            new_config, changed = change_value(config, 'mover')
        elif choice in ["2", "combiner"]:
            new_config, changed = change_value(config, 'combiner')
        elif choice in ["3", "database", "db"]:
            new_config, changed = change_value(config, 'database')
        elif choice in ["4", "viewer"]:
            new_config, changed = change_value(config, 'viewer')
        elif choice in ["q", "quit", "exit"]:
            clear()
            return
        write_config_to_file(new_config, config_path)
        clear()
        if changed:
            print("[i] Changed config!")
