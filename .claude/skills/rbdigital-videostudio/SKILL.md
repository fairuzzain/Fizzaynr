---
name: "rbdigital-videostudio"
description: "9:16 short-video studio with 110 styles (5 signature tested styles + 105 recipe styles, incl. 10 real-3D Three.js styles), two modes: Code-only (HyperFrames + generated VO) or Flow (images + generated VO). Use for any \"buat video\", explainer/story/ad short, Flow prompts, VO script, or uploaded images/mp3. Always ask mode + style first, full style menu as text."
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Video Style Studio

Reply in the user's language (default: informal Bahasa Melayu / rojak when they write in Malay), concise. Give anything they must copy (prompts, VO script) inside code blocks. After mode + style are chosen, work autonomously — no confirmation pauses between steps.

## Step 0 — Ask MODE + style (mandatory)

If their message doesn't already say both, ask in ONE message: mode, then the FULL style menu (all 110, every category), plus the topic if not given (or offer to pick one). He answers e.g. "A 39". He may also add a size (e.g. "16:9") — default is 9:16.

**How to show it (strict):**
- **Never use AskUserQuestion / button cards / option pickers for the mode or the style.** They only fit 4 options, so they end up seeing ~5 styles. This has happened — don't repeat it.
- Never shorten, summarise, or "recommend a few" instead of the menu. Paste both code blocks below exactly as written, all 110 styles.
- Put the menu in your final reply text and end the turn there (or send it with SendUserMessage if you must keep working). Text written between tool calls may be summarised and they won't see the list.
- You may add ONE line under the menu with 3–4 suggested numbers for their topic, but the full menu must still be shown.
- **Preview images first:** never send them straight from the skill folder (it's an internal app/plugin folder the viewer can't open → "Couldn't load this preview"). Copy first: `mkdir -p previews && cp <skill>/assets/previews/menu-style-*.jpg previews/` (into `/mnt/user-data/outputs/` if it exists, else the current working/scratchpad folder), then send the 6 COPIES `previews/menu-style-1.jpg` … `menu-style-6.jpg` by full path in ONE SendUserFile call (in order), caption "Contoh visual 110 style, pilih nombor". Sheet map: 1 = 1–19 Cerita & Drama, 2 = 20–35 Fakta & Edu, 3 = 36–59 Data + Hook & Viral, 4 = 60–83 Tech + Jualan & Brand, 5 = 84–100 Seni & Kraf, 6 = 101–110 3D Sebenar. The images are illustrative mockups of each style's look, not renders. Then still paste the full text menu below in the final reply. If SendUserFile isn't available (Claude Code terminal), give the full path of the skill's `assets/previews/` folder so they can open it, then show the text menu.

```
Nak buat mode mana?
 A) CODE ONLY — semua visual aku buat guna code (HyperFrames), tak payah gambar. Aku jana VO sekali.
 B) FLOW — aku jana gambar dengan Nexabot dan VO, lepas tu aku edit.
```

```
Nak buat style apa? (jawab nombor)   ★ = signature style (paling tested)

CERITA & DRAMA
  1 Komik/manga★   2 Polaroid siasatan★   3 Fake chat    4 Dokumentari
  5 Trailer filem    6 Anime opening    7 CCTV/found footage
  8 VHS retro    9 Buku cerita budak   10 Claymation   11 Diari/jurnal
 12 Galeri muzium   13 Kalendar koyak   14 Infinite zoom
 15 Storytime Reddit   16 Film noir   17 Mockumentary
 18 Filem bisu 1920an   19 Siluet senja

FAKTA & EDU
 20 Scrapbook sticker★  21 Whiteboard   22 Chalkboard   23 Mind map
 24 Timeline sejarah   25 Peta perjalanan   26 Blueprint
 27 Isometric 3D   28 Kuiz game show   29 Tutorial langkah
 30 Lakaran → warna   31 Mitos vs fakta   32 Stickman   33 Sains makmal
 34 Angkasa kosmik   35 X-ray / imbasan

DATA & PERBANDINGAN
 36 Infografik   37 Resit/bil   38 Split screen VS   39 Countdown/Top 5
 40 Excel animasi   41 Tier list   42 Bracket kejohanan   43 Roda putar
 44 Siaran sukan / scoreboard   45 Ramalan cuaca

HOOK & VIRAL
 46 Kinetic typography★  47 Caption viral   48 Podcast audiogram
 49 Photo slideshow beat   50 Kad flip reveal★  51 Foto + contengan
 52 Meme format   53 Papan split-flap   54 POV   55 Talking head AI
 56 Street interview   57 TikTok Live   58 Day in my life
 59 Blackout poetry

TECH & MODEN
 60 Skrin phone/Google   61 Terminal hacker   62 Neon cyberpunk
 63 Pixel art 8-bit   64 Flat motion graphic   65 Retro desktop Win95
 66 Y2K chrome   67 Game HUD / quest   68 Video call grid
 69 Low poly 3D

JUALAN & BRAND
 70 Iklan produk/TikTok Shop   71 Testimonial   72 Thread/post sosial
 73 Poster vintage   74 Surat khabar   75 Paper cut parallax
 76 Majalah cover   77 UGC ad   78 Unboxing   79 TVC sinematik
 80 Problem → solution   81 Before & after   82 Macro ASMR produk
 83 Resepi top-down

SENI & KRAF
 84 Stop motion flatlay   85 Sand art   86 Bata mainan
 87 Miniatur tilt-shift   88 Ukiyo-e Jepun   89 Wayang kulit   90 Batik
 91 Pop art   92 Collage surreal   93 One-line art   94 Bauhaus geometri
 95 Groovy 70an   96 Kawaii pastel   97 Stained glass
 98 Kraf felt & kadbod   99 Grafiti dinding  100 Seni Islamik geometri

3D SEBENAR (Three.js — code only)
101 Produk 3D pusing  102 Kad terapung 3D  103 Globe 3D
104 Teks 3D gergasi  105 Kamera terbang (dunia low-poly)
106 Zarah jadi bentuk  107 Carta bar 3D  108 Bilik diorama 3D
109 Galaksi 3D  110 Domino / chain reaction
```
If they say "kau pilih", pick what fits the topic (story → 1/2/3/15, facts → 20/39/31, numbers → 36/37/40, tips → 46/47, product → 70/77/81, horror → 2/7/8, lucu → 52/65/17, journey → 13/25, ranking → 41/42, Islamic/takaful → 100/90, wow/premium 3D → 101/104/105, product launch → 101/102, data → 107, logo/brand reveal → 106/104, sebab-akibat → 110) and say which you picked in one line. If they name a style but no mode, still ask the mode (one short line).

**Paper cut parallax (75)** has its own workflow: if the `rbdigital-parallax` skill is installed, load it and follow it instead of this skill (choosing 75 here counts as asking for it explicitly). If it isn't installed, say in one line that paper cut parallax is a separate add-on skill and offer the closest style here instead (9 Buku cerita budak or 20 Scrapbook sticker). Never code-only.

## Step 1 — Read references

Mode A: also read `references/motion.md` (eases, cuts, anti-slop). Always read `references/common.md` (pipeline, Flow prompt rules, VO rules, rendering limits, audio, fonts). In Mode A, the HyperFrames engine section below overrides common.md wherever they differ (rendering, preview, fonts, muxing).
- Look up the chosen number in the table below. "references/x.md" → read only that file. "recipe below" → the recipe is in "Style recipes" at the end of this file (no reference file yet).
- Numbers run in menu order by category (1–19 Cerita, 20–35 Fakta, 36–45 Data, 46–59 Hook, 60–69 Tech, 70–83 Jualan, 84–100 Seni, 101–110 3D). If a number they give doesn't match the topic they described, confirm by style name. Headings inside the reference files may show other numbers — ignore them; this table is the source of truth.
- Reference files and recipes describe the LOOK (signature, layout, motion, audio). Their PIL/`common.py` drawing instructions apply to Mode B only; in Mode A translate the same look into HTML/CSS/SVG + GSAP.

