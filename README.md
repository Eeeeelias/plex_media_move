# Plex Media Move

These are a few scripts to help with renaming and organizing video files to better work with
Plex (or Jellyfin). So far there are a few scripts, though more may be added in the future.

## media_mover.py

The main script of this repo: it will rename, organize and move your media files into the 
appropriate folders for plex to scan and give back to you. For the script to work you have 
to put in the `origin path` (where your files are currently), the `destination path` (the path
that plex reads from) and optionally some `special values` for some hard to identify shows/seasons.
The `-a` param will look at local Audials files but is more of a legacy feature. Using `-o` will result in
possible duplicate files being overwritten, be careful with this!
```shell
python3 media_mover.py --op "/path/to/files" --dp "/path/to/plex/library" [--sv "IDENTIFIER;SEASON"] [-a] [-o]
```
Alternatively, there is an example batch file ``run_mover.bat`` that you can fit to your needs 
to make it easier to execute and change program arguments if needed.

Your input directory structure should look like this (Assuming you're using Audials):
```
--/videoFiles
----/Audials
------/Audials TV Shows
--------/coolShow s01e01.mp4
------/Audials Movies
----/someShow Episode 1.mp4
----/someShow Season 2 Episode 1.mp4
```
Then you can just point the origin path to `/videoFiles` and the script will handle everything else


## combine_movies.sh / py_combine_movies.py
This script allows you to easily combine two movie files into one with two audio tracks. This is intended 
for combining movies with different languages (e.g. English and German). To use in bash:
```bash
./combine_movies.sh "Movie (YYYY) - English.mp4" "Movie (YYYY) - Deutsch.mp4"
```
Or python:
```shell
python3 py_combine_movies.py -g "Movie (YYYY) - English.mp4" -b "Movie (YYYY) - Deutsch.mp4"
```
There is an optional `-o` parameter that allows you to override the automatic offset. Mind that you have to
specify a number and time fomrat e.g. `400ms`. Also, you can specify an output directory by adding `-p` with 
the directory.


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