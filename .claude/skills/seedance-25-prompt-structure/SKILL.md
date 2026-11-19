---
name: "seedance-25-prompt-structure"
description: "Structure every Seedance 2.5 video prompt (text-to-video, references, first/last frame, keyframes, editing, extension, storyboards, transitions) using the official best-practice templates and checklist."
---

# Seedance 2.5 Prompt Structure

Whenever a prompt is destined for Seedance 2.5, do NOT write a free-form cinematic
paragraph. Build the prompt with the structures below. These rules improve
instruction following, material consistency, and controllability — they are the
official best practice for this model.

## 0. Workflow when this skill activates

1. Identify the task type: text-to-video, reference-based creation, first/last-frame,
   multi-keyframe, video editing, video extension, one-click video, or seamless
   transition. Each has its own template below — pick the right one.
2. Inventory the reference materials the user has (or needs): images, videos, audio.
   Every material MUST get an explicit role line in the prompt.
3. Draft the prompt using the matching template.
4. Run the pre-submission checklist (section 10) before delivering.
5. Deliver the prompt to the user, then (if generation is available) offer to run it.

## 1. The Core Prompt Formula

Combine flexibly; omit what is not needed. Generation parameters (duration, aspect
ratio, resolution) are NOT written in the prompt — they are set on the generation
page or API.

```
Subject + Action or Event + Scene and Environment (opt) + Visual Style (opt)
+ Camera Movement/Cut (opt) + Audio (opt)
```

Basic template:

```
<Subject> performs <primary action or event> in <scene and environment>.
The visuals feature <visual style>.
Use <shot size, camera angle, camera movement, or cuts>.
Audio includes <dialogue, ambience, sound effects, or music>.
```

## 2. Reference Materials: Roles and Limits

### Limits (recommended ranges improve stability; they are not hard capability caps)

| Material | Input limit | Recommended |
|---|---|---|
| Images | up to 30, each ≤4K | 1–8 distinct subjects across subject-reference images |
| Videos | up to 10, combined ≤30s | 1–5 distinct subjects, 5–10s per subject video |
| Audio | up to 10 clips, combined ≤30s | only clips directly relevant to the task |
| Editing | source video + reference images | source <20s, 1–5 ref images |

Up to 50 total reference materials. If a subject needs multiple views, put each view
in a SEPARATE image (independent view images beat collages) and state explicitly:
"All N images define one <subject>. The output must contain only one <subject>."

### Define every material's role — mandatory

Never rely on text labels inside images or make the model infer mappings. Bind each
material individually, and add exclusions for anything that could leak in:

```
@Image 1 defines <subject>'s <appearance, clothing, structure, or material>. Do not use the image background.
@Video 1 defines <motion, camera movement, or pacing>. Do not use the person's identity, clothing, or scene from the video.
@Audio 1 defines <character or sound type>'s <voice, dialogue, ambience, or music>.
```

Never write "@Images 1 through 4 define four characters respectively" — that does not
state which image maps to which character. One binding line per subject.

When a reference video already defines motion/camera/sequence accurately, state only
which attributes to inherit — do NOT restate every action (repetition can conflict
with the reference).

## 3. Special Syntax for Audio and Text

Natural language works, but use this syntax to disambiguate:

| Content | Syntax | Example |
|---|---|---|
| Music | `()` | (Soft, rhythmic piano music plays in the background) |
| Sound effects | `<>` | <A bell rings in the distance> |
| Dialogue | `{}` | {Hello, welcome back.} |
| Subtitles | `【】` | 【Chapter One: Departure】 |

Dialogue language reinforcement (when dialogue is not Chinese, or drifts language):

```
Dialogue language + regional variety/accent + delivery style + speaker + {line}
Dialogue language: American English. The girl says in natural, conversational American English: {I thought you weren't coming.}
```

## 4. Multi-Reference Creation (many materials)

Order: Define roles → Map subjects → Group by type → Subject profiles → Select by scene.
The goal is to help the model pick the correct materials per scene — NOT to make
every material appear at once.

1. **Name and map each subject individually** (one line per person/prop/scene, with
   "use only ..." and exclusions).
2. **Group by type** with headers: `[Characters]`, `[Props]`, `[Scenes]`,
   `[Motion and Audio]`. Add: "Do not interchange the characters' appearances,
   clothing, actions, positions, or dialogue." Bind prop ownership
   ("<Prop A> belongs only to <Character A>").
3. **Subject profile** for any important recurring subject:

