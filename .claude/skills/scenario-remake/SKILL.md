---
name: scenario-remake
description: Use when someone has a short reference video (a faceless vertical short, a what-if simulation with a climbing counter, a ranking reveal, a how-it-works explainer, a character skit or an attention-hook ad) and wants the same format with their own idea, made through Scenario MCP. Claude measures the reference second by second, maps its concept onto the new idea, writes a per-second plan and gates it for logic and entertainment, prices it with dry runs, then makes keyframes, video shots, music, voice and sound effects with Scenario models, draws every caption, counter and label in code, and audits the final cut frame by frame. Triggers include remake, recreate, reverse engineer, "same format but about X", "make one like this for my idea", or a shared short video with a new topic.
---
> [!IMPORTANT]
> **Mandatory Google Drive Sync Across All Video Skills**:
> Every video generated (AI video, music video, commercial, explainer, reel, story clip, reverse video, or motion graphic) MUST be organized and uploaded to **Google Drive** immediately upon generation/assembly.
> 
> **Hierarchy Structure:**
> `AI VIDEO` -> `<MONTH YYYY>` -> `<PROJECT TITLE>` (e.g. `AI VIDEO` -> `NOV 2026` -> `<PROJECT TITLE>`)
> 
> **Required Folder Assets:**
> - Final rendered/assembled video(s) (master MP4, compressed versions)
> - Source clips, assets, and raw recordings
> - Audio / VO files (`.wav`, `.mp3`)
> - Subtitle/caption files (`.ass`, `.srt`, `.json`)
> - Prompt manifests, batch files, and storyboard contact sheets
> - Generation / assembly scripts (`.py`, `.ts`, `.js`, `.html`)
> 
> **CLI Upload Commands:**
> `gdrive mutate mkdir "<PROJECT TITLE>" --parent <MONTH_FOLDER_ID>`
> `gdrive mutate upload "<FILE>" --parent <PROJECT_FOLDER_ID>`

# Scenario Remake

## Overview

One reference in, one new video out: the same concept, storytelling and style, a new idea. Claude
reads and measures the reference, maps it onto the idea and writes each second. Scenario MCP makes
the generated pixels and sound; code builds whatever must be exact; `scripts/build.py` draws the
text layer and cuts the master.

Four rules make it work:
- **Analyse until you could rebuild the reference blind.** The concept, why each second holds
  attention, and the style in numbers. Shallow analysis gives a remake that looks similar and
  plays empty.
- **Copy the format, change the idea.** Keep the skeleton, the beat rhythm, the camera grammar,
  the type and the sound bed. Describe the style in words. Never upload the reference's frames to
  a model, never copy its caption lines, never name its creator.
- **Each second is logical and entertaining.** Run the gate in
  [logic-gate.md](references/logic-gate.md) on the plan, on each asset and on the final. A morph,
  a re-spawn or a dead second is a bug.
- **Models never draw text.** Each title, number, caption and label is drawn in code. Prompts say
  "no text, no captions, no numbers, no UI, no logos".

Two gates come before any spend: the plan with its dry-run price, then the keyframe board. Wait for
a go at each.

## Quick reference

| Step | What | Credits | Output |
|---|---|---|---|
| 1 Deconstruct | `scripts/breakdown.sh`, read every second | none, local | `ref/`, `analysis.md` |
| 2 Map the idea | concept map, facts checked | none | `concept.md` |
| 3 Per-second plan | t, words, picture, camera, graphics, sound, tool | none | `concept.md` |
| 4 Logic gate, pass 1 | plain-sentence log, then the text layer | none, local | `logic.md`, `episode.json`, stills |
| **Gate 1** | **plan + dry-run price, wait for a go** | dry runs only | |
| 5 Keyframes | style frame, then edits of it | yes | `keyframes/` |
| **Gate 2** | **keyframe board, wait for a go** | | |
| 6 Shots | first and last frame chained, drafts first | yes | `clips/` |
| 7 Sound | music bed, voice lines, sound effects | yes | `audio/` |
| 8 Edit in code | `build.py` | none, local | MP4 + contact sheet |
| 9 Final frame audit | gate pass 3 on extracted frames | none, local | `logic.md` complete |

Scenario MCP calls used: `recommend` or `search` (pick a model), `model_schema_get` (its exact
parameters), `model_run` with `dry_run: true` (price), `model_run` with `wait: false` (start a
job), `jobs_wait` (up to 32 jobs), `asset_download` (a URL per asset), `upload_asset` and
`upload_asset_complete` (only for files that exist only on disk).

## Work folder

