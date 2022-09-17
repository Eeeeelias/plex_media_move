import csv
import glob
import os

def sum_files(file_list):
    sum = 0
    for file in file_list:
        sum += file['show_size']
    return sum


if __name__ == '__main__':
    sum_files(glob.glob("P:\\script_testing\\TV Shows\\*.mp4"))
