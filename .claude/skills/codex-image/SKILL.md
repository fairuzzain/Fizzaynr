---
name: codex-image
description: FALLBACK image engine. Images are made with Nexabot `img` by default (see global CLAUDE.md). Use this Codex CLI skill only when Nexabot cannot do the job - image-to-image edits or character/style consistency from a reference image, key/sprite sheets that need -Pad, or when Nexabot fails or the user asks for Codex. Saves verified PNGs on the user's ChatGPT login and keeps the calling skill's prompt, aspect ratio, filenames and folder.
---

> **Default is Nexabot, not Codex.** Plain text-to-image (posters, thumbnails, scene frames,
> start frames, b-roll stills) goes through
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" img "<prompt>" --aspect 1|2|5 --out <path>.png`
> (1 = 1:1, 2 = 16:9, 5 = 9:16; other ratios: generate the nearest and crop with ffmpeg).
> Use Codex below only for reference-based jobs (`-Reference`), `-Pad` key sheets, or when Nexabot fails.

# codex-image — image generation through Codex CLI

The user's own image engine. Codex CLI is installed at
`%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe` and logged in with their **ChatGPT
account**. Never switch it to a paid API key (`codex login --with-api-key`,
`OPENAI_API_KEY`) without the user's explicit consent.

## Generate one image

```powershell
powershell -ExecutionPolicy Bypass -File "$(git rev-parse --show-toplevel)\.claude\skills\codex-image\codex-image.ps1" `
  -Prompt "<full image prompt>" -Out "<absolute path>.png" -Aspect 16:9 [-Width 1920] [-Reference "<img1>","<img2>"]
