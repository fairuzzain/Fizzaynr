---
name: vox-2
description: Vox 2 - Vox-style collage explainer rendered in code with Remotion, assets made with Nexabot. Turn any topic into a short Vox-style animated explainer video, end to end. Claude researches the topic, writes a fact-checked voiceover script, generates the narration and archival-style collage images, then renders a hand-made mixed-media animation (black-and-white halftone cut-outs, yellow paint blocks, ink notes drawn with p5.brush, grid paper, newspaper clippings, ransom-note type, stop-motion feel) to an MP4 with Remotion. Use for /vox-2, "vox 2", "vox collage", "collage explainer", "paper cut-out explainer". The Veo-clip diorama Vox stays /vox.
---

# Vox 2: collage explainer (Nexabot edition)

> Every image, voice and music request goes through Fizz's Nexabot client
> (`NEXA` = `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"`). Never use ElevenLabs.
> All global rules in `~/.claude/CLAUDE.md` apply: language lock, voice routing and voice lock,
> no captions, storyboard pre-approval, the 4 QA gates, the SFX pipeline, Drive sync, Editted-DDMMYYYY revisions and antislop (DURING mode).
> The Remotion engine draws all the motion, so this skill makes **no Veo clips**. Nexabot supplies only stills, VO and music.

The user gives a topic. You deliver a finished MP4 (1920x1080, H.264/AAC, default ~10 s) in the house collage style, plus the script and sources. The user should not have to do anything else: install, research, write, generate and render yourself, and only stop to ask when something genuinely needs their decision (for example, approving a download from a website, or spending a lot of credits).

## The look (why it works)

