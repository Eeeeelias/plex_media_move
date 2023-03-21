import glob
import os
import re
import shutil
import subprocess
from src.mediainfolib import logger
from prompt_toolkit import HTML, print_formatted_text, prompt


def greetings():
    print_formatted_text(HTML("""
    ############################################################################
    #                                                                          #
    # To synchronize your subtitles make sure they have a <ansigreen>.language.ext</ansigreen> end-   #
    # ing. If you want to synchronize an entire folder, your references must   #
    # be video files (.mkv or .mp4).                                           #
    #                                                                          #
    ############################################################################
    """))


def check_ffs():
    if not shutil.which('asdf'):
        raise RuntimeError


def get_input() -> tuple:
    off = prompt(HTML("<ansiblue>[a] Specify an offset in seconds ([ENTER] to skip): </ansiblue>"))
    if off == "q":
        return 0, 0
    inp = prompt(HTML("<ansiblue>[a] Put in your unsynced subs here (file or folder): </ansiblue>")).strip('"')
    if os.path.isdir(inp):
        return match_folder(inp), off
    ref = prompt(HTML("<ansiblue>[a] Put in your reference: </ansiblue>")).strip('"')
    return [[ref, inp]], off


def match_folder(folder: str) -> list:
    folder = glob.glob(folder + "/*")
    references = [x for x in folder if x[-4:] == '.mp4' or x[-4:] == '.mkv']
    subs = [x for x in folder if x[-4:] == '.ass' or x[-4:] == '.srt']

    matches = []
    for ref in references:
        name = os.path.splitext(os.path.basename(ref))[0]
        tmp = [ref, [x for x in subs if name == re.sub(r"(\.[\w]{2,3}\.(srt|ass)$)", "", os.path.basename(x))][0]]
        # the regex removes the language and file ending
        matches.append(tmp)
    return matches


def subsync_exec(to_sync: str, reference: str, offset: str):
    sync = ['ffsubsync', reference, "-i", to_sync, "-o"]
    lang = re.search(r"\.([^.]*?)\.[^.]*$", to_sync)
    try:
        lang = lang.group(1)
    except AttributeError:
        print_formatted_text(HTML("<ansired>[w] Subtitles not properly named! Exiting.</ansired>"))
        return
    original_ext = os.path.splitext(to_sync)[1]
    ref_path = os.path.splitext(reference)[0]
    output = ref_path + "_sync." + lang + original_ext
    sync.append(output)
    if offset != "0":
        sync.extend(["--apply-offset-seconds", offset])
    logger.debug("[subsync] Synchronizing subtitles: " + " ".join(sync))
    subprocess.run(sync)


def main():
    try:
        check_ffs()
    except RuntimeError:
        print_formatted_text(HTML("<ansired>[w] ffsubsync not found! Make sure it's on PATH</ansired>"))
        return
    greetings()
    offset = "0"
    inputs = get_input()
    if inputs[0] == 0:
        return
    if inputs[1] != "":
        print("inp:", inputs[1])
        offset = inputs[1]
    for i in inputs[0]:
        inp = i[1]
        ref = i[0]
        subsync_exec(inp, ref, offset)
    return


if __name__ == '__main__':
    main()
