---
name: "logo-light-spec-ad"
description: "Build a premium code-only spec ad (Python + ffmpeg, no AI video) where one continuous light born from a brand's logo does every job, lands on beat and folds back into the logo."
---

# Logo-Light Spec Ad

A method for a ~20 s product spec ad rendered frame by frame in Python (numpy, OpenCV, Pillow, scipy) and piped into ffmpeg. One continuous film, zero hard cuts, no AI video, no stock footage. Reference build: keemfinity's Google Drive ad "Every file. One place." (21.8 s, 1920x1080, 60 fps, 1308 frames). Swap the product, keep the method.

## Core rules (never break)
1. **Find the idea inside the logo.** Split the logo into its parts (facets, letters, strokes, colours). Each part becomes one light, and each light does one product job. Drive: green saves, yellow finds, blue shares.
2. **One light does every job and never stops.** Hook lights, progress bars, focus lines, traces, strands, loops, races, writing light and end line are all the same light primitive.
3. **Record the voice first.** Then time each key word, not each line, to a picture beat.
4. **Put the logo on the song's own drop.** Offset the music so its biggest section change lands on the logo hit.
5. **Iterate cheap, render once.** Use half-res stills, then a half-res preview with the full mix, then contact sheets. Run the 1080p render only once everything is locked.
6. **Brand respect.** Use only the official logo (SVG). Move, scale, fade or mask it, but never redraw, recolour or distort it, and keep it pixel-exact at rest. Use fictional files, people and numbers, with no faces and no other brands. The end card says "Spec ad · not affiliated with [Brand]".

## Phases (get the user's approval before each next phase)
1. **Brief + beat sheet.** Logo idea, light-to-job mapping, script (roughly 8 short lines ending on the brand name), stage colour, palette from the official logo gradients, UI kit, and frame-exact times on the music grid.
2. **Voice.** 4 takes in one call. Transcribe them with word timestamps (faster-whisper), reject any take that repeats or drops words, then pick one and lock the key-word times.
3. **Assets.** Split the logo into layers, set up the font, and convert SFX to 48 kHz/16-bit. Ask the user for the music track and SFX library.
4. **Engine + scenes.** Build one shared timing file.
5. **Stills.** Render half-res stills at about 20 key moments onto a contact sheet, then fix.
6. **Preview.** Render a half-res full preview with the mix and a contact sheet with one frame every 0.5 s, then fix.
7. **Final.** Render 1080p60 in 60-frame segments with 2 workers, concat, mux AAC 320k, then check loudness and true peak.

What you need: Python 3 with numpy, opencv, Pillow, scipy, soundfile, pyloudnorm, cairosvg and faster-whisper, plus ffmpeg, the brand font, the official logo SVG, voice-over (English: Nexabot TTS; Malay: gemini_tts.py), a music track with a clear build and a big section change, and an SFX library (whooshes, risers, impacts, UI clicks, keystrokes). A 1080p frame takes about 3.5 s on one CPU core, so the final render is about 1 hour on 2 cores. A half-res still takes about 1 s.

## The light primitive
- Each light is a polyline from tail to head, drawn into a float light layer with anti-aliased `cv2.line(..., cv2.LINE_AA, shift=4)` and per-vertex intensity.
- Each light travels a **cubic Bézier**. The head is an eased `u`. The visible tail covers 28-42% of the path with intensity `w**2`, so it fades out behind the head.
- **Curves, not spirals.** Never use spirals or constant-radius circles, because they read as artificial.
- Hand-overs change colour along the tail (A→B).
- Bloom: `B = L + blur(3) + 0.75*blur(12) + 0.5*blur(42)` (px at 1080p).
- **Rim light:** extract the logo's outer contour (`cv2.findContours`) and resample it to 900 points. The first lap takes 1.05 s with ease-out, then it runs at 0.32 laps/s forever. The tail is 22% of the perimeter, and its colour is sampled 40 px inside the edge.
- **Loop:** a rounded shape that echoes the logo (Chaikin x4, 1200 points). Lights sit evenly spaced and chase at about 0.62 laps/s over a 10% track. They pass behind objects: `L += L_loop * (1 - 0.9*obj_alpha)`.

### On a light stage, light is ink
Additive glow vanishes on white, so composite the bloomed light as coloured ink:
```python
mx = B.max(-1); mn = B.min(-1)
A   = 1 - np.exp(-2.3 * mx)                  # opacity from energy
hue = B / mx[..., None]                       # pure colour
sat = np.clip((mx - mn) / mx * 1.8, 0, 1)[..., None]
ink = slate**2.2 * (1 - sat) + hue * 0.82 * sat
img = img * (1 - A[..., None]) + ink * A[..., None]   # linear light; gamma 2.2 at end
```
Neutral light (particles, tracks) becomes slate. Never draw white cores or white flashes, because they turn grey on white. On a dark stage, plain additive glow is fine.

