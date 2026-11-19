# Common pipeline (all styles)

## Paths
Skill scripts: `<skill>` = the folder that contains this skill's SKILL.md. If you don't know it: `dirname "$(dirname "$(find / -path '*rbdigital-videostudio/scripts/common.py' 2>/dev/null | head -1)")"`. Scripts live in `<skill>/scripts`.
Work in a project folder inside the working directory (or scratchpad). Final MP4 → `/mnt/user-data/outputs/<name>.mp4` if that folder exists (claude.ai), otherwise the working directory; then deliver it with whichever file tool the session has (`SendUserFile` or `present_files`).

## Format
9:16, 1080x1920, 24 fps, 35–55 s. Keep text inside x 90–990; top ~250 px and bottom ~250 px are covered by TikTok UI on phones, so key text sits between y 250–1700 (bottom captions ≈ y 1600–1780 is OK but keep short).

## Google Flow prompt rules (the user generates, uploads back)
- **Combine assets into sheets** — Keep the number of prompts low. Stickers/icons: 4x4 grid sheet (≤16 items). Scene images/panels/photos: 2x2 grid per sheet (4 images, more resolution each), 2 sheets for 8 scenes.
- Always write: `exactly N separate items/panels in a WxH grid, thin white gutters (or wide empty space), nothing overlapping, no text, no labels, no speech bubbles, no borders` — Claude renders ALL text (AI text is garbage; it happened: "HAPY, OUR OFFER").
- One shared style line at the end of every prompt so sheets match; describe recurring characters identically in each prompt (name + hair + clothes) and tell the user to use sheet 1 as **ingredient** for sheet 2.
- Backgrounds: separate prompt each, `Vertical 9:16 …, empty center, no text`.
- Sticker sheets: ask for `plain solid dark grey background` (easiest to cut). Flow sometimes bakes a fake transparency checkerboard anyway — `cut_sheet.py` handles it.
- Things AI can't draw reliably (text on paper, UI, numbers, charts, chat bubbles) → leave blank in the image, render them yourself.

## VO (ElevenLabs v3)
One code block, one short paragraph per scene, audio tags in brackets: `[excited] [curious] [surprised] [playful] [amazed] [laughs] [nervous laugh] [serious] [sad] [thoughtful] [cheerful] [calm] [whispers] [scared] [trembling] [gasps] [sighs] [crying] [dramatic] [shocked] [confident] [pause]`. Tell them: use model **Eleven v3** (others read tags aloud), a Malay-capable voice; for horror lower stability. Malay pace ≈ 2.3 words/s; aim 90–120 words for 45 s. Keep claims factual; hedge numbers ("lebih kurang", "±").

## Identify uploads
Sheets are square (1:1), backgrounds 9:16, VO is mp3. Tell pages/sheets apart by content (view them) — upload order is random. Check mean colour to tell backgrounds apart.

## Cutting assets
- Sticker sheet → `python <skill>/scripts/cut_sheet.py sheet.png assets --names A1,...` then view `assets/_check.png`.
- 2x2 grids of photos/panels → find white gutters: rows/cols where `(gray>235).mean() > 0.9` (see examples). Crop 4 px inside the gutters. Manga pages: gutter threshold 0.97, keep the black border.
- AI garbage text inside an image → paint it out with a fill of the local background colour, then draw your own element on top (see examples/manga P2 fix).

## VO timing
`python <skill>/scripts/vo_segments.py vo.mp3 -32 0.35` (paragraph breaks) then `-32 0.18` (phrase cues). Map script lines to segments by order and duration. Scene cuts go in the pauses; each visual event is timed to the word that mentions it (number spoken → number slams in). Video length = VO + 1–2 s outro. Tell the user timing came from pauses, not a transcript.

## Rendering (sandbox limits!)
1 CPU core and 300 s per tool call. Measure `frame_time(compose)` first; frames per chunk ≈ 250 / frame_time. Render with `render_chunk(compose, a, b)` across several tool calls, then `concat_and_mux`. Never start background jobs (`nohup … &` gets killed). Target < 0.15 s/frame: cache sprites/text, precompose static layers, avoid rotating huge layers every frame, render at 24 fps.

Always preview first with `contact_sheet(compose, [times])` and **view** it — check overlaps, text cut-offs, elements off-screen, camera beyond the background edge (clamp camera to the world bounds).

## Audio (`Mix` in common.py)
No network for stock music → synthesize. Under VO: music gain 0.3–0.35, SFX ~0.6×. Mute music during dramatic beats (`mute=[(t0,t1)]`) and use `drone` for tension. If the user uploads their own music, mix that instead (ffmpeg amix or load into Mix via vo()-style decode with lower gain).

**Every video must get its own track.** `m.music(style, gain, seed=...)` is a seeded generator: key, BPM, chord progression, arp pattern, instruments (pluck/marimba/bell/epiano/square/saw/flute/koto), bass style and drum groove are all picked from the seed, and the track has sections (intro without drums, main, contrast section without lead).
- Use the video title as seed (`seed="Tajuk video"`) so a re-render of the same video keeps the same song; a new video = new title = new song. Never copy a fixed seed or a hardcoded chord list from an earlier script/example.
- If the user says "tukar lagu", change the seed (e.g. `seed="Tajuk video v2"`) or override: `bpm=`, `key='D'`, `mode='min'`, `arp='marimba'`, `lead=None`, `drums='lofi'`.
- The call prints `[music] style=… key=… bpm=… arp=…` — mention it in one line of the summary.

Mood → style: facts/scrapbook `cheerful`, skits/meme `comedy`, study/tips `lofi`, horror/mystery `tense` (+ `drone`), trailer/hype/countdown `epic`, storybook/testimonial/kisah sedih `emotional`, product ad/UGC `funky` or `cheerful`, pixel/game/Win95 `retro8bit`, wayang kulit/batik/ukiyo-e/sejarah Melayu `traditional`. When two fit, alternate between them across videos.

## Fonts (`get_font`)
bangers (comic SFX), comicneue (bubbles), marker (handwritten notes), typewriter (horror/news captions), anton/bebas/oswald (bold kinetic/countdown/news), caveat (casual handwriting), poppins (local, clean UI/labels).

## Reply after render
Short rojak summary: what's in the video (3–5 bullets), then "kalau ada timing lari, bagitahu saat berapa".
