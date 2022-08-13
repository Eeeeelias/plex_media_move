# Plex Media Move

These are a few scripts to help with renaming and organizing video files to better work with
Plex (or Jellyfin). So far there are 3 scripts, though more may be added in the future.

## media_mover.py

The main script of this repo: it will rename, organize and move your media files into the 
appropriate folders for plex to scan and give back to you. For the script to work you have 
to put in the `origin path` (where your files are currently), the `destination path` (the path
that plex reads from) and optionally some `special values` for some hard to identify shows/seasons.
```shell
python3 media_mover.py --op "/path/to/files" --dp "/path/to/plex/library" [--sv "IDENTIFIER;SEASON"]
```
Alternatively, there is an example batch file ``run_mover.bat`` that you can fit to your needs 
to make it easier to execute and change program arguments if needed.

## rename.py

A really small script to strip a leading "Watch" and tailing characters after the episode 
numbering. E.g. Turns ``Watch Parks and Recreation s01e02 720p WEB.mp4`` into 
`Parks and Recreation s01e02.mp4`. To use this script just execute it with the folder with your 
video files.
```shell
python3 rename.py "P:\<downloaded>\<files>\<folder>\"
```

## organize_shows.py

This is a script to better organize your already existing media files for TV Shows. Turns 
this folder structure:
```
--/TV Shows
----/Parks and Recreation
------/Parks and Recreation s01e01.mp4
------/Parks and Recreation s01e02.mp4
------/Parks and Recreation s02e04.mp4
------/Parks and Recreation s02e05.mp4
----/The Office
------/The Office s01e01.mp4
------/The Office s02e01.mp4
------/The Office s02e02.mp4
```
Into this (better) structure:
```
--/TV Shows
----/Parks and Recreation
------/Season 1
--------/Parks and Recreation s01e01.mp4
--------/Parks and Recreation s01e02.mp4
------/Season 2
--------/Parks and Recreation s02e04.mp4
--------/Parks and Recreation s02e05.mp4
----/The Office
------/Season 1
--------/The Office s01e01.mp4
------/Season 2
--------/The Office s02e01.mp4
--------/The Office s02e02.mp4
```
It will also inform you about shows that do not follow either of those structures. For those
you will probably have to put in some manual effort.