It is a paper collage animated by hand. On a dull warm-white board, a black-and-white photo or engraving is cut out with a thin white edge and a newspaper halftone dot screen, and slapped down on a painted yellow block. Black felt-pen notes circle and point at things, yellow highlighter swipes sit under key words, a grid panel and a clipped newspaper column sit behind, and big serif titles type on. The last beat lands on a ransom-note word. Everything moves "on twos", while the textures and line jitter move slowly, so it feels handmade rather than jittery. Yellow (#EDBD2E) is the only accent colour. Don't add orange or red, and don't use a dark background. The engine handles all of this; your job is the story, the pictures and where the notes point.

## Workflow

Paths below use `SKILL_DIR` = `$ROOT/.claude/skills/vox-2` and `VOX` for `python "$ROOT/.claude/skills/vox-2/scripts/vox.py"`.
Create projects in `${RUNS_DIR:-$ROOT/runs}/<Project Title>` (the local save location).

### 1. Set up (first run only)

Run `VOX doctor`. If anything is missing, run `VOX setup`. It installs the engine (Remotion, p5.brush, headless Chrome) and a Python venv into `~/.vox-2` and takes about a minute. It needs Node 18+ and ffmpeg (both are on this PC). Word timings use whisper.cpp if present, otherwise faster-whisper from the system Python (CPU here, because the CUDA cuBLAS DLLs are not installed), otherwise silence detection. The final encode runs on the GPU (`h264_nvenc`). On Windows, cut-outs use the colour-key path (Apple Vision is macOS only), so the plain backdrops in the image prompts matter.

Before the first Nexabot generation of the day, run `NEXA check` and then `NEXA credit`.

### 2. Research the topic

Use web search to find how the thing actually works. Aim for 3–5 solid sources: primary papers, university or agency pages, reputable journalism. Pick **one** surprising, concrete mechanism or fact that fits in the time. A good explainer answers a question the viewer already half-wonders about ("why can't you tickle yourself?"). Save notes with links to `<project>/research.md`. Every claim in the script must trace to a source. If a fact is contested, either say so or pick a different fact.

### 3. Write the script

- About 2.6 spoken words per second: 10 s ≈ 25 words in 4 beats, 20 s ≈ 50 words in 6–7 beats, 30 s ≈ 75 words in 9–10 beats. Default to 10 s unless the user asks for another length.
- One beat = one short sentence (one breath). Use a hook, then the mechanism, then a payoff that echoes the hook.
- Plain words. Name the key term once if it matters ("the cerebellum"). The final card credits the main source.
- Language lock: a Malay title means 100% Malaysian Malay (no rojak, no Indonesian words such as riset/durasi/bisa). An English title means 100% English. The lock covers the VO, every on-screen word, the labels, the ransom word and the source card.
- On-screen text here is design typography (titles, labels, notes, stat numbers). Never add a caption track that transcribes the VO.

### 4. Storyboard

Create the project with `VOX new <project> --title "<title>"`, then write `<project>/storyboard.json`. Read `references/storyboard.md` now for the beat types, every field and a complete example. In short:

| beat type | use it for | centre of the frame |
|---|---|---|
| `subject` | the hook, a person or object doing the thing | a cut-out photo on a yellow block, title column on the right |
| `diagram` | how it works inside (anatomy, machine, map) | an engraving on a yellow disc, with ink arrows, circles and labels |
| `chart` | a signal, a trend, before/after numbers | graph paper with a yellow highlight series and an ink series |
| `stat` | one striking number | ransom-note number on a yellow block, caption |
| `closer` | the payoff, usually last | a cut-out on yellow, beige sheet with headline + ransom word + source |

**Pre-approval gate (mandatory):** once the storyboard and the images (step 6) exist, render a layout draft with `VOX make <project> --draft`. Use a silent placeholder `public/audio/vo.mp3` of the planned length (`ffmpeg -f lavfi -i anullsrc -t <sec> ...`) if the VO is not made yet. Then present in an artifact: the script, a beat-by-beat table (type, line, cues, images, timing), the locked voice with rationale and tone, the image contact sheet and `out/contact.jpg`. Do not generate the final VO or music, or render the final, until Fizz says "approved" or "proceed".

Each beat's `line` must be exactly its sentence of the script, in order, because timings come from matching those words. Cues like `"cue": "cerebellum"` fire when that word is spoken. Images are listed per beat and generated next.

### 5. Voiceover (Nexabot TTS / Gemini TTS)

Lock one voice for the whole project from the genre matrix in CLAUDE.md (science or data: Charon/Leda; general explainer: Fola, which is Leda or Kore on Nexabot; history: Fenrir) and state it in the pre-approval artifact.

- **English:** `NEXA tts "<full script, all beat lines in order>" --voice <Voice> --out "<project>\work\vo.wav"` (0.15 credit, no tone option).
- **Malay:** `python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/gemini_tts.py" -t "<full script>" -v <Voice> -i "<tone>" -o "<project>\work\vo.wav"`. Send the whole script in one request (the free tier allows 10 a day). Write the pepet e as ë in the TTS text only (sëmpëna). The storyboard `line` keeps normal spelling.
- Use `...` for a beat pause. The spoken words must match the storyboard lines.
- Convert: `ffmpeg -y -i work\vo.wav -ar 44100 -b:a 192k public\audio\vo.mp3`.
- Listen for pronunciation (Malaysian Malay, no Indonesian drift). Set `VOX_LANG=ms` (or `en`) so faster-whisper aligns in the right language.

### 6. Images

Read `references/image-prompts.md` for prompt templates that cut out cleanly. Typically you need 1–2 **photos** (people, waist-up, plain grey studio backdrop), 1 **engraving** (the "inside" diagram) and 1 **props** sheet (2–3 small objects for decoration). Generate them with Nexabot at 16:9:

- New image: `NEXA img "<prompt>" --aspect 2 --out "<project>\work\src\<name>.png"` (0.15 credit).
- Same person or style as an earlier image (hook to payoff): `NEXA gpt-image "<prompt>" --media "<project>\work\src\<first>.png" --aspect 2 --out ...` (0.10 credit), with the identity-lock line from CLAUDE.md in the prompt.
- Several images: put them in an `images.json` batch (`"mode":"img"`) with the unique part of each prompt FIRST, and run it with `--parallel 1`. Run `--dry` first and state the count and cost. For a new look, make one test image and check it before making the rest.
- **Gate 2:** inspect every image (clear subject, plain backdrop, no stray letters or numbers, culturally right). Re-roll a bad one before cutting it out.

For each image:
1. Run `VOX grid <image>` and **look at the `_grid.jpg`** to read the source-pixel coordinates of the points you will annotate (face, hands, the part of a diagram you circle, where arrows start and end).
2. Cut it out:
   - `VOX cutout <project> <name> <image> --kind photo`. Add `--wiggle x0,y0,x1,y1 --pivot px,py` to cut a hand or small part as a separate piece that wiggles.
   - `--kind engraving` for illustrations on plain paper.
   - `--kind props --names a,b,c` for a sheet of objects, named left to right.
3. Put the points in the storyboard (source px, as read from the grid).

For a real historical figure, use a genuine public-domain photo (Wikimedia Commons, Library of Congress, Smithsonian Open Access), and **ask Fizz** before downloading it. Never generate real, identifiable people.

### 7. Render and check

Run `VOX make <project>`. It aligns the timings, lays out the scene, renders the p5.brush layers (cached, so only changed layers re-render) and writes the video. Use `--draft` for a fast half-resolution pass while iterating. Then **look at `<project>/out/contact.jpg`** and check:
- nothing important overlaps (titles vs subject, notes vs arrows), and no text runs off the frame;
- arrows and circles land on the right spot, and notes read in order with the voice;
- the yellow, black and warm-white palette holds.

- every on-screen word is spelled right (language lock, no typos), and there is no caption track.

Fix by editing points, cues or text in the storyboard and running `make` again. `VOX sheet <project> <frames…>` shows specific frames. Expect one or two passes.

**Sound.** The engine cues its own bundled paper, marker, typewriter and scribble Foley (`assets/sfx/`). Every *extra* sound (whoosh, hit, riser, ambience) goes through the SFX pipeline: `openverse-sfx` (check `${SFX_DIR:-$ROOT/assets/sfx}/<type>/` first), then `real-sfx` for placement and levels (`--voice-safe`), then `earshot` to judge the mix. For an optional music bed, run `NEXA music "<brief>"` (0.15 credit) and mix it under the VO with real-sfx `--duck`. Ask first if Fizz did not request music.

**Gate 4:** the voice sits clearly above the music and sound effects, key cues land on the spoken word, and the ending settles (hold the closer for 2–3 s, then fade picture and audio). If the closer ends abruptly, lengthen the last beat or add a trailing `...` to the VO.

### 8. Deliver

1. Upload everything to Google Drive with the gdrive CLI, never the browser connector: `python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/sync_gdrive.py" "<Project Title>" <files…>` puts them in `AI VIDEO / <MMM YYYY> / <Project Title>`. Upload the final MP4, vo.wav/mp3, music, storyboard.json, script.md, research.md, the source images and cut-outs, the contact sheets and images.json. If the upload is blocked, emit an Antigravity Handoff Ticket.
2. Send the MP4 with SendUserFile, along with the script, 2–4 source links and the Nexabot cost (img 0.15 each, gpt-image 0.10, TTS 0.15, music 0.15; Malay VO is free).
3. Put revisions in `Editted-<DDMMYYYY>\`, both locally and on Drive. Never overwrite the originals.

Offer an obvious next step, such as another length, a 9:16 version or a music bed.

## Good judgment calls

- **Fewer, bigger ideas.** One mechanism per video. If the research is rich, save the rest for a follow-up rather than cramming it in.
- **Real copy only.** Clipping text, labels and numbers must be true and sourced. Never invent a statistic to fill a `stat` beat. Use one from the research, or pick another beat type.
- **People and likeness.** Generated "archival" people are fictional. Don't generate images of real, identifiable people or brand logos. For a real historical figure, use a genuine public-domain photo (ask before downloading), or show their work or objects instead. In Islamic or Malaysian scenes, apply the cultural guardrails from CLAUDE.md Gate 1.
- **Points come from looking.** Always read coordinates off the grid image rather than guessing. A circle that misses the face looks broken.
- **When something looks off,** prefer changing the storyboard over editing engine code. The beat layouts are tuned. If you do change the engine, the source is in `engine/`, and `VOX setup` copies it into place (`~/.vox-2/engine`).

## Files

- `scripts/vox.py`: the CLI for everything above (`VOX -h`).
- `scripts/layout.py`: beat layouts, mapping storyboard to scene.
- `scripts/render_brush.mjs`: p5.brush layer renderer.
- `engine/`: the Remotion project that draws scenes.
- `references/storyboard.md`: the storyboard format with a full example (read before step 4).
- `references/image-prompts.md`: image prompt templates (read before step 6).
- `examples/tickle/`: a complete worked example (research, script, storyboard).
- `assets/sfx/`: paper, marker, typewriter and scribble Foley, cued automatically by the engine. Extra sounds come from the SFX pipeline.
