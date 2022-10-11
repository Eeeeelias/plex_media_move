# Plex Media Move

This is a small program to help with renaming and organizing video files to better work with
Plex (or Jellyfin).

## Execute

Execute `main.py` like so:
```shell
python3 main.py
```
This will start a setup for you to get started. After that you're able to move your files, edit videos,
edit Episode numbering, convert videos or look up shows in your database.

For the media mover to work properly, your input directory structure should look like this 
(Assuming you're using Audials):
```
--/videoFiles
----/Audials
------/Audials TV Shows
--------/coolShow s01e01.mp4
------/Audials Movies
----/someShow Episode 1.mp4
----/someShow Season 2 Episode 1.mp4
```
Then you can just point the origin path to `/videoFiles` and the mover will handle everything else.

## Requirements

The program should install all the needed requirements automatically, but if that fails make sure to have
`pycountry`, `opencv-python` and `prompt_toolkit` installed.


## src/organize_shows.py

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