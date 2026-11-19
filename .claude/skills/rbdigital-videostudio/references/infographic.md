# 9. Infografik data (recipe — not yet tested)

Look: clean flat design, big animated numbers counting up, bar/line/pie charts that grow, icons popping in, comparison blocks, source line at the bottom; consistent 2–3 colour palette on light or dark background.
Best for: statistics, cost comparisons, plan comparisons (e.g. takaful coverage vs bills), survey results, "berapa kos...".

## Flow prompts
Icons only — ONE 4x4 sheet: `A sheet of 16 separate flat vector icons in a 4x4 grid with wide space between, <palette> flat design, simple shapes, no text, plain solid dark grey background. Row 1: ...`. Charts, numbers, labels are drawn in code (never ask Flow for charts).

## Build (common.py)
- Numbers: count-up with ease_out over 0.8–1.2 s, formatted (`RM 12,500`, `68%`), Anton/Oswald, huge.
- Bar chart: bars grow from baseline with staggered ease_back; value labels count up; highlight the key bar with accent colour + pulse.
- Pie/donut: PIL `pieslice`/arc with growing end angle; percentage in centre.
- Line chart: polyline revealed by increasing point count + moving dot.
- Icons from sheet via `cut_sheet.py`; pop in beside stats.
- Always show "Sumber: ..." small at bottom if real data; only use numbers the user gives or well-established facts (search if needed), hedge estimates.
- Audio: `lofi`/`cheerful` 0.3, tick sound during count-up (word_pop repeated), ding at final value.
