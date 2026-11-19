"""Print speech segments of a VO file (split on pauses) to map script lines -> timestamps.
Usage: python vo_segments.py vo.mp3 [noise_db=-32] [min_pause=0.18]
Tip: first run with min_pause=0.35 to find sentence/paragraph breaks, then 0.18 for phrase-level cues.
"""
import sys, subprocess, re
f = sys.argv[1]; nz = sys.argv[2] if len(sys.argv) > 2 else '-32'; d = sys.argv[3] if len(sys.argv) > 3 else '0.18'
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                           capture_output=True, text=True).stdout)
log = subprocess.run(['ffmpeg', '-i', f, '-af', f'silencedetect=noise={nz}dB:d={d}', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
cur = 0.0; segs = []
for s, e in zip(st, en):
    if s > cur + 0.05: segs.append((cur, s))
    cur = e
if cur < dur - 0.05: segs.append((cur, dur))
print(f'duration {dur:.2f}s, {len(segs)} speech segments')
for i, (a, b) in enumerate(segs): print(f'{i:2d}  {a:6.2f} - {b:6.2f}  ({b - a:4.2f}s)')