```
<work>/ref/          breakdown.sh output (sheets, full-res frames, measure.txt, transcript)
<work>/analysis.md   the deep read of the reference
<work>/concept.md    the concept map and the per-second plan for the new idea
<work>/logic.md      the gate log: one plain sentence per second, pass or fail, fixes
<work>/episode.json  the edit: timeline, text layer, clip and audio paths
<work>/keyframes/  <work>/clips/  <work>/audio/   generated assets
<work>/runs.md       one line per Scenario job: what it was, the asset id, the cost
```

## The method

**1. Deconstruct the reference (local, no credits used).**
`scripts/breakdown.sh <file or URL> <work>/ref` writes one frame per second, contact sheets,
full-resolution frames at each cut, `measure.txt` (camera motion, palette, caption boxes, pace,
sound levels) and a transcript when a local Whisper is installed. Read every sheet in order, then
the full-res frames. Fill `<work>/analysis.md` from
[read-the-reference.md](references/read-the-reference.md): the concept in one sentence, the
topic-neutral skeleton, why it entertains (with open-loop plant and payoff times), a per-second
table, the world rules, the measured style spec, what a new topic must satisfy, and the production
read. Name the engine from [story-engines.md](references/story-engines.md). Do not go on while any
second of the reference is unaccounted for.

**2. Map the idea.**
In `concept.md`, a two-column map: each skeleton beat and style element of the reference, and its
counterpart in the new idea (premise, hero, counter, world, twist, ending question). An element
with no counterpart is cut on purpose, with the reason written down, or the idea does not fit. If
the user has no idea, or it fails a constraint, offer three that pass and recommend one. Every
fact and number is true: check public sources and note each one next to its beat, or label the
film hypothetical in the footer.