```
[Subject Profile: <Name>]
Appearance and clothing: @Image N.
Fixed prop: <Prop> from @Image M.
Locations: <Scene list>.
Motion references: <@Video refs>.
Do not use: <other characters' clothing / props that don't belong to them>.
```

4. **Select references by scene**:

```
Scene 1 | <title>
Use: <subjects, props, scenes, motion refs used in THIS scene only>.
Event: <one primary event>.
End state: <visible positions/ownership at scene end>.
```

## 5. Long Videos (multi-event, up to 30s): Stages with End States

One primary state change per stage. Every stage states what is DIRECTLY VISIBLE at
its end. This is the default structure for any narrative video:

```
[Generation Goal]
Generate a <video type>. The central subject is <subject>, and the primary event is <story summary>.

[Stage 1]
Initial state: <characters, props, scene>.
Primary event: <ONE primary action or event>.
End state: <character positions, prop ownership, visible scene state>.

[Stage 2]
Continue from the previous stage: <state that must remain unchanged>.
Primary event: ...
End state: ...

[Maintain Consistency]
Keep <character identity, number of characters, clothing, prop ownership, spatial direction, audio relationships> consistent.
```

### Timestamps and pacing

Stages by default; one-second precision ONLY for critical handoffs, entrances/exits,
transitions, or explicit beats.

- Time range (budget, not edit point): `0–3 seconds ... 3–7 seconds ...` — consecutive, non-overlapping.
- Exact point: `At 5 seconds, the camera whip-pans rapidly to the left.`
- Relative: `Three seconds after the character presses the button, the lights turn off.`

Do not demand frequencies ("three actions in one second"). Too little content in a
range = model freedom; too much = excessive cutting or dropped events.

## 6. Task-Specific Templates

### 6.1 Auto-locked parameters

| Task | Aspect ratio | Duration |
|---|---|---|
| Video editing | locked to input video | locked ≈ input (±~0.3s) |
| First/last-frame | locked to first image (first+last must share ratio) | settable |
| Extension | locked to input video | settable |

### 6.2 Video editing — master, scope, preserve

```
[Edit Goal]
Edit @Video 1. Within <whole video or time range>, <add/remove/replace/adjust> <object, region, or audio category>.
[Source Video Role]
@Video 1 is the sole editing master. It defines <characters, scene, actions, composition, camera movement, occlusion, audio, event order>.
[Target Material Role]
@Image 1 / @Audio 1 defines <specified attributes only>. Do not use <irrelevant background, people, composition>.
[Edit Scope]
Modify only <object/region/time range/audio category>.
[Content to Preserve]
Keep <everything that must not change> from @Video 1.
```

