import csv
import os

name_list = []
shows_list = [x for x in os.listdir("P:\\Plex Shows\\TV Shows")]

with open("show_infos.csv", 'r') as csvfile:
    show_infos = csv.reader(csvfile)
    for lines in show_infos:
        name_list.append(lines[1])

for i in shows_list:
    if i not in name_list:
        print(f"{i} not in your list!")
