# Fizzaynr: Reel Studio × Atlas spot

A 75.5 s, 1920×1080, 24 fps spot whose edit runs on the reference ad's cut grid
(instagram.com/p/Dd66aLqCbO6). Every cut and timed beat sits on the same absolute frame as the reference.
The story, copy, UI designs, brand and character are original:

- a neutral placeholder brand: the **Reel Studio** extension inside the **Atlas** assistant
- **Theo**, an original character, in an original studio location
- interfaces designed from scratch: the chat app, file browser, editor, export panel and pink desktop

Brand names, colours and copy all live in `timeline/brand.json`.

## Layout

| Path | What it is |
|---|---|
| `timeline/timeline.json` | **The editable timeline.** 24 shots with absolute in/out frames, camera keyframes, cursor paths and clicks, typing ranges, captions and the reference beat for each slot. |
| `timeline/brand.json` | Names, copy and colours. `{{key}}` placeholders in the timeline resolve from here. |
| `src/` | Deterministic HTML renderer. `window.seek(frame)` draws one exact frame. `scenes.js` holds the UI scenes; `plates.js` draws the stand-in footage shown inside the UI. |
| `scripts/render.mjs` | Headless Chromium → ffmpeg. Writes `out/ui.mp4`, or `out/captions.mov` (alpha) with `--mode captions`. Options: `--workers N`, `--from/--to`. |
| `scripts/assemble.py` | Lays `plates/<SHOT>.mp4` over the live slots, then the captions layer, then `audio/mix.wav` if present. Writes `out/final.mp4`. |
| `scripts/compare.py` | Compares against the reference at identical absolute frames: `out/compare/side_by_side.mp4`, `sheet.jpg` and `cuts.md`. |
| `scripts/stills.mjs` | Quick stills at chosen frames, written to `out/stills/`. |
| `higgsfield/README.md` | Character sheet, location sheet and per-shot prompts for the seven live-action slots. |
| `reference/` | The local reference download. It is gitignored and fetched with `scripts/fetch_reference.sh`. |

## Workflow

```bash
npm install                      # playwright (uses the preinstalled Chromium)
npm run preview                  # http://localhost:4173/src/ : scrub, play, reference onion-skin, live JSON editing
npm run render                   # out/ui.mp4          (~3 fps with 4 workers on 4 cores)
npm run render:captions          # out/captions.mov
# generate plates in Higgsfield → plates/S05.mp4 … plates/S24.mp4
npm run assemble                 # out/final.mp4
scripts/fetch_reference.sh && npm run compare
```

Editing: change frames, camera keys or copy in `timeline/timeline.json`, or in the preview's side panel
(Apply, then Download), then re-render. Camera keys are focus point `x,y`, scale `s`, rotation `r`, `tilt`,
`blur` and opacity `o`. Each key can set `ease`: `linear`, `in`, `out`, `inOut`, `snap` or `back`. Motion blur
is added automatically from camera speed.

## Cut grid (absolute frames @24 fps)

| # | Frames | Kind | Beat |
|---|---|---|---|
| S01 | 0–68 | UI | title lockup builds, radial burst |
| S02 | 68–172 | UI | chat app: sidebar → Extensions → search → Add |
| S03 | 172–198 | UI | pull-back off the extension icon |
| S04 | 198–257 | UI | extension home, scroll and dolly |
| S05 | 257–287 | live | ECU: SD card into reader |
| S06 | 287–364 | live | wide → push to CU, dictation |
| S07 | 364–436 | live | MS, he stands, tilt |
| S08 | 436–483 | UI | prompt types into the composer |
| S09 | 483–508 | UI | macro send click, tilt-away |
| S10 | 508–599 | UI | user cursor morphs into agent cursor (beat at 526) |
| S11 | 599–662 | UI | file browser, snap pull-back (beat at 621), selection, whip |
| S12 | 662–719 | UI | editor bin populates |
| S13 | 719–807 | live | floor-pump insert, slider |
| S14 | 807–841 | UI | track headers close-up |
| S15 | 841–941 | UI | full editor, clips snap in |
| S16 | 941–1099 | UI | status 1: colour mismatch → grade match |
| S17 | 1099–1134 | UI | file chip dropped into a folder |
| S18 | 1134–1181 | live | gauge CU insert |
| S19 | 1181–1437 | UI | status 2: boom mic (beat at 1258) → full-frame Studio Fill scan |
| S20 | 1437–1480 | UI | export panel, Render click, slide-off |
| S21 | 1480–1560 | UI | desktop file, "Done." toast, cursor hands back to the user |
| S22 | 1560–1691 | live | reaction |
| S23 | 1691–1752 | UI | account menu, credits tick down |
| S24 | 1752–1812 | live | wide exit, tagline super |

`npm run compare` currently reports **0 frames** max Δ between all 24 reference cuts/beats and the timeline.
