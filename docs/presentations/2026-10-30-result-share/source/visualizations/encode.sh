#!/usr/bin/env bash
cd "$(dirname "$0")"; rm -rf anim_out; mkdir anim_out
declare -A SRC=( [slide03]=scenes_a/480p30/Slide03 [slide04]=scenes_b/1200p30/Slide04 [slide06L]=scenes_b/1080p30/Slide06L [slide06R]=scenes_b/1080p30/Slide06R [slide07]=scenes_c/1200p30/Slide07 [slide08]=scenes_c/1200p30/Slide08 [slide09]=scenes_c/480p30/Slide09 [slide10]=scenes_c/1200p30/Slide10 [slide11]=scenes_c/1200p30/Slide11 )
declare -A POS=( [slide03]=6.2 [slide04]=9.9 [slide06L]=3.2 [slide06R]=9.5 [slide07]=7.5 [slide08]=8.0 [slide09]=8.5 [slide10]=99 [slide11]=99 )
for k in "${!SRC[@]}"; do
  f=final/videos/${SRC[$k]}.mp4
  [ -f $f ] || { echo MISSING $f; continue; }
  ffmpeg -v error -y -i $f -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -movflags +faststart -an anim_out/$k.mp4
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 anim_out/$k.mp4)
  t=$(python3 -c "d=float('$d'); t=float('${POS[$k]}'); print(min(t,d-0.4))")
  ffmpeg -v error -y -ss $t -i anim_out/$k.mp4 -frames:v 1 -q:v 3 anim_out/$k.jpg
  echo $k $(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 anim_out/$k.mp4) ${d}s $(du -h anim_out/$k.mp4 | cut -f1) poster@$t
done
