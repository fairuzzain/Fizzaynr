---
name: window-pass-through
description: Make a "window pass-through" transition shot - one continuous cinematic camera move that starts inside Image 1 and flies forward through a window, glass pod, doorway, porthole, reflection or other opening into a second scene, as if both exist in the same space - generated with Nexabot sfv (Image 1 = start frame, the destination written into the prompt), then delogoed, trimmed to the clean range and mixed with the bundled whoosh SFX timed to the moment the camera crosses the glass. Use when the user asks for a window pass-through / pass through effect, "masuk ikut tingkap", "zoom through the window into another scene", a seamless portal/glass transition between two images, the Higgsfield/Kling first-frame-to-last-frame transition look, or names /window-pass-through.
argument-hint: "[image 1] [image 2 or destination description] [9:16|16:9]"
---

# Window pass-through (Image 1 → through an opening → scene 2, one shot)

Source: a Kling 2.5 (Higgsfield) prompt guide + a pass-through whoosh SFX
(`assets/pass_through_sfx.mp3`, 9.6 s, sound 1.56–7.8 s, peak ≈ 3.0 s = the moment of passing through).
Prompts: `references/prompts.md` (read it - the guide's master prompt and its 10 variations).

**Nexabot has no start+end-frame mode** (checked GET /api/v1/modes on 2026-10-31: `sfv` takes 1 image).
So Image 1 is the start frame and the destination (Image 2) is **described in words** inside the prompt;
Veo draws scene 2 itself. One real continuous shot - never fake it by joining an Image 2 clip with a
code transition (the user rejected that approach; it was built once and deleted). If the user
needs scene 2 to match their Image 2 exactly, say so plainly: that needs a true first+last-frame model.

```
ROOT="$(git rev-parse --show-toplevel)"; set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a   # repo root + overrides
NB="${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"
S="$ROOT/.claude/skills/window-pass-through/scripts"    # system Python (cv2, numpy, PIL)
R="${RUNS_DIR:-$ROOT/runs}/window-pass-through/<slug>"               # one folder per shot
```
Always pass **absolute** `--out` paths to nexabot.ts. 0.15 credit per request; safety-filter rejections are refunded.

## 0. Brief (ask once, in Malay if the user writes Malay)
Get or default:
- **Image 1** - the user's photo, or generate it (step 1). It must contain a clear **opening to pass
  through**: window, glass pod (ferris wheel), doorway, car/plane/train window, porthole, shop glass,
  mirror, phone/TV screen, eye, bottle, keyhole. If it has none, pick a variation in `prompts.md` that
  fits (object-based, reflection, push-in) or suggest a better Image 1.
- **Destination** - Image 2 (look at it and describe it: place, light, time of day, palette, key
  objects, camera height) or a text description.
- Aspect: default **9:16** (`ratio 2`, Reels/TikTok); 16:9 → `ratio 1`.
- Several shots in a row (A → B → C)? Each hop is its own clip from its own start frame; the end of
  one clip can be the next start frame (step 5).
Do not ask about anything with a sensible default.

## 1. Start frame
- User photo: crop/scale to 1080×1920 (or 1920×1080) with ffmpeg, keep the opening fully in frame and
  roughly centred - the camera will fly into it:
  `ffmpeg -i in.jpg -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" $R\frames\start.png`
- No photo (ChatGPT image): `python "$ROOT/.claude/skills/codex-image/openai_image.py" --prompt "<scene with the opening as the clear focal point, no text>" --aspect 9:16 --width 1080 --out "$R/frames/start.png"`
  (`--aspect 16:9 --width 1920` for 16:9). If it fails twice, fall back to `bun $NB img "<...>" --aspect 5 --out ...` (aspect 2 for 16:9). Look at it; regenerate if the opening is small, cut off, or there is text.

## 2. Prompt → approval
Build the prompt from `references/prompts.md`: master prompt body + the camera path line (what the
camera flies toward and through) + the **destination description** + AUDIO + AVOID. One camera path,
one opening, forward only. Write it to `$R\clips.json`:
```json
[{"name":"pass","mode":"sfv","prompt":"...","ratio":2,"resolution":1080,"media":["frames/start.png"]}]
```
Show the user: the start frame, the opening and the camera path in one line, the destination
description, and the cost (`bun $NB batch $R\clips.json --dry` → 0.15 per clip). **Wait for approval.**

## 3. Generate (one test first)
`bun $NB batch $R\clips.json --parallel 1` → `$R\pass.mp4` (+ `nexabot-results.json`).
Then analyse it:
```
python $S\pass_through.py analyse $R\pass.mp4
```
This removes the Gemini ✦ watermark (`pass_clean.mp4`), writes a labelled 1 fps contact sheet
(`pass_sheet.png`) and a 4 fps strip around the most likely crossing (`pass_strip.png`), and prints
the top crossing candidates (biggest frame-to-frame change). **Look at both images** and decide:
- the crossing time (camera goes through the glass/opening),
- the clean range: Veo adds stray text/numbers or morphs after ~5–6 s - end before that,
- whether it worked. Retry once with a reworded prompt if the camera never reaches the opening,
  stops at the glass, cuts instead of travelling, or scene 2 is wrong (+0.15, tell the user). Typical fixes:
  name the opening's position in frame ("the lit pod in the upper left"), add "the camera passes
  through the glass without stopping", shorten the destination description to its 3–4 strongest details.

## 4. Finish (SFX on the crossing)
```
python $S\pass_through.py render $R\pass.mp4 --cross <s> --in <s> --len <s> [--veo-gain 0.35] [--sfx-gain 1.0]
```
Trims `pass_clean.mp4` to `[in, in+len]` at natural speed (no slow-down), places the SFX so its peak
lands exactly on `--cross`, mixes it over Veo's own sound (ducked to `--veo-gain`, 0 to mute), fades
the tail, and writes `$R\pass_final.mp4`. Keep at least ~1.5 s before the crossing so the move reads.
Check the result: extract 3 frames (before / at / after the crossing) and listen to where the hit lands.

## 5. Chains (optional, several hops)
For A → B → C, take the last clean frame of hop 1 as the start frame of hop 2:
`ffmpeg -sseof -0.1 -i $R\pass_final.mp4 -frames:v 1 $R2\frames\start.png`
(use the frame at the end of the clean range, not after junk). Each hop is still a real continuous
Nexabot shot; join hops with a hard cut on the matching frame - no faked transitions. Concatenate with
ffmpeg concat after rendering each hop's SFX.

## Delivery
Send `pass_final.mp4` (give its full path) and report: credits used, crossing time, clean range used,
and anything Veo got wrong in scene 2.