**3. Write it per second.**
t | voice or caption | picture | camera | graphics | sound | build or generate. Match the
reference's pace from `measure.txt` (words per second, a new fact every n seconds, holds and
moves). Fix the weak spots in the upgrade checklist of
[story-engines.md](references/story-engines.md#upgrade-checklist): trigger by 8 s, a counter that
never dies, one hero in one strong colour, a question at the end.

**4. Logic gate, pass 1, then the text layer.**
Write `logic.md`: one plain sentence per second. Check each against the logic and entertainment
rules in [logic-gate.md](references/logic-gate.md) and assign each beat the right tool:
measurements, rankings, exact growth, rule-following traffic and moves between places are built,
not generated. Fix the plan until each second passes. Then write `episode.json`
([episode.md](references/episode.md)) and check the text before any picture exists:
`python3 scripts/build.py <work>/episode.json --plan`, then `--stills 1,8,20 --show-zone`, then
`--preview` for a full-length text animatic over grey.

**Gate 1: plan and price.** Find each model, read its schema, and `dry_run` the exact jobs: the
keyframes (with retakes), each shot, the music, each voice line, each sound effect. Show the
concept map, the per-second plan with its tool per beat, the style in words, the total price from
the dry runs and the time. Spend nothing before the user says go.

**5. Keyframes.**
Keyframe 1 is the style frame, 9:16, with the hero in it. Each later keyframe is an edit of
keyframe 1 (passed as a reference image: "same world, same style, same camera: later, ..."), so
the world and the hero hold. One keyframe per shot boundary. Ask for 2 to 4 outputs of keyframe 1
and pick. Check each against the logic rules (gate pass 2): an object that has left the story must
not be in any later keyframe, or the video model brings it back.

**Gate 2: the keyframe board.** Show all keyframes side by side and wait for a go before any video
spend. Optional: point `clips` at the keyframe images (each with `dur`) for a still animatic.

**6. Shots.**
One shot = one continuous camera action. Group the beats that share a world and a camera move into
one shot and write them as timecoded beats inside one prompt ("0-5s: ..., 5-9s: ..."), named as
one continuous take. Chain shots: `image` = keyframe N, `lastFrameImage` = keyframe N+1, so each
shot ends where the next begins. Say what moves, the one camera move, the physics, and the no-text
line. Keep the HUD and caption areas calm (sky, floor, dark). Turn the model's own audio off: music
and voice are laid in the edit. Run each shot as a draft first if the model offers one, review it
against the logic rules, then finalise the picks. Start all shots of an episode together with
`wait: false` and wait on them with one `jobs_wait`.

**7. Sound.**
Match the reference's measured sound: voice pace, the bed level under the voice, and a sound effect
on each event. Music: one instrumental bed for the whole video, never a score per shot. Voice: one
text-to-speech run per beat line (`audio/vo01.mp3`, ...); `build.py` fits each beat to its line
and ducks the music under it. If a line runs long, rewrite and regenerate it; never speed the audio
up. Sound effects: generated through Scenario, never synthesised in code. A music-only engine has
no voice.

**8. Edit in code.**
`python3 scripts/build.py <work>/episode.json` writes `episode.mp4` and a contact sheet: the clips
in order, the text layer, the mix normalised to -14 LUFS. It never overwrites without `--force`,
never writes over one of the episode's own files, stops on a missing clip, ends each beat exactly where the next starts, and names any text that
leaves the Reels safe zone.

**9. Final frame audit (gate pass 3).**
The contact sheet is not the check. Extract the final at 2 fps or more
(`ffmpeg -i episode.mp4 -vf fps=2 audit/%04d.png`, denser around each move and reveal), look at
each frame at full size, and write the plain-sentence log from the frames, not from the plan. Check
each second against the logic and entertainment rules, the safe zone, counters landing on the right
values, and stray text or logos. Put the reference and the remake side by side at the same seconds:
pace, camera, type and sound should match. Fix each failing second before handover. Hand over the
file, `logic.md`, the cost total from `runs.md`, and three next ideas that pass the same
constraints.

## Worked example: film 10 Strike

Film 10 of Scenario's Content Engine: "What if lightning struck one metre from you?" 30 s, 9:16,
engine A (what-if simulation, music only). A low-poly hilltop under a storm, a lone tree, one
person in a yellow raincoat with a black umbrella. COUNTDOWN 5 to 1, then EVENT CLOCK (slow
motion) with AIR TEMP to about 28,000 °C, then FLASHES ON EARTH at 44 per second. Ends on "How close have
you been?" The edit is [strike.episode.json](examples/strike.episode.json) and each generation job
with its parameters is in [strike.jobs.json](examples/strike.jobs.json). Asset and model ids below
are placeholders.

**Pick the models.** The recommended route is `recommend`, which ranks models for one job:

```json
recommend {"capability": "img2img", "prompt": "Edit a stylised low-poly 3D keyframe from a reference image, keeping the same world, style and camera", "features": ["referenceImages"], "limit": 3}
recommend {"capability": "img2video", "prompt": "9:16 shot that runs from a first frame to a last frame, one continuous take", "features": ["lastFrameImage"], "limit": 3}
```

When you already know the model family, `search` finds it by name, which is how the Content
Engine found its models: `search {"target": "models", "query": "<family> sound effects", "public": true}`.
The answer is whatever the catalogue holds that day (for example, `recommend` may return a Gemini
image editing model for keyframes and a Seedance model for first-and-last-frame shots); none of it
is a requirement. Then read the exact parameters, which differ between models:
`model_schema_get {"model_id": "<video model id>"}`.

**Price it (gate 1).** `dry_run` returns the cost without creating a job:

```json
model_run {"model_id": "<video model id>", "dry_run": true,
  "parameters": {"prompt": "...", "image": "<keyframe 1 asset id>", "lastFrameImage": "<keyframe 2 asset id>",
                 "duration": 9, "aspectRatio": "9:16", "draft": true, "generateAudio": false}}
```

The Content Engine dry-ran one job of each kind (a shot, the music, a voice line, a keyframe) and
priced the whole shot plan from the per-second rate, with a buffer for retakes. Pricing each exact
job is more accurate; show the total with the plan.

**Keyframe 1, the style frame, two outputs:**

```json
model_run {"model_id": "<image model id>", "wait": false, "parameters": {
  "prompt": "Stylised low-poly 3D illustration, vertical 9:16, a grassy hilltop under a towering dark violet-grey thunderstorm cloud that fills the upper half of the sky. A single big oak tree stands on the right of the hill. In the middle of the frame, a person in a yellow raincoat holding an open black umbrella stands with their back to the camera, facing the storm. [...] the yellow raincoat is the only saturated colour. Locked wide camera at eye level. No lightning yet. No text, no logos.",
  "aspectRatio": "9:16", "resolution": "2K", "numOutputs": 2}}
```

The second output was picked. Keyframes 2 to 5 are edits of it, one output each (the leader
descends; the strike; the aftermath with the hero crouched alive; the night side of Earth from
space):

```json
model_run {"model_id": "<image model id>", "wait": false, "parameters": {
  "prompt": "Same hilltop, same low-poly style, same locked camera and framing as the reference. The lightning bolt strikes the oak tree: a blinding white-violet bolt from the cloud into the tree, everything lit flat bright white-blue, a visible ring of shockwave rippling through the air around the tree, sparks and bark flying; the person in yellow flinches. No text, no logos.",
  "referenceImages": ["<keyframe 1 asset id>"], "aspectRatio": "9:16", "resolution": "2K", "numOutputs": 1}}
```

**Gate 2.** The keyframes were shown as one board, and no video was run before the go.

**Four shots, chained through the five keyframes** (9, 4, 7 and 7 s), all started at once:

```json
model_run {"model_id": "<video model id>", "wait": false, "parameters": {
  "prompt": "Same locked camera, one continuous take.\n0-2s: thin sparks rise from the tree, the grass and the umbrella tip to meet the descending zigzag.\n2-4s: a blinding white lightning bolt strikes the tree, a bright ring shockwave bursts outward, sparks and bark fly, the person flinches. No text, no captions, no letters, no numbers, no UI, no logos, no watermark.",
  "image": "<keyframe 2 asset id>", "lastFrameImage": "<keyframe 3 asset id>",
  "duration": 4, "aspectRatio": "9:16", "draft": true, "generateAudio": false}}
jobs_wait {"job_ids": ["<s1 job>", "<s2 job>", "<s3 job>", "<s4 job>"]}
```

Only the last shot moves the camera, rising into space for the scale line; the other three are
locked. Keyframe asset ids go straight into `image` and `lastFrameImage`, so Strike needed no
upload. The 480p drafts were used as the finals for the web page. At the time of the build, finalising a draft was a button on the asset page of the Scenario web app, not an
MCP call.

**Sound.** One music bed ("dark tense cinematic storm score ... a ticking countdown pulse that
tightens for fifteen seconds, then a sudden cut to near silence, then a slow, awed, ringing
aftermath", instrumental) and two sound effects: an extremely close lightning strike, and a
looping rain ambience. In the edit: rain at 0 s (-15 dB), the strike at 11.4 s (-2 dB), rain again
at 19 s (-17 dB). No voice. The sound was made before the shots.

**Download.** One `asset_id` per call; follow redirects when saving:

```
asset_download {"asset_id": "<s2 output asset id>"}
curl -sfL -o <work>/clips/s2.mp4 "<url from asset_download>"
```

**When a file exists only on disk.** For film 11 Magnet, two frames pulled out of generated clips
became the first and last frame of a retake. Upload a local file with the multipart route:
`wc -c < frame.png` for the size, then
`upload_asset {"file_name": "frame.png", "content_type": "image/png", "kind": "image", "file_size": <bytes>}`,
PUT each part to its presigned URL as the reply instructs (for example
`curl -X PUT -T frame.png "<url>"`, with the full URL and no checksum headers), then `upload_asset_complete {"upload_id": "<upload id>"}` returns the asset id. (That
retake brought the pulled car back again; an impact cut plus a clean-plate patch from the same clip
fixed it. See [logic-gate.md](references/logic-gate.md).)

**Edit and audit.** `build.py` drew the countdown with a jump label per number, the event clock on
an exponential curve beside the air temperature, a white flash on the strike, and the end card.
The Content Engine's final check was a contact sheet, full-size spot checks and a logic pass per
film. That missed a one-frame fault in film 07, which is why step 9 now reads extracted frames.

## Common mistakes

From our own films; details and fixes in [logic-gate.md](references/logic-gate.md).

- **Morphs.** A boy lunges off a light switch and lands seated at a desk, the switch turning into
  the chair (03 No Sleep). A change of place is a cut or a visible move.
- **Re-spawns from later keyframes.** A car pulled away reappears parked on the road because a
  later keyframe still held it (11 Magnet). Edit a departed object out of each later keyframe, or
  chain from the real last frame with no `lastFrameImage`.
- **Generated traffic or crowds that must follow a rule.** A zipper merge rendered as grey cars
  sliding through each other while the lane line dissolves (06 Zipper). Build rule-following motion
  in code or 3D, or show it as a diagram.
- **Cross-faded caption text.** A status read "Signedd" for one frame because two strings were
  drawn on the same frame (07 Tap). Hard-switch text; `build.py` now ends each beat where the next
  starts.
- **Text under the platform UI.** Counters, labels and pills ran into the Reels buttons and
  caption area (ranking film, first cut). Keep text inside x 65 to 1015, y 269 to 1248, and clear
  of x 853 and over below y 1152 on 1080x1920; check with `--show-zone`.
- **Caption drift after tightening the voice with crossfades.** Captions ran up to 0.4 s late
  (ranking film, first cut). Cut only inside measured silences, as hard cuts, then check each word
  against its caption.
- **Passing a one-frame fault from a contact sheet.** The 07 frame was first passed as fine. Read
  the extracted frames at full size.
- **Letting a model draw text, or feeding it the reference.** Text comes from `build.py`; the
  reference is described in words, never uploaded.

## Before you hand it over

- `analysis.md` covers each second of the reference; `concept.md` maps each element.
- `logic.md` has one sentence per second of the final, all passing.
- The hook lands in the first 3 s, readable in one second.
- Each number is sourced, or the footer says the film is hypothetical.
- Same concept, storytelling and style as the reference; only the idea is new.
- Nothing from the reference itself: no frames, footage, names, handles or exact caption lines.
