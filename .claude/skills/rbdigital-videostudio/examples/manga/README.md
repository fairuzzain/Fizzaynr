Tested example (40 s). Working dir needs: P1.png..P8.png (cropped panels), Bangers-Regular.ttf, ComicNeue-Bold.ttf
(get via common.get_font('bangers'/'comicneue') and copy/rename), vo.mp3 → vo.wav.
Render: `python manga.py 6 12 17` = preview grid; full render in chunks (write a chunk.py calling compose over frame ranges,
or use common.render_chunk(manga.compose, a, b)); audio: `python audio.py` (edit EVENTS/times), then concat_and_mux.
P2 fix: the original panel had AI text in a bubble — painted out with a white ellipse before adding our bubble.