## Look
- Near-white stage (Drive used #FAFAFB) with pastel blobs that drift and breathe: 62% white + 38% scene colour, at 16% strength, with a +10% pulse on each hit. The tint follows whichever light is active.
- Use one typeface at weights 400/500/700, primary text #1F1F1F and secondary #5F6368.
- Rebuild the product UI by eye with fictional content: white cards, a #DADCE0 border and soft drop shadows.
- Finish with a 7% vignette, 0.5% grain and motion blur on anything that flies. Text holds still whenever it has to be read.

## Render order (per frame)
`render(t)`: pastel background → particle field (fast streaks toward camera before the slam, then a slow drift with bumps on hand-overs) → UI layer (premultiplied linear RGBA) → UI drop shadow (alpha blurred 16 px, offset 10 px, 13%) → composite UI → light layer as ink → camera breath (scale 1 ± 0.8%) → shake → vignette → gamma → grain.

## Beat sheet template (100 BPM, one bar = 2.4 s, downbeats at 0.60 + 2.4k)
| Time | Beat |
|---|---|
| 0.00-0.60 | **Hook.** Frame 0 is already moving. Particles rush the camera while the lights sweep in from three edges on soft Béziers (`u = 0.18 + 0.82*(0.35x + 0.65x²)`, `x = t/0.60`), each ending at the centroid of its logo part. |
| 0.60 | **SLAM** on downbeat 0. The logo appears; its parts punch inward and settle on a spring (6 Hz, ζ 0.35) while scale overshoots 1.10→1.00. About 140 shards fly off the rim (250-1400 px/s, drag e^-6t, 0.35-0.9 s life). Shake is 11 px, decaying over 75 ms. No flash. The rim light starts. |
| 1.1-2.1 | The logo slides into the lockup, and a light writes the wordmark along its baseline (left-to-right reveal, 40 px soft edge). |
| 2.6-3.0 | **Peel.** Light #1 leaves its part and lands on 3.00 as the start of scene 1's UI element. The lockup recedes and fades. |
| 3.0-8.1 | Scene 1 (job 1). Waves of objects are keyed to each key word. The drop at 7.80 lands the payoff line. |
| 8.6-9.3 | Hand-over: light #1 flies to scene 2, changing colour along its tail. |
| 9.1-11.0 | Scene 2 (job 2). The key word lands on its beat. |
| 11.0-14.0 | Push-in, then scene 3 (job 3) on a 3D-warped texture (homography). The tap or action hits on its key word. |
| 14.0-16.3 | Payoff scene: the lights chase a loop shaped like the logo, behind the devices or objects. |
| 16.3-17.4 | **Race.** Each light leaves the loop and races to its logo part (ease-in, power 2). The music breathes at 16.80. |
| 17.40 | **LOGO HIT** on downbeat 7: the same slam at 0.86x size with lighter shake and 70% of the shards. Lockup and wordmark follow, and the rim light keeps circling. |
| 19.35-19.80 | Everything fades, and the rim head becomes one dot that travels to the end-card line. |
| 19.8-21.8 | **End card.** The dot draws a 300 px line in the brand's colour thirds with a moving glint. "made by" (30 px, grey) sits over [name] (74 px, 500) with a 14 px rise, plus the small spec disclaimer. Fade from 21.45. |

## Voice-over
- Use a premium, lively read. A calm read sounds dull under music. Generate the whole script in one call; with gemini_tts.py set the tone in `-i` (upbeat, confident, warm).
- Works in any language, including Bahasa Melayu. Pick key words that carry stress and still land on beats.
- Cut lines at silences (−40 dB, ≥ 0.12 s). Trim to the first sound, with a 6 ms fade-in and 40 ms fade-out.
- **Place lines by key word:** `start = beat - word_offset`. Never time-stretch the voice; move the picture or the line instead.
- Voice chain: HPF 80 Hz, −2 dB @ 250 Hz, +3.5 dB @ 3.4 kHz, +4 dB shelf @ 7.5 kHz, comp 3:1 @ −24 dB (4/80 ms, +4 dB makeup). Set the voice to −15 LUFS.

## Music + sound
- Offset the track so its biggest section lands on the logo hit. The other downbeats then fall into place.
- Shape the music in four moves: airy under the hook, building from the slam, a groove on the drop, a short filtered breath before the hit, then full on the hit and ringing out under the end card.
- Ducking: −6 dB under each hit and −8 dB under every word (60 ms/300 ms), with extra dips under the payoff line and the brand name. The voice must sit ≥ 15 dB above the music in the 1-4 kHz band.
- **Every visible move gets a sound** (about 55-60 cues): the air whoosh from frame 0, a riser cut 15 ms before each hit, impact + sub + transient on the slams, a metallic ring under the rim light, a pitched keystroke per landing (0.8-1.25x, pan ±0.6), UI ticks and chimes, and whoosh-hits peaking exactly on the hand-overs.
- Master to −14 LUFS integrated and ≤ −1 dBTP. Re-measure after the AAC encode and add a limiter if it overshoots.

## Build notes
- **One timing file** feeds both picture and mixer: VO starts, key-word times, the object-wave schedule (landing time, kind, angle, radius and seed for each object) and the music grid. Every tick then hits its frame.
- Make sprites once with Pillow at 3x, then downsample with Lanczos. Animate them with ROI-only affine blits, and use one perspective warp for any 3D page.
- Rasterise the logo at 4x and downsample with Lanczos. For the slam, split its parts into layers under the original mask.
- Device screens must be **holes** in the frame sprite, or content behind them turns grey.
- A row growing into a page must keep the page's aspect ratio.
- If the VO changes after the scenes are built, map film time to the scene's design clock with a piecewise-linear table, and keep hand-overs on the real clock.
- Check every hand-over on a contact sheet before the long render.

```bash
ffmpeg -f rawvideo -pix_fmt rgb24 -s 1920x1080 -r 60 -i - -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p seg_NN.mp4
ffmpeg -f concat -safe 0 -i list.txt -c copy video.mp4
ffmpeg -i video.mp4 -i mix.wav -c:v libx264 -crf 18 -c:a aac -b:a 320k -movflags +faststart final.mp4
```

## Starting a new ad
Ask for the brand or product, script language, aspect ratio (16:9, or 9:16 for Reels, where all positions are rescaled), the name on the end card, and whether the user has music and SFX. Then present Phase 1 for approval before writing any engine code.