| # | Style | Where |
|---|-------|-------|
| 1 | Komik / manga ✅ | references/manga.md |
| 2 | Polaroid siasatan ✅ | references/polaroid.md |
| 3 | Fake chat | references/fakechat.md |
| 4 | Dokumentari | references/documentary.md |
| 5 | Trailer filem | references/trailer.md |
| 6 | Anime opening | references/anime.md |
| 7 | CCTV / found footage | references/cctv.md |
| 8 | VHS retro | references/vhs.md |
| 9 | Buku cerita budak | references/storybook.md |
| 10 | Claymation | references/claymation.md |
| 11 | Diari / jurnal | references/diary.md |
| 12 | Galeri muzium | references/gallery.md |
| 13 | Kalendar koyak | references/calendar.md |
| 14 | Infinite zoom | references/infinitezoom.md |
| 15 | Storytime Reddit | recipe below |
| 16 | Film noir | recipe below |
| 17 | Mockumentary | recipe below |
| 18 | Filem bisu 1920an | recipe below |
| 19 | Siluet senja | recipe below |
| 20 | Scrapbook sticker ✅ | references/scrapbook.md |
| 21 | Whiteboard doodle | references/whiteboard.md |
| 22 | Chalkboard | references/chalkboard.md |
| 23 | Mind map | references/mindmap.md |
| 24 | Timeline sejarah | references/timeline.md |
| 25 | Peta perjalanan | references/map.md |
| 26 | Blueprint | references/blueprint.md |
| 27 | Isometric 3D | references/isometric.md |
| 28 | Kuiz game show | references/quiz.md |
| 29 | Tutorial langkah | references/tutorial.md |
| 30 | Lakaran → warna | references/sketch2color.md |
| 31 | Mitos vs fakta | recipe below |
| 32 | Stickman | recipe below |
| 33 | Sains makmal | recipe below |
| 34 | Angkasa kosmik | recipe below |
| 35 | X-ray / imbasan | recipe below |
| 36 | Infografik | references/infographic.md |
| 37 | Resit / bil | references/receipt.md |
| 38 | Split screen VS | references/splitscreen.md |
| 39 | Countdown / Top 5 | references/countdown.md |
| 40 | Excel animasi | recipe below |
| 41 | Tier list | recipe below |
| 42 | Bracket kejohanan | recipe below |
| 43 | Roda putar | recipe below |
| 44 | Siaran sukan / scoreboard | recipe below |
| 45 | Ramalan cuaca | recipe below |
| 46 | Kinetic typography ✅ | references/kinetic.md |
| 47 | Caption viral | references/viralcaption.md |
| 48 | Podcast audiogram | references/audiogram.md |
| 49 | Photo slideshow beat | references/carousel.md |
| 50 | Kad flip reveal ✅ (Mode A, HyperFrames) | references/cardflip.md |
| 51 | Foto + contengan | references/annotated.md |
| 52 | Meme format | references/meme.md |
| 53 | Papan split-flap | references/splitflap.md |
| 54 | POV | recipe below |
| 55 | Talking head AI | recipe below |
| 56 | Street interview | recipe below |
| 57 | TikTok Live | recipe below |
| 58 | Day in my life | recipe below |
| 59 | Blackout poetry | recipe below |
| 60 | Skrin phone / Google | references/phone.md |
| 61 | Terminal hacker | references/terminal.md |
| 62 | Neon cyberpunk | references/neon.md |
| 63 | Pixel art 8-bit | references/pixel.md |
| 64 | Flat motion graphic | references/flatmotion.md |
| 65 | Retro desktop Win95 | references/win95.md |
| 66 | Y2K chrome | recipe below |
| 67 | Game HUD / quest | recipe below |
| 68 | Video call grid | recipe below |
| 69 | Low poly 3D | recipe below |
| 70 | Iklan produk | references/productad.md |
| 71 | Testimonial | references/testimonial.md |
| 72 | Thread / post sosial | references/threads.md |
| 73 | Poster vintage | references/poster.md |
| 74 | Surat khabar | references/newspaper.md |
| 75 | Paper cut parallax | separate skill (rbdigital-parallax) — see Step 0 note |
| 76 | Majalah cover | references/magazine.md |
| 77 | UGC ad | recipe below |
| 78 | Unboxing | recipe below |
| 79 | TVC sinematik | recipe below |
| 80 | Problem → solution | recipe below |
| 81 | Before & after | recipe below |
| 82 | Macro ASMR produk | recipe below |
| 83 | Resepi top-down | recipe below |
| 84 | Stop motion flatlay | recipe below |
| 85 | Sand art | recipe below |
| 86 | Bata mainan | recipe below |
| 87 | Miniatur tilt-shift | recipe below |
| 88 | Ukiyo-e Jepun | recipe below |
| 89 | Wayang kulit | recipe below |
| 90 | Batik | recipe below |
| 91 | Pop art | recipe below |
| 92 | Collage surreal | recipe below |
| 93 | One-line art | recipe below |
| 94 | Bauhaus geometri | recipe below |
| 95 | Groovy 70an | recipe below |
| 96 | Kawaii pastel | recipe below |
| 97 | Stained glass | recipe below |
| 98 | Kraf felt & kadbod | recipe below |
| 99 | Grafiti dinding | recipe below |
| 100 | Seni Islamik geometri | recipe below |
| 101 | Produk 3D pusing | "3D engine" section + recipe below |
| 102 | Kad terapung 3D | "3D engine" section + recipe below |
| 103 | Globe 3D | "3D engine" section + recipe below |
| 104 | Teks 3D gergasi | "3D engine" section + recipe below |
| 105 | Kamera terbang (dunia low-poly) | "3D engine" section + recipe below |
| 106 | Zarah jadi bentuk | "3D engine" section + recipe below |
| 107 | Carta bar 3D | "3D engine" section + recipe below |
| 108 | Bilik diorama 3D | "3D engine" section + recipe below |
| 109 | Galaksi 3D | "3D engine" section + recipe below |
| 110 | Domino / chain reaction | "3D engine" section + recipe below |

✅ = tested. Scrapbook/manga/polaroid have working Mode B examples in `examples/` (scrapbook also uses `scripts/scrapbook_engine.py`); kinetic was tested code-only in the old PIL engine. Kad flip reveal (50) was tested in Mode A HyperFrames: tarot cards with CSS 3D `rotationY` flip (`.card` with `transform-style: preserve-3d`, `.back`/`.face` with `backface-visibility: hidden`, face pre-rotated 180°, `transformPerspective: 1800`), others drop away while the chosen card goes big on the left and its text panel enters on the right, then it returns face-up to the row. Three.js 3D layer was tested in Mode A HyperFrames (see "3D engine (Three.js)"). Python examples are for Mode B; in Mode A use them only as a guide to layout, timing and look. After the first successful Mode A video in a style, offer to save its `index.html` into `examples/hyperframes/<style>/` and repackage the skill (keep the same name).

**Fonts note (Mode B / PIL):** github raw may be blocked in the sandbox (get_font then saves a JSON error file → "OSError: broken file"). Fallback: `npm pack @fontsource/<font>` (e.g. anton, bebas-neue, bangers, permanent-marker, special-elite, caveat, oswald) and use `files/<font>-latin-400-normal.woff` — PIL loads .woff fine. Poppins is local. Mode A fonts: see the HyperFrames engine section.

Mode A → follow "Mode A". Mode B → follow "Mode B".

**No two styles may look the same.** When building, respect each style's signature (the "Signature" line in the recipe or reference). If a topic pushes two styles together, keep the chosen style's signature elements and drop the other's.

---

## Mode A — CODE ONLY (no images from the user) — HyperFrames engine

Every code-only video is built and rendered with **HyperFrames** (npm `hyperframes`, by HeyGen): the video is an HTML page (HTML + CSS + inline SVG) animated with a GSAP timeline, and HyperFrames captures it frame by frame in headless Chrome into an MP4. Do NOT draw Mode A frames with PIL / `common.py`. Everything on screen is HTML/CSS/SVG: shapes, icons, charts, UI mockups, text, backgrounds, particles, transitions. In the style recipe, ignore the Flow prompt / asset-cutting parts and replace every image slot with drawn SVG/CSS elements. the user uploads nothing except their own music if they want.

