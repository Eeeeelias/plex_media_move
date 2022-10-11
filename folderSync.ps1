param($videoPath, $audioPath, $languageVideo, $languageAudio, $outputPath)

$inputPath1 = Get-ChildItem $videoPath -Filter *.mp4
$inputPath2 = Get-ChildItem $audioPath -Filter *.mp4
$lang1 = $languageVideo
$lang2 = $languageAudio
$out = $outputPath

$len = $inputPath1.Length
Write-Output "[i] Make sure that there are the same number of files (and more than 1 file) in both folders!"
Write-Output "[i] Alphanumeric sorting in windows is bad so do check that it's comparing the correct files!"
Write-Output "[i] Processing $len files"

for ($i = 0; $i -le $inputPath1.length-1; $i++)
{
  py .\src\py_combine_movies.py -g $inputPath1[$i] -b $inputPath2[$i] -p $out -l $lang1 $lang2
}

