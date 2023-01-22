from prompt_toolkit import print_formatted_text, HTML
import src.db_infos as di
from src.mediainfolib import cut_name


def all_stats(db: str) -> None:
    gs = "<ansigreen>"
    ge = "</ansigreen>"
    print_formatted_text(HTML(f"""
    ############################################################################
    #                                                                          #
    # {gs}[1]{ge} {call_function(db, di.media_size)}#
    # {gs}[2]{ge} {call_function(db, di.num_videos)}#
    # {gs}[3]{ge} {call_function(db, di.total_watchtime)}#
    # {gs}[4]{ge} {call_function(db, di.database_size)}#
    # {gs}[5]{ge} {call_function(db, di.oldest_movie)}#
    # {gs}[6]{ge} {call_function(db, di.best_quality)}#
    # {gs}[7]{ge} {call_function(db, di.worst_quality).replace("&", "&amp;")}#
    #                                                                          #
    ############################################################################
    """))
    return


# regret sets in
def call_function(db, funct):
    line_length = cut_name(funct(db)[5:], 69)
    empty_space = ' ' * (69 - len(line_length))
    return line_length + empty_space