### A1. Setup (every new chat — the workspace resets, ~1 min)
```bash
W=<scratchpad dir>; cd $W
which hyperframes || npm i -g hyperframes
hyperframes browser ensure        # chrome-headless-shell
HYPERFRAMES_SKIP_SKILLS=1 hyperframes init <slug> --example blank --resolution portrait --non-interactive
cd <slug>
npm i gsap@3.14.2 --no-save --silent && mkdir -p vendor assets && cp node_modules/gsap/dist/gsap.min.js vendor/
```
- **Python is needed too** (music/SFX `Mix` in `common.py`, `vo_segments.py`, `look.py`, `slop_lint.py`; Mode B also PIL/OpenCV). Check `python --version` (or `py --version`) and `python -c "import numpy, PIL"`. Missing on **Windows (Claude Code on a PC)** → install it yourself, don't skip the music or QA:
  ```powershell
  winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
  python -m pip install numpy pillow opencv-python-headless scipy
  ```
  The current shell won't see the new PATH → call `"$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"` (Git Bash: `"$LOCALAPPDATA/Programs/Python/Python312/python.exe"`) or ask them to reopen Claude Code. No `--break-system-packages` on Windows. ffmpeg missing → `winget install -e --id Gyan.FFmpeg --scope user`; Node 22+ missing → `winget install -e --id OpenJS.NodeJS.LTS`. If winget fails, ask them to install Python from python.org (tick "Add python.exe to PATH") and wait. Linux sandbox: `pip install numpy pillow --break-system-packages -q` if missing.
- Default 1080x1920 portrait (`--resolution portrait`). If they ask 16:9 use `--resolution landscape` (1920x1080) and lay scenes out wide (e.g. visual left, text panel right); 1:1 → `square`. Read the project's `AGENTS.md` once for framework rules.
- **Sandbox blocks CDNs** (jsdelivr, unpkg, Google Fonts, external images). Reference `vendor/gsap.min.js`, never a CDN URL. A missing GSAP fails the render with `sub_timeline_script_failure`. Never leave any external http(s) URL in the HTML.
- Extra JS libs (e.g. a path morph helper) → install from npm and copy into `vendor/`. Install every `--no-save` package in ONE `npm i` command — a second `npm i --no-save` removes the earlier ones.
- **3D (Three.js):** styles 101–110 always, and optionally any code-only style where real depth helps (27, 34, 69, 25 as globe, 62, 70) — read the "3D engine (Three.js)" section at the end of this file first and follow it exactly (vendored `three.module.js` + `three.core.js`, `window.THREE = THREE`, scene = pure function of time via the `hf-seek` event, DOM text stays GSAP, render with `--workers 2`). Never `requestAnimationFrame` / clock / physics in a video.

### A2. Composition rules (HyperFrames)
- Root: `<div id="root" data-composition-id="main" data-start="0" data-duration="<total s>" data-width="1080" data-height="1920">` (swap width/height for landscape).
- Each scene: `<div id="sN" class="clip" data-start="<s>" data-duration="<s>" data-track-index="0">`; scenes fill the frame (`position:absolute; inset:0`). Persistent layers (background, grain, HUD, a row of cards that lives across scenes) sit outside scenes without timing and are animated by the timeline.
- Audio: `<audio src="assets/mix.wav" data-start="0" data-duration="<total>" data-track-index="9"></audio>` (one pre-mixed music+SFX track), plus a separate `<audio src="assets/vo.mp3" … data-track-index="8">` once they upload the VO.
- One paused root GSAP timeline: `window.__timelines = window.__timelines || {}; const tl = gsap.timeline({paused:true}); ... window.__timelines["main"] = tl; tl.seek(0);`
- Deterministic only: no `Math.random()`, `Date.now()`, network fetches. For particles/jitter use a seeded PRNG (mulberry32 with seed from the video title) and generate the elements in script before building the timeline.
- Animate transforms and opacity (x, y, scale, rotation, rotationY, opacity), not layout props (letterSpacing, width, top, font-size) — lint rejects them. For a letter-spread effect split into per-letter spans and animate x.
- `fromTo` tweens on overlays that start later need `immediateRender: false`, otherwise the start value shows from frame 0 (e.g. a white flash covering the opening).
- Long videos (>~25 s or many scenes): split scenes into `compositions/*.html` mounted with `data-composition-src` to keep files manageable (the `timeline_track_too_dense` / `nested_structure` lint warnings are fine to ignore for short videos).
- Useful docs offline: `hyperframes docs gsap|data-attributes|compositions|rendering|troubleshooting`.

### A3. Fonts & assets
- Local system fonts work directly in CSS: Poppins, Inter (`font-family: "Poppins"`).
- Other fonts: `npm pack @fontsource/<font>` → copy the `.woff2` into `assets/fonts/` and declare `@font-face` with a relative URL (tested: cinzel for tarot/elegant titles). `hyperframes-localize-fonts` can also help.
- Icons: write inline SVG yourself (person, phone, money, house, clock, tick, cross, chart, pin, flag…). Keep a consistent stroke width and corner radius per video. Avoid emoji/special glyphs (may be missing) — draw them in SVG.
- Textures (grain, paper, halftone, scanlines): CSS gradients, `repeating-linear-gradient`, or inline SVG `feTurbulence` filters — never external images.

### Style fit
- Strong fit (suggest these if they pick A but no style): 3, 13, 23, 24, 25, 26, 28, 31, 32, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 53, 57, 59, 60, 61, 62, 63, 64, 65, 67, 68, 72, 74, 80, 81, 93, 94, 95, 100, 101–110 (Three.js).
- OK with simplification (flat vector characters/props instead of illustrations — warn in one line): 4, 5, 7, 8, 9, 14, 15, 19, 20, 21, 22, 27, 29, 34, 52, 66, 69, 70, 71, 73, 76, 90, 96, 97.
- 101–110 are Mode A only. If they pick B with one of them: build it in Mode A and use their uploaded images as textures in the 3D (product photo on the turntable, Flow images on floating cards) — say so in one line.
- Needs real images, not code-only: 1, 2, 6, 10, 11, 12, 16, 17, 18, 30, 33, 35, 49, 51, 54, 55, 56, 58, 75, 77, 78, 79, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 98, 99 → suggest mode B or the closest code-only style.

### Visual rules
- Motion-graphic quality: one palette (3–4 colours + neutral) as CSS variables, one display font + one body font, consistent corner radius and stroke width.
- Use what HTML does well: gradients, `filter: blur()` glow orbs, box-shadow depth, backdrop blur, SVG strokes with `stroke-dashoffset` draw-on, CSS 3D flips, flexbox layout with auto text wrap (set `white-space: nowrap` where a line must not break).
- **Motion follows `references/motion.md` (read it before writing the timeline; it overrides eases/transitions in any recipe).** In short: paste the `E` ease presets + `F()` frame helper; entries decelerate (`E.land`, ~10–12 f), exits accelerate (`E.exit`); overshoot (`E.settle`) only on the hero, ~1 in 10 moves; nothing grows from `scale:0` (crash in from oversize or move in from the edge); move, don't fade; hard cut on motion is the default scene change, designed transitions (whip, zoom, flash, wipe) only on 2–3 key moments; no dead frames (slow drift/parallax under every scene).
- Every scene moves: elements enter with a move + stagger; numbers count up (tween a proxy object and write `textContent` in `onUpdate`); bars grow (scaleY/scaleX with transform-origin); lines draw on.
- No page chrome or deck layouts (corner labels, "02/05" counters, timecodes, progress bars, kicker over headline, headline-left + card-right every scene, letter-typed headlines, vibe-coded UI cards) unless it IS the style's signature — see motion.md §4.
- Charts and numbers animate from 0, are clearly labelled, and uncertain figures are hedged ("±", "lebih kurang").
- Safe zone (9:16): text inside x 90–990, y 250–1700. 16:9: keep ~80 px margins. Big, mobile-readable type (body ≥ 40px, headlines 90–150px).

### VO — generated by Claude
Claude generates the VO itself, after showing the script in the plan.

- English VO: `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" tts "<text>" --voice Fenrir --out vo.wav` (0.15 credit per request, no tone option).
- Malay VO: `python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/gemini_tts.py" -f script.txt -v Fenrir -i "<tone>" -o vo.wav` (Nexabot TTS rejects Malay; the free tier allows 10 requests a day per model, so send the whole script in one request).
- Never ElevenLabs. Voice names and the project voice lock follow the global rules.
- Script: see VO in common.md. One short paragraph per scene in scene order, no bracket audio tags, 90–120 words for ~45 s (≈ 2.3 words/s; scale to the video length). Factual, hedged numbers. Save it as `vo.txt`.
- Convert with `ffmpeg -i vo.wav assets/vo.mp3`, get pauses with `python <skill>/scripts/vo_segments.py assets/vo.mp3 -32 0.35` (paragraph breaks, then `-32 0.18` for phrases), map paragraphs to scenes by order, set every scene's `data-start`/`data-duration` and timeline times (keep all scene times as variables at the top of the script), render `mix.wav` with music at gain 0.3–0.35 under VO and SFX on those times, and add the VO `<audio>`.
- If the user supplies their own VO file, use it in place of the generated one.
- If they say "tak payah VO" → music + SFX only, no script.

