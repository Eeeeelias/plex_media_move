import os
from pathlib import Path
from prompt_toolkit import prompt, HTML, print_formatted_text
from prompt_toolkit.completion import PathCompleter

path = "sdf"


while 1:
    try:
        print_formatted_text("TEST")
        print_formatted_text(HTML("<ansired>[w] This is a warning!</ansired>"))
        user_input = prompt(HTML("<ansiblue>Please enter text: </ansiblue>"), completer=PathCompleter())
        us = prompt(HTML("<ansiblue>Please do {} things: </ansiblue>".format(path)))
        path = user_input
        print(user_input)
    except KeyboardInterrupt:
        exit(0)
