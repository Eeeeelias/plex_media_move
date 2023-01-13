## Introduction
PMM or Plex Media Move is a little command line tool that helps you organise, sort, rename, move your media files so your favourite Media Server (not just Plex!) has an easy time picking everything up. PMM also offers some basic video editing possibilities as well as converting different files. It's designed to require very little effort and work do most things automatically. 

## Prerequisites
In order for PMM to work, you need the following programs/packages:

- FFMPEG - it can be found here: [Link](https://ffmpeg.org/).
- prompt_toolkit (only when cloning from git)
- pycountry (only when cloning from git)
- opencv-python (only when cloning from git)

The latter three should be installed automatically but you might need to restart PMM in order to get it working properly.
If this does not work even after restarting, please install the packages manually using this command:
```python
python3 -m pip install pycountry prompt_toolkit opencv-python 
```

## Setup

When you start up the program for the first time you are able to set default file paths and such. While you can skip this, it is highly recommended to do it since most parts of PMM will not work without it. The values you need to put in there are described here:

| Value              | Description                                                                                                                                                                                                                                                                                      |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| unsorted media     | Usually the folder where all the media files land when you initially download them. Note that all subfolders are also being considered!                                                                                                                                                          |
| sorted media       | The folder where your media is supposed go. Note that this folder should not be specific to TV Shows or Movies as PMM will make those folders automatically if they're not found.                                                                                                                |
| overwrite existing | Tell PMM to overwrite files if a file with a duplicate has been found. If say no PMM will ask each time.                                                                                                                                                                                         |
| special values     | If some show has a season that can not be read from the file name, you can specify that here. e.g. your file is called `Attack on Titan Last Season Episode 4.mp4`, then you could put in `Titan;4` and PMM will consider that. **This is mostly redundant when the newer file viewer is used.** |
| combined movies    | When combining/editing movies, the default output path can be specified here. Giving the same path as unsorted media makes sense here                                                                                                                                                            |
| ask regardles      | You can tell PMM to ask for the output path each time if you prefer that                                                                                                                                                                                                                         |
| database path      | PMM makes use of a database. You can specify where that database should be stored. If you give no value, the default path will be used                                                                                                                                                           |
| filetypes          | Specify the filetypes the viewer should consider. These need to be space separated so it could look something like this: `.mp4 .mkv .ts .webm`                                                                                                                                                   |


After that, PMM will ask to order your sorted media folder. It will try to put files into proper folders following the naming scheme that most Media Servers like [Plex](https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/) or [Jellyfin](https://jellyfin.org/docs/general/server/media/shows/) use. It will also show you which folders it left out due to poorly named files or other problems.

When that is done, PMM will ask you if you want to create a database. Depending on the size of your existing media library, this  can take a while.

## First start

When you first open PMM you will see on the left all the different functions of PMM and on the right a preview of what files are currently in your unsorted media folder as well as how many there are and in how many folders. From there you can choose what you want to do by either inputting the number of the corresponding function or inputting it's name directly. So if you want to open the file viewer you can put in `6` `[ENTER]`. If you put in `c` you can change the config you set up in the setup and with the keyword `log` you can see the logs media_mover created.

Wherever you are in the program, whenever you input `q` you will return to  the previous screen. To quit out of the program, either use `q` or `exit` in the main view. Alternatively you can just use `Ctrl+C`, which also works.

## Shortcuts for all functionalities 

Each submenu is reachable via different inputs. Here's a list of each submenu and the possible inputs to get there. These can be found and edited in `main.py`.

| menu        | possible inputs      |
|-------------|----------------------|
| media mover | `1`, `mm`            |
| video edits | `2`, `combine`, `ve` |
| shifting    | `3`, `sf`            |
| converter   | `4`, `cv`            |
| database    | `5`, `db`            |
| file view   | `6`, `fw`            |
| configs     | `c`                  |
| logs        | `log`                |