```

- `-Aspect` — exact ratio the result is centre-cropped to (16:9, 9:16, 1:1, 4:5, 21:9, 3:4 …).
- `-Width` — optional final width in pixels (e.g. 1920 for 16:9, 1080 for 9:16).
- `-Reference` — reference/source images for image-to-image, character consistency, style
  match or edits. Pass the previous frame of the same character to keep it consistent.
- `-Pad auto` (or `-Pad "#00FF00"`) — fit the whole image and pad to `-Aspect` with the sheet's
  background colour instead of centre-cropping. Use for green/magenta key sheets and sprite sheets.
- Existing files are never overwritten (a `-2`, `-3` suffix is added) unless `-Overwrite`.
- Prints JSON `{Path, Width, Height, Bytes, Source}` on success; throws with Codex's last
  output on failure. Each call takes roughly 1–3 minutes — use a 600000 ms timeout.
- Several independent images: run them as parallel tool calls (or `run_in_background`),
  at most ~4 at once. Images that reference an earlier one must wait for it.

## Standing in for another skill's image connector

When a skill (rb-digital-video, vox-collage, omni-ugc, storyboard, carousel, explainer …)
says to call Magnific / Higgsfield / another image connector that is not connected here:

1. Do the skill's own work exactly as written (style choice, scene list, prompts).
2. For each image step, pass the skill's prompt **unchanged** to `codex-image.ps1`, with the
   skill's aspect ratio and the skill's output filename and folder. If the skill gives
   none, save into the project's `images/` folder with a descriptive kebab-case name.
3. Translate connector options: aspect/size → `-Aspect`/`-Width`; reference / init /
   character / style image → `-Reference`; "n variations" → n separate calls with
   `-2`, `-3` names. Negative prompts → append "Avoid: …" to the prompt.
4. Carry on with the rest of the skill using the saved PNG paths.
5. Tell the user once that images were made with Codex instead of the named connector.

Limits — say so instead of faking it:
- **Video, motion, lip-sync, upscaling beyond re-render, audio**: Codex cannot do these.
  If the skill needs Higgsfield/Magnific for video or upscaling, keep using that connector
  if it is connected; otherwise tell the user that step needs the connector.
- If the user explicitly names Magnific/Higgsfield and it is connected, use it, not Codex.

## RB Digital skills (rb-digital-video, rbdigital-parallax, rb-digital-poster, rbdigital-*)

These skills are managed on claude.ai (never edit their cached copies). Bridge them like this:

**rb-digital-video — Mode B (Flow).** Offer the user a third choice next to A/B:
`C) AUTO — aku generate gambar guna Codex terus, kau cuma bagi VO (atau guna VO free mode A).`
In B or C, write the skill's Flow prompts exactly by its `references/common.md` rules
(2x2 scene sheets / 4x4 sticker sheets **1:1**, backgrounds **9:16**, "no text", shared style
line), then instead of waiting for uploads generate each prompt with `codex-image.ps1`:
- sheets → `-Aspect 1:1 -Width 2048`; backgrounds → `-Aspect 9:16 -Width 1080`;
- save into the video's working folder as `sheet1.png`, `sheet2.png`, `bg1.png` …;
- "use sheet 1 as ingredient for sheet 2" → pass `-Reference sheet1.png` for sheet 2+, so
  recurring characters stay consistent;
- view each result; regenerate a sheet if panels overlap, gutters are missing or text appears.
Then continue with the skill's "Build when uploads arrive" steps on those files. The VO still
comes from the user (ElevenLabs mp3) or the skill's free edge-tts path — Codex makes no audio.
Run the full Mode B/C pipeline in the Code tab: the generated files and the skill's Python/ffmpeg
scripts are on the same PC there.

**rbdigital-parallax.** In its step 0 question set, add to the image line:
"Gambar: (a) aku generate terus guna Codex (default), (b) kau generate sendiri dari prompt aku."
On (a), write every prompt exactly by its `references/prompts.md` + §1 STYLE rules (same STYLE string,
character described verbatim, green/magenta key rule), then generate them here instead of waiting
for uploads, saved in the working dir under the skill's filenames:
- backgrounds `b1.png`… → 9:16 `-Aspect 9:16 -Width 1536` (16:9: `-Aspect 16:9 -Width 2688`);
- character sheets `c1.png`, `c2.png` → `-Aspect 16:9 -Width 2560 -Pad auto` (pad with the sheet's own
  key colour so full-body poses are never cropped); pass `-Reference c1.png` for `c2` (same character);
- fg sheets `f1.png`, `f2.png` → `-Aspect 16:9 -Width 2560 -Pad auto`;
- pass `-Reference b1.png` for later backgrounds so the craft style stays the same across scenes.
Up to 4 independent images in parallel (all bgs + c1 + f1 at once; c2 after c1). Then continue with the
skill's step 4 (keyout.py) and open every `_contact.png`; regenerate an image if the key colour is not
flat, poses touch, text appears, or the style drifts (Codex leans 3D: repeat the STYLE words). Tested
2026-10-30: a Codex green sheet keys cleanly with `keyout.py --key green --split x`. Needs `scipy`
(`python -m pip install scipy`). VO still comes from the user's ElevenLabs MP3.
Lessons from the first full video (2026-10-30, "kuih"):
- Nothing green on a green-key character sheet: green kuih / pandan / leaves held by the character
  were keyed out as holes. Say "nothing green on the character or props" and name the allowed colours.
- For the character sheet pass `-Reference b1.png` and say "flat 2D layered paper cut figure … NOT a 3D
  render, not clay" — without it Codex drew a 3D-looking character.
- Windows: the skill's `render.py` uses `multiprocessing` "fork" (Linux only) and crashes. Don't edit the
  skill; run it through a wrapper in the working dir that swaps in a thread pool:
  `import sys,os,runpy,types,multiprocessing; from multiprocessing.pool import ThreadPool;`
  `multiprocessing.get_context=lambda m=None: types.SimpleNamespace(Pool=ThreadPool);`
  `s=sys.argv[1]; sys.argv=sys.argv[1:]; sys.path.insert(0,os.path.dirname(s)); runpy.run_path(s,run_name="__main__")`
  → `python render_win.py <S>\render.py scenes.json` (15 s rendered in ~8 s). `--preview` works directly.
- In PowerShell, pass `vo_args.txt` to mix.py as separate args: `$va=(Get-Content vo_args.txt -Raw).Trim() -split ' '` then `@va`.

## vox-collage-explainer (anthropic-skills:vox-collage-explainer)

Its step 6 asks for ElevenLabs `creative_generate_image`. Use Codex instead (no credits), with the
prompt templates from its `references/image-prompts.md` unchanged, 16:9:
`-Aspect 16:9 -Width 1920 -Out <project>\work\src\<name>.png`. Photo, engraving and props can
run in parallel. A second photo of the same person → `-Reference <first photo>`.
On Windows, vox has no Apple Vision and cuts photos with a colour key. A grey studio backdrop
then eats the face and hands, because skin is the same grey. Tested 2026-10-30 fix: after the
photo, run one edit pass with `-Reference <photo>.png -Out <name>-green.png` and the prompt
"Edit the attached photo: replace only the grey studio backdrop with a perfectly flat, even, solid
pure chroma-key green (#00FF00) background … keep the man exactly the same … fully black-and-white,
no green spill", then `cutout --kind photo` on the green file (the cut-out is grayscale, so the
green never shows). Engravings (cream paper) and props (white background) cut cleanly as they are.
The skill's cut/grid/new commands run with the system Python (numpy, opencv, pillow are installed):
`python <skill>\scripts\vox.py new|grid|cutout …`. Always open the cut-out PNGs to check them.

**rb-digital-poster.** After the skill outputs its poster prompt code block, ask once
"Nak saya terus generate poster ni guna Codex?" (or do it straight away if the user already
asked for the poster image). Generate with the prompt unchanged, at the ratio the skill chose
(default 4:5, width 1080), save in `images/` (or `Documents\Gambar AI`), and pass any product
photo the user gave as `-Reference` so the real product is kept.

## After generating

Verify the PNG (the script already checks signature and size), view it with Read, and show
the user the path. Send finished images with SendUserFile when they asked for them.
The `voicestudio` MCP error (`127.0.0.1:3900`) in Codex logs is unrelated noise.
