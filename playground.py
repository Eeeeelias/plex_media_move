import csv
import os


def completeness_check(path):
    name_list = []
    shows_list = [x for x in os.listdir(path)]

    with open("show_infos.csv", 'r') as csvfile:
        show_infos = csv.reader(csvfile)
        for lines in show_infos:
            name_list.append(lines[1])

    for i in shows_list:
        if i not in name_list:
            print(f"{i} not in your list!")


def sum_files(file_list):
    sum = 0
    for file in file_list:
        sum += file['show_size']
    return sum