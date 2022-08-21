#!/bin/bash


help () {
  printf "================================================================================\n"
  printf "+              <Plex Media Move> - https://github.com/Eeeeelias                +\n"
  printf "================================================================================\n"
  printf "| Usage ./combine_movies.sh input1 input2 [offset]                             |\n"
  printf "|                                                                              |\n"
  printf "| Variables:                                                                   |\n"
  printf "|     input1: English version of the movie e.g.                                |\n"
  printf "|         \"Movie Title (2020) - English.mp4\"                                   |\n"
  printf "|     input2: German version - in the same format as input1                    |\n"
  printf "|     offset: manual offset of the audio files in case the                     |\n"
  printf "|         automatic offset doesn't work. e.g. 500ms                            |\n"
  printf "| Example:                                                                     |\n"
  printf "| ./combine_movies.sh \"300 (2006) - Eng.mp4\" \"300 (2006) - Deu.mp4\" 500ms      |\n"
  printf "|                                                                              |\n"
  printf "| Thanks a lot for using this beginner script!                                 |\n"
  printf "================================================================================\n"
}

input1=$1
input2=$2
offset=$3

if [ $# -eq 0 ]
  then
    help
    exit 0
fi

dur_en=`ffmpeg -i "$input1" 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | awk '{ split($1, A, ":"); print 3600000*A[1] + 60000*A[2] + 1000*A[3] }'`
dur_de=`ffmpeg -i "$input2" 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | awk '{ split($1, A, ":"); print 3600000*A[1] + 60000*A[2] + 1000*A[3] }'`
diff=$(($dur_en-$dur_de))

if [ -z "$3" ]
  then
    echo "[i] No offset given, using time diff"
    offset="${diff}ms"
fi
combined_name=$(echo ${input1##*/} | perl -pe "s/(?<=\(\d{4}\)).*//g")

if [ ! -d "$PWD/Movies" ]
  then
    echo "[i] \"Movies/\" folder does not exist. Making folder"
    mkdir "$PWD/Movies"
fi

echo "[i] English verion: $input1, video length: $dur_en ms"
echo "[i] German version: $input2, video length: $dur_de ms"
echo "[i] File will be written to: $combined_name"
echo "[i] Time difference: $diff ms, offsetting by: $offset"


sleep 3s


ffmpeg -loglevel warning -i "$input1" -itsoffset $offset -i "$input2" -map 0:0 -map 0:a -map 1:a -metadata:s:a:0 language=en -metadata:s:a:1 language=de -c copy "$PWD/Movies/${combined_name}.mkv"
