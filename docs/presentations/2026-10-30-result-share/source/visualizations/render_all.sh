#!/usr/bin/env bash
cd "$(dirname "$0")"
M="/home/light/anaconda3/bin/python -m manim render --fps 30 --media_dir final"
job(){ ASPECT=$1 $M -r $2 $3 $4 > final/log_$4.txt 2>&1; echo "done $4"; }
job 5.0    2400,480  scenes_a.py Slide03 &
job 1.55   1860,1200 scenes_b.py Slide04 &
job 1.6667 1800,1080 scenes_b.py Slide06L &
job 1.6667 1800,1080 scenes_b.py Slide06R &
wait
job 1.55   1860,1200 scenes_c.py Slide07 &
job 1.55   1860,1200 scenes_c.py Slide08 &
job 5.0    2400,480  scenes_c.py Slide09 &
job 1.55   1860,1200 scenes_c.py Slide10 &
wait
job 1.55   1860,1200 scenes_c.py Slide11
echo ALLDONE