**Subject replacement** adds a quantity line ("The entire video contains <N> target
object(s)") and a `[Timeline Inheritance]` block: the target inherits every
appearance, motion, occlusion, and exit of the original — timing, duration, path,
speed. Close with: "Except for the object or area explicitly modified above, keep
all other people, props, scene content, camera movements, cuts, and event order from
@Video 1 unchanged."

**Background replacement**: replace only the background outside the subject's
silhouette; the image ref provides only spatial layout, materials, depth of field,
ambient color, lighting direction; never modify subject identity/face/hair/clothing/
expression/position/size/motion.

**Audio editing**: edit dialogue, language, voice, music, SFX separately — state the
speaker or sound category, the change, and every other sound that must stay.

### 6.2b Mandatory Identity & Feature Lock (The Face Codes)

When editing or animating characters where face, identity, or key features must NOT change ("sekiranya tak nak berubah apa pada wajah, karektor or anything"):
- Always include the **Identity Lock** directive in `[Content to Preserve]`:
  `Identity lock: keep [character/subject]'s face and features exactly as in @Image 1 / @Video 1. Same face shape, eyes, nose, mouth, skin tone, hairline, freckles and marks. Don't slim, smooth, reshape or age anything.`
- Enforce single-variable edits (one change per turn) using the Face Codes formula:
  - **Pose only**: `Pose only: change pose to [...]. Keep face, hair, outfit, background and lighting exactly the same. [Identity lock]`
  - **Expression only**: `Expression only: change expression to [...]. Keep face shape, features, pose, outfit, background and lighting exactly the same. [Identity lock]`
  - **Background only**: `Background only: replace background with [...]. Keep character exactly as is: face, hair, pose and outfit. Match lighting to new scene. [Identity lock]`
  - **Outfit only**: `Outfit only: change clothes to [...]. Keep face, hair, pose, background and lighting exactly the same. [Identity lock]`
  - **Lighting only**: `Portrait light: relight with [...]. Only change light and shadows. Keep face, features, skin tone, pose, outfit and background the same. [Identity lock]`

### 6.3 First and last frames (+ extra references)

State each anchor image on its own line — never "@Images 1 and 2 are the first and
last frames." First and last images must share the same aspect ratio.

```
@Image 1 is the first frame. It defines the opening composition, subject position, pose, prop state, scene, and camera direction.
@Image 2 is the last frame. It defines the ending composition, ...
@Image 3 defines <Subject>'s <attributes>. Do not change the first-frame composition defined by @Image 1 or the last-frame composition defined by @Image 2.
<Describe ONE continuous action or event.>
The video begins naturally from the first frame defined by @Image 1 and reaches the last frame defined by @Image 2 after the continuous action.
Between the first and last frames, maintain continuity in <identity, prop structure/ownership, scene layout, camera direction>.
```

### 6.4 Multi-keyframe sequences

```
Use @Image 1 through @Image N as keyframes in this order.
@Image 1 is the first frame. It defines <...>.
@Image 2 defines the second keyframe: <visible end state of Stage 1>.
...
@Image N is the last frame. It defines <...>.
The video passes through the states defined by @Image 1 ... @Image N in order, using continuous action to transition naturally between stages.
Maintain continuity in <subject identity, prop structure and ownership, scene layout, lighting, axis of action> throughout.
```

Keyframes control stage order and key states — not exact per-frame reproduction.

### 6.5 Video extension

Align the boundary frame BEFORE describing new content. Always add: "Keep each
subject as the same continuous instance throughout: do not duplicate or split it."

Forward (after the original):

```
@Video 1 is the source video to extend forward.
Extend @Video 1 forward. The first frame of the extended segment directly continues from the last frame of @Video 1. Maintain continuity in <pose/orientation, prop positions, background, camera position and composition, lighting, motion direction>.
Then, <new action, event, camera treatment, or audio>.
Throughout the extension, maintain continuity in <identity/clothing, key props, background layout, axis of action>.
```

Backward (before the original): describe the preceding events first, then define the
source video's FIRST frame as the explicit end state of the extension ("The last
frame of the extended segment naturally connects to the first frame of @Video 1:
<match pose, props, background, camera, lighting, motion direction>"). Writing only
"then connect to the source video" is not enough. With extra references, state which
materials are used in the extension and which must appear only AFTER the source
video begins.

### 6.6 Storyboard grids & Sheet De-rasterization

≤15 panels, clean line art, minimal text labels. When using a storyboard grid or character sheet as a reference, **always protect against the model animating the grid layout or rendering panels/UI as part of the scene**:

```
@Image 1 provides an <N-panel storyboard grid> for shot order and approximate composition. Read it left to right, top to bottom.
TREAT EACH STORYBOARD PANEL AS A SEPARATE FULL-SCREEN CINEMATIC SHOT.
DO NOT animate the storyboard sheet itself. DO NOT render the character sheet graphic, text, frames, divider lines, panel borders, sheet margins, or any UI elements.
Shot 1: <shot size, subject action, scene state>.
...
The final video uses <visual style>. Audio includes <...>.
```

Storyboards communicate order and approximate composition — not strict panel-by-panel
reproduction. For multi-character sheets (`@Image 2 as character sheet`), always append:
`Use @Image 2 strictly as reference for character design, costume, hair, and expression variations — do not render character sheet layouts, labels, or pose turnaround graphics.`

### 6.7 Blockout references

First classify: **coarse** (simple geometry → provides motion paths, blocking,
camera, cuts, lighting timing, sound rhythm) or **fine** (complete model → re-render
materials, colors, characters, scene, style).

Coarse: map each geometric object to its final subject ("The tall cylinder in
@Video 1 corresponds to <Guide>"), state exactly which temporal/spatial info to
inherit, and exclude the blockout's gray appearance and empty scene.

Fine: "Preserve <structure, action, spatial layout, camera position, movement,
cuts>. Do not use its original gray materials or empty background." Then define the
re-render targets from image refs. Keep fine blockouts clean — no path lines, axes,
controllers, or camera frustums.

### 6.8 One-click video (images → packaged video)

Never write only "turn these materials into a video." Structure:
Material Roles → Image Order → Motion Amount → Editing Style → Visual Treatment → Audio,
using `[Material Roles] [Arrangement] [Image Motion] [Final Style] [Audio]` blocks.
State exact image order if it matters (or explicitly allow thematic ordering); bind
every character/product; keep structural elements stable during image motion.

### 6.9 Seamless transitions between two videos

Order: Before video → After video → Trigger action → Camera movement → Visual
transformation → Arrival state → Audio transition.

```
@Video 1 is the before-transition clip. Use its <ending subject, action, composition, camera direction, audio>.
@Video 2 is the after-transition clip. Use its <opening subject, composition, camera direction, audio>.
Keep <identities, structures, scenes, primary actions> stable in the original portions.
At the end of @Video 1, <subject/foreground object> triggers the transition through <action>.
The camera <direction and speed change>, while <shape/material/light/space> gradually transforms into <corresponding element> at the start of @Video 2.
The transition ends naturally at @Video 2's opening composition, preserving <subject position, camera direction, motion trend>.
Audio transitions smoothly from <before audio> to <after audio>.
```

Transition methods and what to specify: dive/reverse move (camera direction, speed,
when next scene begins); character rotation (pose, direction, continuous change);
foreground occlusion (when it fills frame, following composition); object morph
(corresponding shapes/materials, process); push-pull/focus (movement, focus target,
spatial continuity).

### 6.10 Diagram-Guided Trajectory & Camera Navigation (Red Route Control)

When an uploaded 2D image contains drawn flight routes, arrows, ball trajectories, or FPV camera paths (e.g. red navigation lines):
- Treat the underlying scene as the actual environment.
- Enforce the **Negative Navigation Blocker** so the model uses the line as a coordinate path without drawing it:

```
Use @Image 1 as the terrain/environment and camera navigation guide.
The red route line and red arrow annotations indicate the intended camera flight path / trajectory only.
IMPORTANT NEGATIVE EXCLUSION: The red line, red arrows, route markings, guides, overlays, and all navigation graphics visible in the reference image are strictly for path planning. They must be completely excluded and removed before rendering. Under no circumstances may any red route line, arrow, trail, path indicator, or navigation graphic appear in any frame of the final video.
```

### 6.11 Infinite Seamless Turntable & Locomotion Loops

For character turnaround sheets, running cycles, or infinite looping ambient clips:
- Set duration tight (typically 5s or exact cadence).
- State that loop continuity takes precedence over narrative evolution:

```
Perfect seamless loop: the final frame must match the first frame exactly (first frame equals final frame).
Cyclic motion structure, infinite looping animation without start or stop acceleration.
The rotation/cycle completes exactly one full 360-degree revolution (or stride cycle) and returns precisely to the starting pose.
Loop continuity has higher priority than storytelling.
```

### 6.12 Structured State-Matrix / Tabular Format (Commercials & VFX Transformation)

For complex product transformations, food commercials, or multi-element physics sequences, a tabular state-matrix format ensures zero ambiguity across pipeline stages:

```
[Sequence Matrix]
TRIGGER     | <chef snap / key press / button press / impact beat>
SUBJECT     | <initial state: 2D sketch / disassembled floating parts / raw ingredients>
MOTION      | <orbital path / slow macro push / synchronized assembly>
MATERIAL    | <metallic luster / flowing cheese / glossy carbon fiber / fluid ceramic>
PHYSICS     | <weightless hover / fluid silk movement / realistic impact settle>
CAMERA      | <macro prime arc / slow vertical rise / locked hero close-up>
LIGHTING    | <architect desk lamp / volumetric god rays / warm tabletop beauty glow>
FINAL BEAT  | <fully assembled 3D product / mouthwatering plated hero shot>
```

## 7. Emotional Direction → Observable Performance

Emotion words ("tense", "warm") set direction but leave interpretation loose. For
stable acting, pair the emotion with 2–4 directly visible or audible cues: eye
movement, brow tension, mouth movement, breathing, gaze direction, hand movement.

Single transition:

```
The overall emotion shifts from <start> to <end>.
After <triggering event>, <subject> first shows <immediate observable reaction>.
Then, <eyes/brows/mouth/breathing/gaze/hands> gradually <changes>.
Finally, <subject> expresses <target emotion> through <restrained or explicit outward behavior>.
```

Multiple changes: progress through event-triggered stages ("When <subject> hears
<event>, <reaction>. When <second event> occurs, <change>...").

## 8. Cinematography Terms

Directly supported: shot sizes (extreme wide → extreme close-up), movements (push in,
pull out, pan, lateral move, follow, orbit, dive, dolly out, tilt up, handheld
shake), positions (low angle, overhead, first-person).

Popular techniques — always state WHICH subject and where movement starts/ends:
one-take (subjects/spaces passed in order), dolly zoom (subject size preserved +
background closer/farther), aerial (height, direction, area revealed), FPV (path,
speed, turns), bullet time (frozen action + orbit direction), handheld (followed
subject + shake amount), bounce speed ramp (where it accelerates/decelerates/rebounds
+ resting state).

Uncommon/ambiguous terms — keep the term AND translate it into observable change:

```
<Term> + target subject + visual change + foreground/background relationship + direction or speed
Rack focus: shift focus smoothly from the foreground leaves to the person behind; the leaves blur while the face sharpens.
```

Numeric aperture/focal/shutter values are allowed but the visible result matters more.

## 8b. Biomechanical Grounding & Strict Anatomy (Anti-Glitch Rules for Action & Stunts)

AI video models frequently deform limbs during high-speed actions (martial arts, parkour, dance, sports) or create floating characters. Whenever generating action or fast physical performance, **always mandate strict anatomical grounding**:

```
[Human Anatomy & Physics Rules]
Strict natural human anatomy throughout. Exactly two arms, two legs, and five fingers per hand only.
Do not generate extra legs, overlapping arms, split feet, or materialized afterimages during high-speed rotations, kicks, flips, jumps, landings, or somersaults.
Motion blur only flows thinly on the exterior contours of the body.
All physical attacks, dancing, and stunts are realistically grounded: movements derive from pelvic rotation, shoulder twisting, stepping, center-of-gravity transfer, and natural inertia.
No floor skating; feet plant firmly with believable weight shift.
```

For ziplines, climbing, or hanging: explicitly state the mechanical attachment point (e.g., "The courier is physically attached: hands gripping metal handle clipped to the rolling pulley on the cable, body hanging below; no flying, no hovering, no standing on the cable").

## 8c. Acoustic Environment & Audio Projection Rules

When prompts specify dialogue in varied environments, declare microphone behavior and vocal dynamics:
- **Noisy Crowd / Sports Stadium / Street Vlog:**
  `Audio: The ambient stadium roar is loud. The speaker must intentionally SPEAK LOUDLY and PROJECT THEIR VOICE directly into the phone microphone at close range to stay distinct and louder than background chants.`
- **Intimate Drama / Secret Crush / ASMR Whispers:**
  `Lip-sync is natural and subtle: low-energy whisper tone, natural short pauses of 200–400ms between lines, mouth moves slightly without robotic exaggeration, synchronized breathing and micro-tremors.`

## 9. Structural Habits That Prevent Drift

- One primary state change per stage; every stage declares a visible end state.
- Lock instance counts in a `[Maintain Consistency]` block: "exactly one <X>", "same
  single continuous person, do not duplicate or split", prop ownership, spatial
  direction, camera behavior, and audio policy (e.g., "no music, no cartoon SFX, all
  audio diegetic").
- State irreversible states explicitly ("the bed stays vertical from Stage 2 to the
  end", "the hat never returns to his head").
- Negative constraints belong next to the thing they constrain AND in the
  consistency block.
- References are selected per scene, never required to all appear at once.

## 10. Pre-Submission Checklist (run before delivering any prompt)

- Subject and primary action/event clearly stated?
- Every reference material states what to use AND what not to use?
- Every distinct character/product/prop named and bound to a reference?
- References selected by scene, not forced to appear simultaneously?
- Each long-video stage: one primary change + clear end state?
- Character count, clothing, prop ownership, spatial relationships consistent?
- Editing: sole master, edit scope, target quantity, content to preserve defined?
- Abstract emotions and cinematography terms paired with observable cues?
- First/last frames: one role per image, same aspect ratio?
- Storyboard/blockout: structure to inherit stated; coarse vs fine identified?
- Auto-locked aspect-ratio/duration rules respected for editing/frames/extension?
- Extension: boundary image, motion trend, audio continuity checked?
- One-click: material roles, order, motion amount, editing style, audio defined?
- Transition: both roles, trigger, process, arrival state defined?

## 11. Known Limitations (set expectations; do not promise otherwise)

- Timestamps allocate time budgets — they are not frame-accurate edit points.
- Editing prompts raise alignment probability; they cannot guarantee frame-by-frame overlap.
- Multi-reference = correct selection and combination, not simultaneous appearance.
- For perfectly accurate subtitles/formulas/signs/specs, combine prepared reference
  materials + generation + post-production.
- Editing locks input ratio and ≈duration (±~0.3s); frames mode locks ratio to the
  first image; extension locks the input ratio.
- Seamless transitions aim for visual/audio continuity, not pixel-identical splices.
- Prompt structure improves controllability; it does not raise the model's inherent
  capability ceiling (visual quality, human realism, complex camera execution still
  depend on model capability, materials, and randomness).