Music and SFX stay synthesized offline with `Mix` in `scripts/common.py` (free) unless they upload their own: render one `assets/mix.wav` with music + SFX placed at the scene/beat times from your plan, and reference it with a single `<audio>`. Music is seeded per video (`seed="<video title>"`), so every video gets a different track — see Audio in common.md. `hyperframes beats` / `hyperframes audio` can detect beats/onsets in an uploaded track to sync cuts.

### A4. Check, preview, render
```bash
hyperframes lint                                   # must be 0 errors
python <skill>/scripts/slop_lint.py index.html --style <N>   # anti-slop + motion lint: 0 ERROR
hyperframes snapshot --at 1.5,5,9,14,20 --no-end -o snaps   # one time per scene
```
- **Read `snaps/contact-sheet.jpg` and LOOK at it** before the full render: overlaps, wrapped lines, text outside safe zone, overlays covering the frame, empty scenes. Fix and re-snapshot.
- Render: `hyperframes render --output <slug>.mp4` (default quality `looks`; `-q draft` for a quick test). With a Three.js layer add `--workers 2` and expect ~7 s render per 1 s of video; run the frozen-frame check from "3D engine (Three.js)". ~3–6 s of render per 1 s of video in this sandbox; the "Screenshot capture (slower)" notice is normal. Don't use `--docker`.
- Verify with the QA gates: `python <skill>/scripts/look.py <slug>.mp4 --expect-duration <s> --audio --sheet qa.jpg` (drop `--audio` for a silent first version). It checks: decodes, right size, not blank, duration matches, audio present, **no still run > 0.4 s mid-video**, **end hold ≤ 1.4 s**, and counts cuts. Every FAIL gets fixed and re-rendered — don't argue with it. Look at `qa.jpg` (frames from the real MP4) to confirm overlays rendered. Quote the numbers in one summary line ("QA: still max 0.2 s, end hold 0.9 s, 16 cuts"). A deliberate pause (silence before a punchline) may be passed with `--allow-still <t1,t2>`.
- Render fails with `REQUESTFAILED … ERR_TUNNEL_CONNECTION_FAILED` → an external URL is still in the HTML; localize it.

### Mode A flow
Short plan message (title + scene list: VO line + what gets drawn), then build immediately with no waiting: setup → write VO script (`vo.txt`) → generate VO → time scenes from it → write `index.html` (motion.md rules) → mix audio → lint + slop_lint → snapshot contact sheet, view, fix → render → look.py gates, fix any FAIL → copy to `/mnt/user-data/outputs/` (if that folder exists) and send the file with SendUserFile → reply with: short summary (3–5 bullets, music line, Nexabot credits used) and "kalau ada timing lari, bagitahu saat berapa".

---

## Mode B — FLOW images + generated VO

### Plan reply (no files yet)
One message with: title + scene list (on-screen text, VO line, visual, asset codes), Flow prompts in code blocks (see common.md for sheet rules — few prompts, combined sheets), and the VO script in one code block. Generate the images with Nexabot and the VO yourself; ask for uploads only for files the user wants to supply.

