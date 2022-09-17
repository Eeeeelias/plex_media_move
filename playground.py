import csv
import glob
import os
from pathlib import Path
import manage_db

def sum_files(file_list):
    sum = 0
    for file in file_list:
        sum += file['show_size']
    return sum

db_path = os.getenv('LOCALAPPDATA') + "\\pmm\\media_database.db"

manage_db.get_item(4, db_path)
