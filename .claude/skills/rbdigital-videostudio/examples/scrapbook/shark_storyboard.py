"""Example storyboard: '5 Fakta Ikan Jerung' (52s, synced to VO pauses).
Run from a working dir that contains assets/ (cut stickers) and the backgrounds.
  python shark_storyboard.py preview   -> grid.jpg
  python shark_storyboard.py           -> fakta_jerung.mp4
"""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))  # this skill's scripts/
from scrapbook_engine import *

setup('assets', {'blue': 'bg_blue.jpg', 'note': 'bg_note.jpg'})

# S1 hook
scene(0, 6.5, 'blue')
el(sprite('A1', 470), 300, 1050, 0.2, 6.5, rot=-6)
caption(['JERUNG', 'LEBIH', 'TUA'], 360, 1.2, 6.5, 110, NAVY)
el(sprite('D1', 260), 560, 760, 2.3, 6.5, rot=-10)
el(sprite('A2', 380), 800, 1000, 2.7, 6.5, rot=5)
caption(['DARI', 'POKOK?!'], 1450, 2.8, 6.5, 140, RED, rot=-3)
el(sprite('D2', 220), 860, 640, 5.2, 6.5, rot=12, anim='slam')

# S2 fakta 1
scene(6.5, 12.8, 'note')
caption(['FAKTA', '#1'], 330, 6.75, 12.8, 90, RED, rot=-4)
el(sprite('A3', 500), 540, 930, 7.6, 12.8, rot=-4)
el(sprite('D3', 340), 540, 700, 8.0, 12.8, rot=8, anim='slam')
caption(['400', 'JUTA', 'TAHUN'], 1320, 8.4, 12.8, 120, NAVY)
caption(['lebih', 'awal', 'dari', 'pokok', 'pertama'], 1580, 10.15, 12.8, 70, NAVY, step=0.2)

# S3 fakta 2
scene(12.8, 21.9, 'blue')
caption(['FAKTA', '#2'], 330, 13.0, 21.9, 90, RED, rot=-4)
el(sprite('A4', 420), 540, 870, 14.5, 21.9, rot=-18)
caption(['TAKDE', 'TULANG!'], 510, 15.5, 21.9, 120, NAVY)
el(sprite('D4', 360), 540, 870, 15.9, 21.9, rot=4, anim='slam')
caption(['rawan', 'je,', 'macam', 'hidung', '&', 'telinga', 'kita'], 1500, 17.1, 21.9, 72, NAVY, step=0.45)
el(sprite('A5', 420), 540, 1240, 19.3, 21.9, rot=3)

# S4 fakta 3
scene(21.9, 27.65, 'note')
caption(['FAKTA', '#3'], 330, 22.1, 27.65, 90, RED, rot=-4)
for i in range(22):
    el(sprite('A6', random.randint(130, 210)), random.randint(120, 960), random.randint(560, 1200),
       23.0 + i * 0.13, 27.65, rot=random.uniform(-40, 40), anim='fall')
caption(['PULUHAN', 'RIBU', 'GIGI'], 1330, 25.2, 27.65, 110, NAVY)
caption(['tumbuh', 'ganti', 'seumur', 'hidup'], 1570, 23.4, 27.65, 72, RED, step=0.2)

# S5 fakta 4
scene(27.65, 38.1, 'blue')
caption(['FAKTA', '#4'], 330, 27.85, 38.1, 90, RED, rot=-4)
el(sprite('A7', 560), 540, 800, 29.3, 38.1, rot=-3)
caption(['Jerung', 'Greenland'], 1400, 29.5, 38.1, 80, NAVY, step=0.3)
caption(['HAMPIR', '400', 'TAHUN!'], 1540, 31.2, 38.1, 105, RED, step=0.35)
el(sprite('A8', 330), 330, 1180, 33.4, 38.1, rot=-8)
el(sprite('A9', 230), 800, 1170, 34.3, 38.1, rot=10)

# S6 fakta 5
scene(38.1, 46.3, 'note')
caption(['SETIAP', 'TAHUN...'], 300, 39.3, 46.3, 90, RED, rot=-3)
el(sprite('A10', 340), 280, 620, 39.9, 46.3, rot=-6)
el(text_sprite('MANUSIA bunuh', 58, NAVY), 700, 560, 40.3, 46.3, anim='word')
el(text_sprite('±100 JUTA', 100, RED), 700, 680, 41.2, 46.3, rot=-4, anim='slam')
el(text_sprite('jerung', 58, NAVY), 700, 790, 41.9, 46.3, anim='word')
el(sprite('D5', 700), 540, 990, 42.4, 46.3, rot=-2)
el(text_sprite('VS', 110, RED), 540, 990, 42.6, 46.3, rot=-5, anim='slam')
el(sprite('A1', 360), 300, 1300, 42.8, 46.3, rot=6)
el(text_sprite('JERUNG bunuh', 58, NAVY), 710, 1220, 43.0, 46.3, anim='word')
el(text_sprite('±10', 120, RED), 710, 1340, 44.9, 46.3, rot=4, anim='slam')
el(text_sprite('manusia', 58, NAVY), 710, 1460, 45.4, 46.3, anim='word')

# S7 outro
scene(46.3, 52.0, 'blue')
caption(['SIAPA', 'SEBENARNYA', 'YANG', 'BAHAYA?'], 380, 46.5, 52.0, 100, NAVY, step=0.4)
el(sprite('A11', 520), 540, 1100, 47.9, 52.0, rot=-4)
caption(['FOLLOW', 'untuk', 'fakta', 'lagi!'], 1620, 49.3, 52.0, 100, RED, step=0.25, rot=-2)
el(sprite('D1', 240), 830, 1400, 49.9, 52.0, rot=40)

DUR = 52.0

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview([6, 12, 21.5, 27, 37, 45.9, 51.5])
    else:
        run('fakta_jerung.mp4', DUR, vo='vo.mp3')
