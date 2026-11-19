# Editorial Documentary Troubleshooting & Diagnostic Guide

This reference provides exact diagnosis and fixes for common generation artifacts, camera glitches, text issues, and workflow bottlenecks in Gemini Omni Flash and Nano Banana Pro.

---

## 1. Core Diagnostic Matrix

| Issue | Symptom | Root Cause | Exact Operational Fix |
|---|---|---|---|
| **Unwanted Scene Cut** | Hard cut or cross-dissolve instead of smooth whip-tilt | Prompt describes two locations without locking continuous shot mechanics | In First + Last Frame prompt, append: `"One continuous shot, oner, no scene cuts, physical camera whip-tilt downward."` Never describe the second location as a new scene. |
| **Blurry or Warped Text** | Garbled letters, pseudo-alphabet, drifting typography | Relying on video model to generate small text from scratch during motion | 1. Bake major typography into the Nano Banana Pro base still.<br>2. Wrap exact required words in single quotes in the Omni prompt (e.g. `labeled 'ORIN CINEMA'`). |
| **Scene Drifts on Revision** | Composition, props, or faces shift completely on Turn 2 | User re-pasted the entire prompt, treating multi-turn as a fresh generation | Use stateful conversational syntax: begin turn with `"Edit this keeping everything the same. [Specify only the delta]."` |
| **Morphed Portrait Cutouts** | Faces in Polaroid frames morph, blink, or melt during pop-in | Omni treats photo cutouts as live video subjects rather than static paper photographs | Prompt explicitly: `"Two rigid static paper Polaroid photos with matte photographic prints—the images inside the frames do not move or animate."` |
| **Incoherent Wireframe Lines** | Wireframe lines scribble randomly instead of clean product shapes | Prompt lacks geometric structure or projection type | Specify: `"Crisp glowing white 3D isometric line-art CAD wireframes with precise straight lines and clean right angles, extruding upward."` |
| **Match-Cut Zoom Disconnect** | Center punch-in zooms into an offset or misaligned area | The focal target in Frame 1 does not align with the entry point in Frame 2 | Ensure the anchor element (e.g., logo or portal) is placed dead center in both images (`x: 50%, y: 50%`) before interpolating. |
| **Slow Multi-Scene Iteration** | Wasted credits and long wait times during early draft phase | Rendering full sequences at 1080p or 4K during camera curve testing | Force `--resolution 360p` for initial motion checks (renders 60% faster at 1/3 credit cost). Upscale to 1080p/4K only after timing is locked. |

---

## 2. Deep Dive: Fixing First + Last Frame Jump Cuts

When Gemini Omni 1.1 Flash produces a cut between two frames instead of moving the camera, the prompt usually failed to describe the physical camera movement bridging them.

### Bad Prompt (Causes Jump Cut)
> "First frame is the 1952 workshop wall. Last frame is the top-down wooden desk. Show both frames."

### Good Prompt (Forces Physical Camera Movement)
> "Transition smoothly from the first frame (lab wall) to the last frame (wooden workbench) with a fast downward camera whip-tilt. The camera physically tilts down on its vertical axis while rapidly dropping downward, causing vertical motion blur on the concrete wall until settling top-down over the desk mat. One continuous shot, oner, no scene cuts, physical camera whip-tilt."

---

## 3. Deep Dive: Preventing Text & Date Corruption

### Principle 1: Surface Binding in Anchor Stills
Nano Banana Pro reliably produces clean typography when the text is physically attached to an object or surface:
- ✅ `"Distressed red stencil lettering on raw concrete reading 'OCT 1952'"`
- ✅ `"White silk-screened Helvetica lettering on the blue cutting mat reading 'ORIN'"`
- ❌ `"Add text on top of the screen saying OCT 1952"` (treated as floating graphic overlay, often warps)

### Principle 2: Rigid Tracking in Video Motion
When introducing new text overlays during motion in Gemini Omni 1.1 Flash:
- Quote the exact string: `labeled 'ELIAS VANCE'`
- Describe its physical medium: `"printed on the white lower border of the Polaroid photo"`, `"clean white vector callout text tethered by a thin line"`
- Anchor to an object: `"the label stays locked to the top-left corner of the wireframe box as it moves"`

---

## 4. Multi-Turn Conversational Best Practices

Gemini Omni retains the context of previous video generations within the same interaction session.

### Turn Architecture
```
Turn 1: Base Generation (Camera path, major subject actions, primary timing)
   │
   ▼  Output reviewed
   │
Turn 2: Motion Tuning (Rack-focus depth, bounce overshoot, speed curve)
   │
   ▼  Output reviewed
   │
Turn 3: Audio & Lighting Polish (Sound sync cues, rim lighting intensity, vector glow)
   │
   ▼  Take locked
   │
Turn 4: Upscale & Extension (Switch to 1080p/4K or extend clip duration by 10s)
```

### Turn 2 / Turn 3 Prompt Templates
- **To intensify background blur:**
  `"Edit this keeping everything the same. When the Polaroid cutouts pop into the foreground at 1.5s, rack-focus the background more aggressively so the lab shelves blur into heavy f/2.0 bokeh."`
- **To tighten motion physics:**
  `"Edit this keeping everything the same. Make the Polaroid landing crisper with a micro spring overshoot (settles in 0.2 seconds)."`
- **To add audio cues:**
  `"Edit this keeping everything the same. Include a subtle tactile paper-slide sound effect synced exactly to each photo pop-in."`

---

## 5. Prototyping & Render Cost Optimization

### Cost Analysis (Per 10s Clip)
- **Drafting (360p)**: Fastest turnaround (~20–30s), lowest resource usage.
- **Production (720p / 1080p)**: Crisp edges, sharp typography, broadcast quality.
- **Mastering (4K)**: Extended render time, ideal for final archival master delivery.

### Recommended Pipeline:
1. Generate base anchor stills in Nano Banana Pro (or Nexabot `img --aspect 2`).
2. Draft motion and transitions in Gemini Omni Flash at **360p** to verify camera velocity and layer timing.
3. Lock the camera take via conversational delta edits.
4. Render the locked prompt at **1080p** or **4K**.
5. Pass final audio through the SFX pipeline (`openverse-sfx` → `real-sfx` → `earshot`).
6. Sync completed documentary package to Google Drive (`AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>`).