### Build when uploads arrive
Needs Python + numpy, Pillow, OpenCV, SciPy (Windows: install as in A1 setup). Motion laws from `references/motion.md` §2–3 apply here too (decelerate in / accelerate out, no scale-from-zero, hard cuts by default, no dead frames — apply them to the PIL lerp/easing curves). Identify files → cut/crop assets → VO timing (`scripts/vo_segments.py`) → write the style script → **contact sheet preview and look at it** → fix overlaps → render in chunks → mix audio → mux → `scripts/look.py` gates (fix any FAIL) → send the file → short summary (what's in it, timing synced from pauses, ask which second is off).

---

## Style recipes (styles without a reference file)

Each: **Signature** (what makes it unique — never drop it) · **Flow** (assets to ask for in mode B, as few sheets as possible) · **Build** · **Audio**. All 9:16, rules from common.md apply. In Mode A, build the same signature in HTML/CSS/SVG + GSAP (e.g. "grayscale filter" → CSS `filter: grayscale(1)`, "mask reveal" → CSS `clip-path` or SVG mask tween, "Voronoi/Delaunay" → precompute polygons in script with a seeded PRNG).

**15 Storytime Reddit** — Signature: top half = Reddit-style post card (avatar circle, username, upvotes, text revealed line by line), bottom half = satisfying loop gameplay-like background (parkour, kinetic sand, slime). Flow: 1 vertical satisfying-loop background (or 2x2 frames to cycle). Code-only: draw a procedural satisfying loop (rolling marbles, colour waves). Build: post card highlights the line being read, comment replies pop in at the end. Audio: VO is the core; lofi bed, notif on new comment.

**16 Film noir** — Signature: black & white high contrast, venetian-blind light stripes, rain, smoky detective narrator, typewriter captions. Flow: 2x2 noir film stills (detective in trench coat, rainy street lamp, office with blinds, shadowy figure) — "black and white, 1940s film noir". Build: B/W grade, animated blind-shadow overlay, rain streaks, grain heavy, iris transitions. Audio: drone + slow jazz-like lofi, rain (filtered noise), typing.

**17 Mockumentary** — Signature: The-Office-style confessional: character sits facing camera, awkward slow zoom, lower-third name + job title, cut-aways with deadpan "look at camera" pauses. Flow: 2x2 of the same character in a confessional seat with 4 expressions + 2x2 workplace cut-aways. Build: slow zoom 1.0→1.12, sudden snap-zoom on punchline, freeze-frame + record scratch. Audio: minimal music, awkward silence (mute), record scratch SFX.

**18 Filem bisu 1920an** — Signature: silent movie — sepia/B&W, heavy flicker + scratches + dust, 4:3 frame with rounded vignette, ornate intertitle cards with the dialogue (no lip text), sped-up comedic motion. Flow: 2x2 1920s silent-film stills. Build: flicker brightness per frame, vertical scratch lines, intertitle cards between shots, 16 fps stepped motion. Audio: ragtime-like piano (pluck fast cheerful), projector clatter (rapid knock).

**19 Siluet senja** — Signature: everything as solid black silhouettes against huge gradient sunset/sunrise skies, cinematic and emotional, large thin captions. Flow: 2x2 silhouette scenes ("pure black silhouettes against vivid sunset gradient sky"). Code-only: gradient sky + simple silhouette shapes. Build: slow parallax of silhouette layers, sun glow pulse, fade transitions. Audio: emotional pad, drone soft.

**31 Mitos vs fakta** — Signature: each claim card gets stamped "MITOS" (red rubber stamp, rotates in, ink splat) then flips to "FAKTA" (green) with the truth. Flow: optional 4x4 icon sheet for claims. Build: card flip (x-scale 1→0→1), stamp slam with shake, counter "MITOS #1/5". Audio: slam per stamp, ding on fakta.

**32 Stickman** — Signature: black stick figures on white/off-white, simple line physics (fall, run, bounce), hand-drawn wobble lines (boil effect: redraw with tiny random jitter every 3 frames). Flow: none needed (code). Build: skeleton joints animated with lerp poses, props as simple lines, labels in marker font. Audio: comedy music, pop/knock for impacts.

**33 Sains makmal** — Signature: lab aesthetic — microscope circle view (round vignette mask with crosshair), molecules/atoms orbiting, beakers bubbling, labelled diagram callouts. Flow: 2x2 microscope-view macro images (cells, crystals, bacteria, fibres) + 4x4 lab icon sheet. Build: circular mask zoom, focus-pull blur→sharp, orbiting dots, callout lines draw on. Audio: lofi, bubble pops, ding.

**34 Angkasa kosmik** — Signature: deep space — starfield parallax, glowing planets, nebula clouds, orbit lines, HUD-light labels, epic scale. Code-only: starfield + gradient planets + nebula noise. Flow: 2x2 space vistas. Build: flying-through-stars parallax, planet slow rotate (texture scroll), orbit dots. Mode A 3D option: real Three.js planets (`SphereGeometry` + flat/standard material, rim point lights) and a `Points` starfield the camera flies through ("3D engine (Three.js)"). Audio: drone + riser, boom on reveals.

**35 X-ray / imbasan** — Signature: scanner view — a scan bar sweeps across an object revealing its inside (X-ray blue-white negative), measurement labels and callouts, "SCANNING…" UI. Flow: 2x2 pairs: object normal + matching X-ray version (same angle). Build: mask reveal follows scan bar, glow line, callouts with numbers. Audio: scanner beep, hum (drone), ding on result.

**40 Excel animasi** — Signature: a spreadsheet UI — gridlines, cell selection box moving, formulas typed into the formula bar, numbers filling down, conditional-format colours, a chart generated at the end. Code-only. Build: cursor jumps cell to cell, typing() SFX, SUM result count-up, chart bars grow. Audio: typing, click pops, lofi.

**41 Tier list** — Signature: S/A/B/C/D tier rows (coloured labels left), item tiles dragged from a pool at the bottom into rows one by one, with a short reason caption. Flow: optional 4x4 item icon sheet. Code-only fine. Build: tile drag path with ease and drop bounce, row highlight on drop. Audio: whoosh on drag, pop on drop, slam for S tier.

**42 Bracket kejohanan** — Signature: tournament bracket (8 → 4 → 2 → 1) — two items face off, winner advances along bracket lines that draw on, final champion crown. Flow: optional 4x4 item sheet. Code-only fine. Build: zoom camera onto each matchup, VS flash, line draw-on to next round, trophy at end. Audio: slam per VS, crowd swell at champion.

**43 Roda putar** — Signature: spinning prize wheel with segments — spins, decelerates, ticks past segments, lands on a choice which then gets explained; repeat. Code-only. Build: wheel angle with ease_out over 3 s, pointer flick on each segment pass, winner segment glow. Audio: tick per segment (knock short), ding on land.

**44 Siaran sukan / scoreboard** — Signature: live sports broadcast — scoreboard bug top-left, play-by-play commentary captions, replay wipe with logo, "GOL!" / stats overlays comparing two sides. Flow: optional 2x2 action stills. Code-only fine. Build: score increments with slam, replay star-wipe, stat bars compare. Audio: crowd roar (filtered noise swell), whistle (sine 2.5 kHz trill), slam.

**45 Ramalan cuaca** — Signature: TV weather report — map of Malaysia (simple shapes) with animated weather icons, but forecasting a topic (e.g. "ramalan ekonomi minggu ni"), temperature-style big numbers, scrolling ticker at bottom. Flow: optional presenter 2x2. Code-only: map + icons drawn. Build: icons bob, numbers count, ticker scroll, presenter-style lower third. Audio: upbeat newsy music, whoosh per region.

**54 POV** — Signature: first-person viewpoint — hands/feet in frame, "POV: …" text pinned top in TikTok style, the world reacts to the viewer. Flow: 2x2 of first-person shots (hands holding phone, walking into a shop, opening a door, someone talking to the camera). Build: subtle walking bob (sin y offset), POV caption pinned, reaction subtitles of the other person. Audio: ambient room tone (static low) + music.

**55 Talking head AI** — Signature: one presenter character centred chest-up, jump-cut punch-ins (1.0 → 1.15) on every sentence, big captions with key word highlight, b-roll pop-up cards. No lip sync (say so) — use subtle breathing scale and eye-level framing. Flow: 2x2 of the same presenter (identical description) in 4 expressions/gestures + 1 room background. Build: swap expressions on beats, punch-in cuts, emoji/icon pop-ups beside head. Audio: VO-driven, light music, pop on b-roll.

**56 Street interview** — Signature: handheld mic with a coloured mic flag (topic name), interviewer question as top text, different "passers-by" answering, lower-third name tag ("Aiman, 24"). Flow: 2x2 of 4 different passers-by in a Malaysian street (mall, pasar, LRT, kedai mamak) facing camera, mic visible + 1 mic flag close-up blank. Build: fast cuts per answer, handheld shake, name tags slide in, crowd-noise. Audio: static() as street ambience, comedy music.

**57 TikTok Live** — Signature: livestream UI — LIVE badge + viewer count rising, comments scrolling bottom-left, gift animations flying, host speaking, "pin" product card. Flow: 1–2 host images (same person) in a live-selling setup. Code-only: host as stylised avatar. Build: comments stream (relevant questions answered by VO), viewer counter, hearts float up, product card pops. Audio: notif, hearts pops, lofi.

**58 Day in my life** — Signature: vlog timeline — big timestamps ("6:30 AM") in clean font before each clip, cosy aesthetic grade, quick montage of routine. Flow: 2x2 + 2x2 first-person/cosy routine shots of the same person/day. Build: timestamp flip-in per clip, soft warm grade, gentle zooms. Audio: lofi, clock tick on timestamps.

**59 Blackout poetry** — Signature: a page of dense printed text; words get blacked out with marker strokes until only a few remaining words form the message, which then highlight. Code-only. Build: typeset paragraph (typewriter/serif), marker strokes animate across lines (rounded rect growing), remaining words glow/highlight, camera slowly zooms. Audio: marker scribble, slam on final message, calm music.

**66 Y2K chrome** — Signature: liquid chrome 3D text, glossy bubbles, butterflies/stars sparkles, holographic iridescent gradient, early-2000s UI windows. Flow: 1 iridescent Y2K background + 4x4 sheet of chrome/glossy stickers (butterfly, star, heart, flip phone, CD, sparkle). Code-only: gradient chrome text via vertical colour bands + highlight. Build: floaty bob, lens-flare sweep, sparkle twinkle. Audio: cheerful music pitched up, sparkle pops.

**67 Game HUD / quest** — Signature: life as a video game — health/XP bars, quest log ("QUEST: …"), "+50 XP" popups, achievement unlocked toast, level-up flash. Flow: optional 2x2 character scenes. Code-only: full HUD drawn. Build: XP bar fills on each tip, achievement toast slides from top, level-up flash + particles. Audio: 8-bit-like blips (sweeps), level-up arpeggio, ding.

**68 Video call grid** — Signature: meeting app grid (2x2 or 3x3 tiles) with name labels, mute icons, speaking-tile green border, chat sidebar messages, "You're on mute" gag. Flow: 2x2 of 4 different people at home desks facing webcam. Code-only: avatar circles with initials. Build: active speaker border switches with VO, tiles zoom to fullscreen on key points. Audio: notif sounds, join chime.

**69 Low poly 3D** — Signature: faceted low-poly worlds (triangles, flat-shaded), camera glides over a tiny low-poly landscape, pastel/gem colours. Flow: 2x2 low-poly 3D scenes. Code-only: triangulated backgrounds (random points + Delaunay via scipy) with flat shading. Build: slow camera pan, triangles shimmer, objects pop in scale. Mode A 3D option: real low-poly terrain in Three.js (`PlaneGeometry` with seeded height per vertex, `flatShading: true`) + camera glide — see 105. Audio: calm ambient, soft pops.

**77 UGC ad** — Signature: handheld selfie-creator feel — slight constant handheld shake, phone-camera framing, creator holding product, casual hook text in TikTok-native white bold with black outline, jump cuts every 1.5–2 s. Flow: 2x2 sheet of the same creator (describe identically) in 4 selfie poses with the product (hold up, point, use, smile at camera), plus product shot. Build: Ken-burns punch-in on each jump cut, shake via shake_offset low amp continuous, word-by-word captions bottom-middle, "link kat beg kuning" sticker at end. Audio: lofi/cheerful low, pop per caption.

**78 Unboxing** — Signature: top-down box opening sequence: closed box → flaps open → items lift out one by one → flat-lay reveal. Flow: 2x2 sheet: closed box top-down, open box, items inside, all items laid out (same box, same table). Build: crossfade + scale between stages, each item gets a pop label with name/feature, sparkle particles on reveal. Audio: paper/rustle (paper()), pop per item, ding at reveal.

**79 TVC sinematik** — Signature: cinematic letterbox bars (2.39:1 band inside 9:16), slow push-ins, elegant serif/thin titles fading, warm grade, end packshot with tagline. Flow: 2x2 sheet of 4 cinematic film stills (golden hour, shallow depth of field) + 1 product packshot on clean backdrop. Build: slow 1.0→1.08 zoom per shot, letterbox bars, fade-through-black cuts, light leak overlay. Audio: emotional pad (drone low + cheerful slow), riser into packshot, boom on logo.

**80 Problem → solution** — Signature: two halves of the video graded differently: problem part desaturated grey + red crosses + slow; solution part bursts into full colour + green ticks + faster pace, with a "colour wipe" transition at the pivot. Flow: 2x2: person frustrated, mess/problem object, person happy, product hero. Build: grayscale filter (ImageOps) for part 1, radial colour wipe at the pivot, tick/cross icons drawn. Audio: tense → cheerful switch at the pivot, whoosh + flash.

**81 Before & after** — Signature: draggable slider wipe — a vertical divider line with a round handle sweeps across the SAME framing, "SEBELUM" / "SELEPAS" tags. Flow: 2x2 of 2 matching before/after pairs (identical camera angle and composition, only the subject changes). Build: compose both, mask by x of handle, handle eases back and forth then completes; repeat per pair. Audio: whoosh per sweep, ding on final reveal.

**82 Macro ASMR produk** — Signature: extreme close-up textures — slow, satisfying, shallow depth of field, slow-motion pour/squeeze/slice, minimal tiny text. Flow: 2x2 macro shots of the product (texture, drop, pour, detail). Build: very slow zoom/pan 1.0→1.15, focus-pull blur, soft fades, 1–3 word captions. Audio: no music or very soft, ASMR SFX (crisp clicks, pour noise filtered).

**83 Resepi top-down** — Signature: overhead cooking (Tasty style) — ingredients drop into the bowl/pan from top, quantities pop as labels, sped-up steps, final hero dish. Flow: 2x2 top-down cooking steps (same pan/bowl, same table) + 4x4 ingredient cut-outs. Build: ingredients drop with bounce into frame, step numbers, fast-forward feel. Audio: cheerful, pop per ingredient, sizzle (filtered noise).

**84 Stop motion flatlay** — Signature: real objects on a table shot from top, moving in choppy 8–12 fps steps (hold each pose 2–3 frames), hand-made feel. Flow: 4x4 sheet of everyday objects (cut out) + 1 top-down table texture. Build: positions quantised to 8 fps, slight random rotation per step, objects slide/assemble into shapes or words. Audio: paper/knock per step, ukulele-ish cheerful.

**85 Sand art** — Signature: sand drawing on a lit glass table — warm amber light, images "brushed" in and wiped away by hand sweeps, morphing scene to scene. Flow: 2x2 sand-art images on backlit glass (same warm palette). Build: reveal with noisy brush-mask, wipe-out with directional smear mask, morph by dissolve with noise. Audio: soft sand hiss (filtered noise), calm music.

**86 Bata mainan** — Signature: everything built from toy building bricks (studs visible), characters as minifigure-like toys, brick-by-brick build-up animation. No real brand names/logos. Flow: 2x2 toy-brick dioramas + 4x4 brick character/prop sheet ("generic toy bricks, no logos"). Build: bricks drop in with bounce, stepped stop-motion moves. Audio: plastic click (short knock high), cheerful.

**87 Miniatur tilt-shift** — Signature: real scenes that look like tiny models — strong top+bottom blur band, saturated colours, sped-up motion feel. Flow: 2x2 high-angle photos of Malaysian scenes (pasar, traffic, KLCC area, kampung) "tilt-shift miniature effect". Build: apply blur bands (Gaussian on top/bottom with gradient mask), boost saturation, small elements (cars) moving fast, pans. Audio: playful music sped up, tiny pops.

**88 Ukiyo-e Jepun** — Signature: Japanese woodblock print look — flat colours, bold outlines, wave patterns, washi paper texture, vertical red seal stamps for captions. Flow: 2x2 ukiyo-e prints of the scenes + 1 washi paper texture. Build: layer parallax of print elements, captions on vertical red banners, wave pattern wipes. Audio: koto-like pluck (_pluck with pentatonic notes), calm.

**89 Wayang kulit** — Signature: Malaysian shadow puppetry — intricate leather puppets as shadows on a glowing off-white screen, flickering oil-lamp light, puppets move on rods with pivot limbs. Flow: 4x4 sheet of wayang kulit puppet silhouettes (characters, trees/gunungan, props) on plain grey. Build: puppets as dark silhouettes with soft blur halo, flicker brightness, limb rotation at joints, gunungan wipe between scenes. Audio: gamelan-like plucks (pentatonic), drum (knock).

**90 Batik** — Signature: Malaysian batik art — canting wax lines draw on first, then colour floods in the outlines, floral/leaf motifs frame the text. Flow: 2x2 batik-style illustrations (crisp outlines) + 1 batik pattern border. Code-only: procedural floral motifs with spline lines. Build: line draw-on (reveal mask along path), colour flood fill dissolve, motif borders rotating slowly. Audio: calm traditional-flavoured plucks.

**91 Pop art** — Signature: 1960s pop art — Ben-Day halftone dots, bold primaries (red/yellow/blue), thick black outlines, repeated panels of the same image in different colourways (Warhol grid). Flow: 2x2 pop-art portraits/objects. Build: halftone overlay, 2x2 colour-swap grid moments, "WOW!" explosion bursts drawn. Audio: retro surf/cheerful, slam on bursts.

**92 Collage surreal** — Signature: Monty-Python-style cut-out collage — vintage photo cut-outs with jagged edges, oversized heads, objects flying in from odd angles, surreal mash-ups. Flow: 4x4 sheet of vintage engraving/photo cut-outs (hand, eye, head, clock, bird, machine, cloud…). Build: hinge rotations at cut edges, sudden pop-ins, sky backdrop with paper texture. Audio: comedy, boing/pop.

**93 One-line art** — Signature: a single continuous black line draws every image without lifting the pen, morphing from one drawing into the next, minimal cream background, small serif captions. Code-only: draw paths as polylines and reveal progressively; morph by interpolating resampled point lists. Flow: optional 2x2 one-line drawings to trace. Audio: soft pen scribble, piano-like calm.

**94 Bauhaus geometri** — Signature: Swiss/Bauhaus graphic design — circles, squares, triangles in red/blue/yellow/black on off-white, strict grid, bold sans text, shapes snap and rotate into compositions. Code-only. Build: shapes slide on grid lines, rotate 90° snaps, text aligned to grid. Audio: minimal electronic beat (cheerful bass only), click pops.

**95 Groovy 70an** — Signature: 1970s psychedelic — wavy warped text, orange/brown/mustard/teal palette, concentric rainbow stripes, flower power, lava-lamp blobs. Code-only possible (sin warp on text rows). Flow: 1 groovy background + 4x4 retro stickers. Build: text warp waves, rotating sunburst stripes, blob morph. Audio: funky comedy music, wah-like sweeps.

**96 Kawaii pastel** — Signature: cute chibi characters with blush cheeks, pastel palette, bouncy squash-and-stretch, sparkles and hearts, rounded bubbly font. Flow: 4x4 sheet of chibi characters/props (same mascot in many poses). Build: squash/stretch scale on every entry, hearts float, soft bounce idle. Audio: cheerful pitched up, pop/boing.

**97 Stained glass** — Signature: images made of coloured glass panes with thick dark lead lines, light shining through (glow), panes light up piece by piece. Code-only: Voronoi panes (scipy) coloured from a palette/mask. Flow: 2x2 stained-glass illustrations. Build: pane-by-pane light-up, light rays sweep, glass shimmer. Audio: choir-like pad (drone high), chimes (ding).

**98 Kraf felt & kadbod** — Signature: handmade craft world — felt fabric and corrugated cardboard textures, stitched edges, googly eyes, wobbly stop-motion moves. Flow: 2x2 felt/cardboard dioramas + 4x4 felt character/prop sheet. Build: 10 fps stepped motion, slight random wobble, characters hop. Audio: cheerful ukulele-ish, soft felt thumps.

**99 Grafiti dinding** — Signature: street art — brick/concrete wall, spray-paint reveals (spray noise mask) of bold graffiti text and characters, drips, paint can rattle. Flow: 2x2 graffiti murals on walls + 1 blank wall. Build: spray reveal along path with noisy soft brush, drips grow down, camera pans along wall. Audio: spray hiss (noise), can rattle (rapid knock), hip-hop-ish beat (lofi faster).

**100 Seni Islamik geometri** — Signature: Islamic geometric art — star/rosette tessellation lines that grow from the centre, gold on deep emerald/navy, arabesque borders, calm and elegant (great for takaful / Ramadan / nilai). Code-only: generate 8-fold star patterns with rotated polygons, reveal lines progressively. Flow: optional 1 ornamental background. Build: pattern grows outward, gold shimmer sweep, text inside a mihrab-arch frame. Audio: calm pad, soft chimes; no instruments if they prefer (VO + ambience only — ask once if topic is religious).

### 3D SEBENAR (101–110) — Three.js, Mode A only

All ten: read "3D engine (Three.js)" below first (setup, `renderAt(t)` pattern, `kf()` keyframes, render with `--workers 2`). The 3D lives on one persistent `<canvas>`; all text, captions and numbers are DOM + GSAP on top. One palette → material colours + 2 coloured rim lights + CSS gradient background behind the transparent canvas. Every scene changes something in 3D (camera move, object swap, colour shift) — never a static model behind slides. Uploaded images (product photo, Flow images) can go on as textures.

**101 Produk 3D pusing** — Signature: one hero object on a glossy turntable in a "studio" (soft gradient backdrop, reflective floor), slow 360° spin, camera orbits and pushes in to call out features with thin DOM callout lines + labels. Build: hero modelled from primitives (bottle = `LatheGeometry` from a profile, box = `RoundedBoxGeometry` with their product photo as face texture, phone, card, shield for takaful); floor = circle with darker radial CSS behind; feature beats = camera `kf` to a new angle + label pop; final hero shot + price/CTA. Audio: sleek minimal beat, whoosh on camera moves, ding on each feature.

**102 Kad terapung 3D** — Signature: listicle as thick rounded cards floating in 3D space, gently bobbing; camera glides card to card, each card flips to show the point, the rest drift blurred in the background (fog). Build: `RoundedBoxGeometry(2.2,1.3,.08)` cards (front = canvas texture drawn with text OR DOM text aligned on top while the card faces camera); stagger along a curve; per item: camera move → card `rotation.y` flip with `ease.back` → DOM title. Audio: soft pluck per card, whoosh between.

**103 Globe 3D** — Signature: a spinning stylised Earth (dot-matrix or low-poly continents, no photo), glowing arcs fly between cities, pins pop up, camera zooms to the country. Build: sphere + `Points` placed from a hand-made lat/long list of land dots (or low-poly icosahedron detail 3 with ocean/land colours), arcs = `QuadraticBezierCurve3` → `TubeGeometry` drawn on with `setDrawRange` from `t`, pins = cone + DOM label projected with `vector.project(camera)`. Great for "orang Malaysia di seluruh dunia", export, travel. Audio: airy pad, whoosh per arc, pop per pin.

**104 Teks 3D gergasi** — Signature: one giant extruded 3D word/number is the hook — slams in from the camera, rotates to reveal its depth and bevel, lit with coloured rims; then the next word replaces it. Build: `TextGeometry` with a typeface JSON made by `ttf2typeface.mjs` (code in "3D engine") from the video's display font (Poppins/Anton/Bebas `.ttf`), `bevelEnabled`, `depth .25–.4`, metallic standard material; slam = `kf` on z from camera to 0 with `ease.out` + camera shake (sin with decay); word swap on beats; small DOM subtitle below. Max ~6 words total (geometry is heavy). Audio: impact boom per word, riser between.

**105 Kamera terbang (dunia low-poly)** — Signature: continuous first-person flight over a tiny low-poly world (hills, trees, houses, road) — each VO point is a landmark the camera reaches, with a floating DOM sign. Build: terrain `PlaneGeometry(40,120,40,120)` with seeded vertex heights, `flatShading`; trees = cone+cylinder, houses = box+cone roof, placed with seeded PRNG along a path; camera follows a `CatmullRomCurve3` via `curve.getPointAt(kf(t,...))` and looks slightly ahead; fog for depth; pastel palette. Audio: calm adventure lofi, wind (filtered noise), chime per landmark.

**106 Zarah jadi bentuk** — Signature: thousands of particles swirl and snap into shapes (logo, number, icon, word), explode and re-form into the next shape. Build: sample target points from shapes at build time (draw text/icon on an offscreen 2D canvas, read pixels → point list; or `geometry.attributes.position` of a mesh); `Points` with one `BufferAttribute`; in `renderAt` blend each point between seeded scatter positions and target positions with per-point delay (`kf` per point is too slow — compute `p = clamp01((t - start - delay_i)/dur)` inline) and write into the attribute, then `needsUpdate = true`. ≤ 20k points. Audio: shimmer/whoosh on swirl, bass hit when shape locks.

**107 Carta bar 3D** — Signature: a 3D bar chart on a floor grid — bars rise with ease-out, camera orbits around the chart, the winning bar glows, numbers count up in DOM labels pinned above each bar. Build: `BoxGeometry` bars (scale.y from `kf`, origin at bottom by translating geometry up 0.5), `GridHelper` floor, labels positioned each frame by projecting bar tops to screen and setting DOM transform in `renderAt` (same function, so deterministic); hedge uncertain numbers. Audio: tick per bar, rising tone, ding on winner.

**108 Bilik diorama 3D** — Signature: a cut-away isometric room (3 walls + floor, like a dollhouse) built in 3D, camera rotates around it slowly; objects pop into the room one by one as the VO lists them (e.g. "rumah selamat", "office setup", "dapur sihat"). Build: thin `BoxGeometry` walls with pastel colours, furniture from primitives (bed, table, lamp, plant, laptop), orthographic camera for clean isometric (`OrthographicCamera`) or perspective with low FOV 25; pop-in = scale `kf` with `ease.back`; DOM labels with leader lines. Audio: cosy lofi, pop per object.

**109 Galaksi 3D** — Signature: a huge spiral galaxy of coloured particles; the camera starts far out and dives in through the arms to a single glowing star/planet where the message sits. Build: `Points` placed on 3–5 log-spiral arms with seeded spread (colour from core-hot to arm-cool), slow rotation `t * .05`, camera path from far to near with `kf`; core glow = CSS radial gradient behind canvas lined up with the centre; big DOM title at the end. Use for motivasi, "1 dalam sejuta", scale/peluang topics. Audio: cosmic drone, riser on the dive, boom at arrival.

**110 Domino / chain reaction** — Signature: a line of dominoes (or blocks/coins) knocks over in a chain that snakes across a table, each domino labelled with a step of the story (cause → effect); the last one triggers the punchline object. Build: dominoes = `BoxGeometry(.3,1,.08)` placed along a curve; each one's fall is `rotation.x = kf(t, [[t_i, 0], [t_i+.35, angle]], ease.in)` with `t_i = T0 + i*gap` (closed-form, no physics); camera tracks the wave front; DOM step labels pop as their domino falls. Audio: crisp click per domino (tight SFX grid), building music, big hit at the end.

---

## 3D engine (Three.js) — Mode A / HyperFrames ✅ tested

Use for styles 101–110, and as an optional 3D layer inside any code-only style (27 Isometric, 34 Angkasa, 69 Low poly, 25 Peta → globe, 62 Neon, 70 Iklan produk) when real depth helps. Tested on hyperframes 0.8.x + three 0.186 in the sandbox: WebGL renders on software GPU (SwiftShader), 180/180 frames advance smoothly, extruded 3D text + addons load fine.

### How HyperFrames drives Three.js
- On every frame seek, the runtime sets `window.__hfThreeTime = t` and fires a `hf-seek` event on `window` with `e.detail.time` (seconds). Your listener renders the scene for exactly that time.
- If `window.THREE` exists, HyperFrames waits for `THREE.DefaultLoadingManager` (fonts, textures, models) to finish before capturing. So always set `window.THREE = THREE`.
- GSAP still drives every DOM layer (text, captions, UI, transitions) on the root timeline as usual. Three.js only draws the `<canvas>`.

### Setup (add to A1, after gsap)
```bash
npm i gsap@3.14.2 three --no-save --silent      # install ALL --no-save packages in ONE command; a second `npm i --no-save` wipes the first
cp node_modules/three/build/three.module.js node_modules/three/build/three.core.js vendor/   # module imports ./three.core.js — copy both
# addons only if needed (keep folder structure — addons import each other with ../)
mkdir -p vendor/addons && cp -r node_modules/three/examples/jsm/{loaders,geometries,utils} vendor/addons/
```
There is NO `three.min.js` UMD build any more (removed r160) — use the module build. Never a CDN URL.

### Page skeleton
```html
<div id="root" data-composition-id="main" ...>
  <canvas id="gl" width="1080" height="1920"></canvas>   <!-- persistent layer, outside scenes, no timing attrs -->
  <div id="s1" class="clip" data-start="0" ...> ...DOM text... </div>
</div>
<script> /* normal GSAP root timeline for DOM, window.__timelines["main"] = tl; tl.seek(0); */ </script>
<script type="importmap">{"imports":{"three":"./vendor/three.module.js","three/addons/":"./vendor/addons/"}}</script>
<script type="module">
  import * as THREE from "three";
  // import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
  window.THREE = THREE;
  const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("gl"), antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(1080, 1920, false); renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, 1080/1920, 0.1, 100);
  // ...build meshes ONCE here (seeded PRNG for any randomness)...
  function renderAt(t){ /* set every transform from t */ renderer.render(scene, camera); }
  window.addEventListener("hf-seek", e => renderAt(e.detail.time));
  renderAt(window.__hfThreeTime || 0);
</script>
```
CSS: `#gl{position:absolute;inset:0;width:1080px;height:1920px}`. Transparent clear colour → the CSS background/gradient shows behind the 3D, so backgrounds stay in CSS. Landscape: canvas 1920x1080 and camera aspect 1920/1080.

### Golden rules (determinism)
1. **The 3D scene is a pure function of time.** Every position/rotation/scale/colour/camera value is computed inside `renderAt(t)` from `t` only. No `requestAnimationFrame`, `clock.getDelta()`, `Date.now()`, `performance.now()`, `Math.random()`, physics engines or accumulated state (`x += v`).
2. Keyframes with the `kf` helper (copy into every 3D video):
```js
const clamp01 = x => Math.min(1, Math.max(0, x));
const ease = { in: x => x*x*x, out: x => 1-Math.pow(1-x,3), inOut: x => x<.5 ? 4*x*x*x : 1-Math.pow(-2*x+2,3)/2,
               back: x => { const c1=1.70158,c3=c1+1; return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2); } };
function kf(t, keys, e = ease.inOut){            // keys: [[time, value], ...]
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++){ const [t1,v1]=keys[i], [t0,v0]=keys[i-1];
    if (t <= t1) return v0 + (v1-v0)*e(clamp01((t-t0)/(t1-t0))); }
  return keys[keys.length-1][1];
}
// camera.position.z = kf(t, [[0,10],[2.8,7.5],[6,6]]);  mesh.scale.setScalar(Math.max(.001, kf(t,[[0,0],[.9,1]],ease.back)));
```
Keep scene times as the same variables used for the GSAP scene cuts so VO re-timing stays one edit.
3. Randomness (stars, particles, scatter) → seeded `mulberry32` at build time, stored in arrays; motion = `base + f(t)`.
4. "Physics" (falling, domino, bounce) → hand keyframes or closed-form (`y = y0 - 0.5*g*t²`, `abs(sin)` bounce with decay), never a simulation.
5. Never animate the canvas with GSAP and never put the canvas inside a timed scene clip — show/hide 3D objects per scene inside `renderAt` (`obj.visible = t >= S2 && t < S3`).

### Text
- Captions, titles, numbers → **DOM text with GSAP** (sharp, uses the video fonts, counts up easily). Put them over the canvas.
- Real 3D extruded text only for the hero word (style 104): `FontLoader` + `TextGeometry`. Fonts must be typeface JSON, made offline (npm three has no fonts; three's TTFLoader pulls opentype.js from a CDN):
```bash
npm i gsap@3.14.2 three opentype.js@1.3.4 --no-save --silent
node ttf2typeface.mjs /usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf assets/fonts/poppins_bold.typeface.json
```
  Any `.ttf` works (fontsource `.ttf` via `npm pack`, or local Google fonts). Load it with `new FontLoader().load("assets/fonts/poppins_bold.typeface.json", f => { ...build mesh...; renderAt(window.__hfThreeTime||0); })` — the loading manager makes HyperFrames wait. `geometry.center()` before placing. Keep `curveSegments` ≤ 6, bevel small.

### Images in 3D (Flow / uploaded photos)
Uploaded images (product photo, Flow image) can be textures: `new THREE.TextureLoader().load("assets/x.png")`, set `tex.colorSpace = THREE.SRGBColorSpace`, use on `PlaneGeometry`/`RoundedBoxGeometry` faces (cards, posters, product box). Loader is awaited automatically. Keep textures ≤ 2048 px.

### Looks that work on software GL (and are fast)
- `MeshStandardMaterial` with `flatShading: true` (low-poly), `metalness` ≤ .4. Light rig: ambient .3–.4 + 1 directional key + 2 coloured `PointLight` rims (palette colours) → instant premium look.
- `EdgesGeometry` + `LineBasicMaterial` for wireframe/blueprint overlays; `Points` for stars/particles (size .03–.08); `scene.fog` matching the CSS bg colour for depth.
- Glow → put a CSS radial-gradient/blur orb behind the canvas instead of bloom.
- Avoid: post-processing (bloom, SSAO, DOF), real-time shadows (`castShadow`), `MeshPhysicalMaterial` transmission, HDR/PMREM environment maps, > ~150k triangles, `IcosahedronGeometry` detail > 4, more than ~5 lights.

### Render
- Speed: ~7 s of render per 1 s of video on software GL (6 s test → 42 s). Plan ~3–4 min for a 30 s video.
- Always `hyperframes render --output <slug>.mp4 --workers 2` (auto workers can stall on heavy WebGL). If it stalls or frames go black: `--workers 1`, lower triangle count, `antialias:false`.
- The notices "software gpu" and "Screenshot capture (slower)" are normal here.
- Lint warning `nested_structure_needs_subcomposition` is fine for short videos.
- Check smoothness (no frozen 3D): extract frames and diff neighbours — near-zero diffs mid-scene mean the scene isn't reading `t`:
```bash
mkdir -p fr && ffmpeg -v error -i <slug>.mp4 -vf scale=270:480 fr/%04d.png
python3 -c "
from PIL import Image,ImageChops,ImageStat;import glob;f=sorted(glob.glob('fr/*.png'))
d=[sum(ImageStat.Stat(ImageChops.difference(Image.open(a).convert('L'),Image.open(b).convert('L'))).mean) for a,b in zip(f,f[1:])]
print(len(f),'frames, frozen:',sum(x<.05 for x in d))"
```
  (Frozen frames during a deliberate still hold are fine.)

### Snapshot
`hyperframes snapshot` renders WebGL too — read the contact sheet as usual: 3D object not covering the headline, hero inside the safe zone, text readable over the 3D (add a dark CSS gradient scrim behind text if the object is bright).

### ttf2typeface.mjs (write this file into the project when 104 or any 3D text is needed)
```js
// Convert a TTF/OTF font into a Three.js typeface JSON (for TextGeometry), fully offline.
// Three's own TTFLoader imports opentype.js from a CDN (blocked in the sandbox), so this
// script copies it, points the import at the npm package, and runs it in Node.
//
// Run from the HyperFrames project folder (needs: npm i three opentype.js@1.3.4 --no-save):
//   node ttf2typeface.mjs /usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf assets/fonts/poppins_bold.typeface.json
import { readFileSync, writeFileSync, rmSync } from "fs";
import { resolve } from "path";
import { pathToFileURL } from "url";

const [, , input, output] = process.argv;
if (!input || !output) { console.error("usage: node ttf2typeface.mjs <in.ttf> <out.json>"); process.exit(1); }

const cwd = process.cwd();
const src = readFileSync(resolve(cwd, "node_modules/three/examples/jsm/loaders/TTFLoader.js"), "utf8")
  .replace(/https:\/\/cdn\.jsdelivr\.net\/npm\/opentype\.js@[^'"]*/, "opentype.js");
const tmp = resolve(cwd, ".ttfloader.node.mjs");   // inside the project so 'three'/'opentype.js' resolve
writeFileSync(tmp, src);
try {
  const { TTFLoader } = await import(pathToFileURL(tmp).href);
  const buf = readFileSync(input);
  const json = new TTFLoader().parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
  writeFileSync(output, JSON.stringify(json));
  console.log("wrote", output, Object.keys(json.glyphs).length, "glyphs");
} finally { rmSync(tmp, { force: true }); }
```