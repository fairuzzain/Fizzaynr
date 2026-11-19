Tested example (52 s). Working dir needs: assets/ (from cut_sheet.py), bg_blue.jpg, bg_note.jpg, vo.mp3.
`python shark_storyboard.py preview` then `python shark_storyboard.py` (engine renders + mixes audio in one go;
if it risks the 300 s limit, render with common.render_chunk(scrapbook_engine.compose, a, b) instead).
