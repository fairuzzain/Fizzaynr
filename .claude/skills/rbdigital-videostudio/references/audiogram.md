# 25. Podcast audiogram (recipe — not yet tested)

**Look:** Host portrait/illustration in a rounded frame, animated waveform/bars reacting to the VO amplitude, big captions (2–4 words at a time, current word highlighted), episode title, progress bar.

**Best for:** Potong klip podcast/VO panjang, quote motivasi, tips suara, repurpose content.

## Flow prompts
Optional portrait: `A single illustrated portrait of <host description>, <style>, plain background, no text, square 1:1` (or the user uploads their photo).
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Compute VO RMS per frame (numpy on vo.wav, 1/24 s windows) → bar heights (smoothed). Captions from phrase timing split by word length; highlight current word with accent colour pill. Layout: title top y 300, portrait y 500–1000, waveform y 1100, captions y 1300–1550, progress bar y 1700.

## Audio (Mix)
Only the VO (maybe very low lofi 0.12).
