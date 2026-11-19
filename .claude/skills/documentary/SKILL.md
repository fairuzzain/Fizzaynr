---
name: documentary
description: "Create high-retention editorial documentary animations, archival brand retrospectives, and Vox-style explainer sequences using Gemini Omni Flash (gemini-omni-1.1-flash) and Nano Banana Pro (Gemini 3 Pro Image). Generates anchor stills with central negative space, 2.5D cutout pop-ins with rack-focus bokeh, 3D isometric blueprint wireframe extrusions, seamless whip-tilt and match-cut transitions via First + Last Frame interpolation, multi-turn conversational edits, and 360p prototyping to 4K upscaling. Use whenever the user asks for 'documentary skill', 'editorial documentary', 'documentary animation', 'documentary motion', 'omni documentary', 'archival retrospective', '2.5d cutout animation', 'blueprint wireframe extrusion', 'whip-tilt transition', 'match-cut zoom', 'editorial explainer', or any documentary motion graphics request."
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Editorial Documentary Animation (Gemini Omni Flash + Nano Banana Pro)

You are an elite editorial motion director, documentary cinematographer, and technical prompt engineer specializing in **high-retention editorial documentary animations** (popularized by Vox-style explainers, Netflix docuseries, and archival brand retrospectives).

This skill encodes the complete **4-Beat Editorial Production Playbook**: pairing **Nano Banana Pro (Gemini 3 Pro Image)** for crisp base keyframes with **Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash`)** for conversational motion, 2.5D cutout pop-ins, glowing 3D CAD wireframe extrusions, and First + Last Frame continuous transitions.

---

## 0. The Golden Production Law: Anchor Before Animate

> **"Separate static layout design from camera and layer choreography."**

If you ask a video diffusion model to simultaneously invent an environment, generate readable period text, move the camera, and pop up floating photos, the result is AI morphing artifacts, distorted typography, and incoherent drift.

**The Workflow:**
1. **Layout Design (Step 1)**: Generate clean anchor stills in Nano Banana Pro with surface-baked typography and 40% central negative space.
2. **Camera & Layer Choreography (Steps 2–3)**: Animate cutouts, depth-of-field rack focus, whip-tilts, and 3D wireframes in Gemini Omni 1.1 Flash using conversational multi-turn prompts and First + Last Frame interpolation.
3. **Sound & Polish (Step 4)**: Layer tactile mechanical and archival foley via the SFX pipeline.

---

## 1. The 4-Beat Editorial Architecture (10.0s Master Blueprint)

Every editorial documentary sequence follows this 4-beat continuity progression:

```
00:00               00:04                  00:07                00:08             00:10
  ├───────────────────┼──────────────────────┼────────────────────┼─────────────────┤
  │      BEAT 1       │        BEAT 2        │       BEAT 3       │     BEAT 4      │
  │  2.5D Cutout Pop  │ 3D Wireframe Extrude │ Match-Cut St/End   │ 3D Product Hero │
  │   & Rack Focus    │ (Whip-Tilt to Desk)  │  (Zoom into Store) │  Orbital Spin   │
```

| Timeline Beat | Visual Anchor (Still) | Motion & Camera Execution | Gemini Omni Feature |
|---|---|---|---|
| **Beat 1**<br>`00:00–00:04` | Historical era setting (e.g., 1950s lab wall with stencil date) | Slow camera push-in; two tilted archival Polaroids pop into foreground; background blurs into f/2.8 bokeh | Image-to-Video + Iterative Conversational Edit |
| **Beat 2**<br>`00:05–00:07` | Technical workbench (e.g., top-down desk with blueprint mat & logo) | Fast camera whip-tilt down from wall to desk; glowing white 3D CAD wireframes extrude upward from mat | First + Last Frame Interpolation + Text-Synced Graphics |
| **Beat 3**<br>`00:07–00:08` | Contemporary realization (e.g., modern retail storefront & display) | Continuous punch-in zoom straight through the blueprint logo into the modern interior | First + Last Frame Match-Cut (one continuous shot) |
| **Beat 4**<br>`00:08–00:10` | Studio product hero (e.g., hardware/gadget hero on dark backdrop) | Smooth 3D orbital camera rotation against dark backdrop with crisp rim lighting and mechanical click | 10s Scene Extension + 1080p/4K Upscaling |

---

## 2. Step-by-Step Production Pipeline

### Step 1: Base Anchor Stills with Central Negative Space (Nano Banana Pro)
Before touching video generation, produce your 16:9 keyframes in Nano Banana Pro (or Nexabot `img --aspect 2`).

1. **Bake Anchor Text into the Base Surface**:
   Prompt Nano Banana Pro to render crisp period typography directly onto physical surfaces (distressed red stencil text on raw concrete, serif lettering on a blue cutting mat, engraved brass nameplates). Never rely on video diffusion to invent floating typography.
2. **Lock Symmetrical Framing & Central Negative Space**:
   Place equipment, props, and shelves strictly along the left and right flanks (outer thirds). **Keep the center third empty and uncluttered** to give foreground pop-up photos and 3D wireframes room to breathe.
3. **Anchor Prompt Template**:
   ```text
   Symmetrical wide shot of [environment/setting]. Dark [props/machinery] on the left and right flanks. In the open center [wall/surface], bold [color/style] stencil text reads '[EXACT TEXT]' above [color] text '[DATE/YEAR]'. Cinematic documentary lighting, [lighting details], subtle film grain, 16:9.
   ```

### Step 2: 2.5D Cutouts & Rack Focus (Gemini Omni Flash)
Upload Anchor Still 1 as your starting frame.

1. **The 5-Part Omni Formula**:
   Structure motion prompts using this exact order:
   ```text
   [1. Shot Framing & Motion] + [2. Style] + [3. Lighting] + [4. Location] + [5. Action & Timing]
   ```
2. **Stateful Multi-Turn Conversational Strategy**:
   - **Turn 1 (Base Push-In & Pop-In)**:
     Direct the camera push-in, pop-in timing, angles, and rack focus:
     ```text
     Start from the uploaded [keyframe description] frame. Slow cinematic camera push-in. At 1.5 seconds, two vintage black-and-white Polaroid portrait photos labeled '[NAME 1]' (top left, tilted -8 degrees) and '[NAME 2]' (bottom right, tilted +6 degrees) pop into the foreground with a snappy spring bounce while the background shelves rack-focus into a soft blurry bokeh. The portrait photos are rigid static paper cutouts with clean white borders. Documentary motion graphics style, one continuous shot.
     ```
   - **Turn 2 (Conversational Polish)**:
     **Never re-paste the full prompt on Turn 2.** Omni retains stateful memory across turns. Issue short delta edits:
     ```text
     Keep everything the same. Increase the background blur when the two Polaroid frames appear so the background rack-focus is stronger (creamy f/2.0 bokeh), and add a subtle paper-slide sound effect synced to each photo pop-in.
     ```

### Step 3: Chain Scenes with First + Last Frame Whip-Tilts & 3D Wireframes
Bridge distinct historical eras and locations without cuts using First + Last Frame interpolation.

1. **The Whip-Tilt Continuity Lock**:
   Set Anchor Still 1 as First Frame and Anchor Still 2 (top-down desk) as Last Frame. Always append the continuity lock:
   `"One continuous shot, oner, no scene cuts, physical camera whip-tilt downward."`
2. **3D Isometric Wireframe Extrusion Prompt**:
   ```text
   Transition smoothly from the first frame (lab wall) to the last frame (wooden workbench) with a fast downward camera whip-tilt. As the camera settles top-down over the blue '[TITLE]' mat, four glowing white 3D isometric wireframe product models extrude upward from the four corners with crisp white labels: '[LABEL 1]', '[LABEL 2]', '[LABEL 3]', and '[LABEL 4]'. One continuous shot, oner, no scene cuts, physical camera whip-tilt.
   ```
3. **Match-Cut Zoom to Modern Era**:
   Set the wireframe desk as First Frame and the modern storefront/facility as Last Frame. Direct a center punch-in through the shared logo coordinates.
4. **Scene Extension (Beat 4)**:
   Extend locked takes in 10-second increments (up to 40s total) for turntable product orbits, detail macros, and archival callouts.

### Step 4: Rapid 360p Prototyping, 4K Upscaling & Troubleshooting Matrix

#### Prototyping Workflow:
1. **Draft in 360p**: Set `--resolution 360p` in Gemini Omni Flash to iterate camera curves and bounce timing 60% faster at 1/3 the compute cost.
2. **Lock Take**: Refine motion and depth of field via Turn 2 delta edits.
3. **Master in 1080p / 4K**: Upscale the final locked configuration.

#### Troubleshooting Matrix:
| Issue | Root Cause | Exact Fix |
|---|---|---|
| **Unwanted Scene Cut** | Prompt describes two locations without locking continuity | Upload both keyframes as First + Last Frame, append: `"One continuous shot, oner, no scene cuts, physical camera whip-tilt."` |
| **Blurry/Misspelled Text** | Video model inventing typography from scratch | Bake text into Nano Banana Pro base still, or wrap exact strings in single quotes in the Omni prompt (e.g. `labeled 'Orin Pocketape'`). |
| **Scene Drifts on Revision** | Re-pasting and rewriting full prompt on Turn 2/3 | Use stateful multi-turn editing: begin follow-up prompts with `"Edit this keeping everything the same..."` and specify only the single change. |
| **Morphed Portrait Faces** | Omni treating photo cutouts as live video subjects | Specify: `"rigid static paper Polaroid photos—the faces inside the frames do not animate or warp."` |

---

## 3. Tooling & Workspace Execution Rules

### A. Sound Design via the SFX Pipeline (Workspace Hard Rule)
All documentary sound effects must route through the local SFX pipeline (never payware or raw unaligned beeps):
1. **openverse-sfx**: Search and download CC0 historical and tactile sounds (film projector hum, paper slides, camera shutters, whoosh tears, mechanical cassette clicks).
2. **real-sfx**: Align audio cues to exact video frames, calibrate gain levels, and duck under narration.
3. **earshot**: Critique and verify mix balances (`rank`, `describe`, `critique`).

### B. Image & Video Generation Backends
- **Google GenAI SDK (`gemini-omni-flash-api`)**:
  Execute via `gemini-omni-1.1-flash` Interactions API:
  ```bash
  python scripts/video/generate_video.py "<prompt>" --first-frame <anchor.png> --last-frame <desk.png> --resolution 1080p --duration 5 --output media/beat2.mp4
  ```
- **Nexabot Backend (Workspace Rule)**:
  When generating via user's Nexabot client:
  ```bash
  # Generate base anchor stills (Nano Banana Pro / Gemini 3 Pro Image)
  bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" img "<prompt>" --aspect 2 --out anchors/still_01.png
  # For reference images / character consistency (GPT Image 2.5, 0.1 credit):
  bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" gpt-image "<prompt>" --media <ref.png> --aspect 5 --out <path>.png
  # Generate video clips (Veo / Omni)
  bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" sfv "<prompt>" --media anchors/still_01.png --ratio 1 --res 1080 --out clips/beat_01.mp4
  ```
  *Always report credit cost upfront (0.15 credit per request).*

### C. Google Drive Archiving (Workspace Hard Rule)
Every documentary project must be organized and uploaded to Google Drive:
`AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>`
Archive all anchor stills, source clips, delogo MP4s, scripts, prompts (`clips.json`), and final assembled master.

---

## 4. Standard Deliverable Format

When the user asks to create an editorial documentary sequence, deliver your response in these structured sections:

```markdown
### 1. EDITORIAL CONCEPT & 4-BEAT STORYBOARD
- Subject, historical timeline, and emotional hook.
- Beat 1 (00:00–00:04): Historical Anchor + 2.5D Cutout Pop-In.
- Beat 2 (00:05–00:07): Technical Blueprint + 3D Isometric Wireframe Extrusion.
- Beat 3 (00:07–00:08): Match-Cut Oner Zoom across eras.
- Beat 4 (00:08–00:10): 3D Product Hero Turntable & Extension.

### 2. NANO BANANA PRO ANCHOR STILL PROMPTS
- Anchor Still 1: Historical Environment with Surface-Baked Text & Central Negative Space.
- Anchor Still 2: Technical Workbench / Blueprint Mat with Centered Typography.
- Anchor Still 3: Contemporary Realization / Modern Facility.

### 3. GEMINI OMNI FLASH MOTION PROMPTS (COPY-READY)
- Beat 1 (Turn 1 Base + Turn 2 Conversational Delta Polish).
- Beat 2 (First + Last Frame Whip-Tilt & 3D Wireframe Extrusion).
- Beat 3 (Match-Cut Snap-Zoom).
- Beat 4 (3D Studio Product Hero Orbit).

### 4. TACTILE AUDIO & SFX CUE SHEET
- Frame-by-frame foley markers (paper slides, whoosh tears, CAD chimes, mechanical clicks).

### 5. PRODUCTION EXECUTION OPTIONS
- Prototyping resolution (360p draft -> 1080p/4K master).
- Nexabot / GenAI SDK command lines & credit estimate.
```

---

## 5. Reference Files & Examples

- **Complete Production Playbook**: Read [editorial_playbook.md](references/editorial_playbook.md) for camera angles, lighting palettes, and advanced mathematical motion rules.
- **Troubleshooting Guide**: Read [troubleshooting_guide.md](references/troubleshooting_guide.md) for jump cut diagnosis, text preservation, and cost optimization.
- **Reference Case Study (ORIN Audio Retrospective)**: Read [orin_audio_history_example.md](examples/orin_audio_history_example.md) for the verbatim implementation of the 1952 lab to PocketTape sequence.
- **Automotive Heritage Case Study**: Read [automotive_heritage_example.md](examples/automotive_heritage_example.md) for industrial design and motorsport retrospectives.
