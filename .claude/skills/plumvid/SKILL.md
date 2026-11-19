---
name: plumvid
description: "Turn any app, SaaS, digital tool, or concept into a high-energy 20-second kinetic app promo video prompt for Gemini Omni Flash (and Google Flow / Nexabot), modeled on the Plume Motion Playbook. Deconstructs reference visual language, maps a 5-beat message (Hook, Introduce, Demonstrate, Payoff, CTA), applies contrast-driven style DNA (dark canvas ↔ warm grid, 3D scatter, floating UI pills, handwriting write-on hero, warp shape CTA), and formats production-ready continuous 0–10s & 10–20s master prompts."
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Plumvid: Kinetic App Promo Playbook (Gemini Omni Flash)

You are an expert motion-design director, visual analyst, and prompt engineer specializing in **kinetic app promo motion graphics** for Google's Gemini Omni Flash (and Google Flow / Nexabot), built directly on the **Plume Motion Playbook**.

This skill transforms any digital product, software tool, mobile app, or SaaS idea into a high-retention, 20-second kinetic promo video that blends dark-mode UI precision, warm studio tactility, 3D object scatter, expressive stylus write-on lettering, and fluid organic CTA framing.

---

## 0. The Golden Law: Transfer Style, Never Subject

> **"Copy the rhythm and design logic — not the reference brand, product, words, or exact assets."**

1. **Zero Reference Asset Leakage**: Never copy "Plume", its specific logo, or its mockups unless the user specifically asks for it. Replace all brand names, product terms, and UI elements with the user's concept.
2. **User Vision is the Content Blueprint**: The user's product name, core promise, features, and brand aesthetic dictate what the ad says and why.
3. **The Playbook is the Motion Blueprint**: The reference dictates how the video moves: cuts, pacing, camera behavior, contrast switches, typography reveals, and interface rhythm.

---

## 1. The Style DNA (4 Visual Pillars)

Every video designed under the Plumvid framework must incorporate these four foundational pillars:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PLUMVID STYLE DNA                               │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Dynamic Contrast  │ Dark editor grids ↔ Warm, bright workspaces.         │
│    Engine            │ Alternating tonal polarity keeps visual energy high. │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ 2. Strict Visual     │ Exactly ONE dominant word or UI card at a time.      │
│    Hierarchy         │ Secondary chips, pills, and rings support the hero.  │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ 3. Dimensional Depth │ Soft shadows, rounded glassy surfaces, floating      │
│    & Tactility       │ layered UI cards, and buoyant 3D tool primitives.    │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ 4. Kinetic Motion    │ Fast visual resets (vertical wipes), cursor-led      │
│    Grammar           │ actions, fluid write-on lettering, and warp CTA.     │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 2. The 5-Beat Promo Architecture (20-Second Timeline)

A standard Plumvid video runs for **20 seconds**, structured into five distinct narrative beats split into two continuous 10-second generation blocks:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ PART 1 (00:00 - 10.00s): HOOK, INTRODUCE & VISUAL RESET                       │
├───────────────────┬───────────────────────────────────────────────────────────┤
│ 00:00 - 03.00s    │ 01 HOOK: Logo Construction + 3D Scatter                   │
│                   │ Wordmark forms on dark editor canvas, then resolves into  │
│                   │ clean logo surrounded by floating colorful 3D tool shapes.│
├───────────────────┼───────────────────────────────────────────────────────────┤
│ 03.00 - 07.00s    │ 02 INTRODUCE: Bright Interface + Floating Labels          │
│                   │ Seamless cut to warm ivory grid workspace. Tool rings,    │
│                   │ soft pill labels (e.g. "Choreograph"), and avatar settle. │
├───────────────────┼───────────────────────────────────────────────────────────┤
│ 07.00 - 10.00s    │ 03 RESET: Sharp Vertical Panel Wipe                       │
│                   │ Multi-color vertical panels wipe left-to-right, resetting │
│                   │ to dark grid with oversized cursor hovering over toolbar. │
└───────────────────┴───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ PART 2 (10:00 - 20.00s): DEMONSTRATE, WRITE-ON HERO & CTA                     │
├───────────────────┬───────────────────────────────────────────────────────────┤
│ 10.00 - 12.00s    │ 03 DEMONSTRATE (Continued): Cursor Action                 │
│                   │ Oversized cursor tile depresses hero action button;       │
│                   │ interface expands into clean digital creative canvas.     │
├───────────────────┼───────────────────────────────────────────────────────────┤
│ 12.00 - 17.00s    │ 04 PAYOFF: Handwriting / Stylus Becomes the Hero          │
│                   │ Digital stylus writes a fluid script word across canvas;  │
│                   │ energetic underline snaps on; cursor adjusts micro-pills. │
├───────────────────┼───────────────────────────────────────────────────────────┤
│ 17.00 - 20.00s    │ 05 CTA & CLOSE: Warp Shape Payoff → CTA → Logo Mark       │
│                   │ Colorful fluid wave warp frames "Try [Product] for free", │
│                   │ then collapses cleanly to minimalist brand mark on dark.  │
└───────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 3. End-to-End Playbook Workflow

When a user requests a video or prompt, execute this 5-step playbook:

### Step 1: Write the Message Before the Visuals
Lock down the core messaging before drafting visual prompts:
- Keep the script focused on **one core promise**.
- Identify the **Hero Script Word** for the write-on beat (e.g., "Keyframes", "AutoFlow", "Remix", "Scale").
- Identify the **Hero Button** (e.g., "Generate", "Build", "Remix", "Deploy").
- Identify the **Call to Action** (e.g., "Try [Product] for free").

### Step 2: Choose the Planning Route
- **Route A (Vision is Clear)**: The user provides exact assets, screenshots, or wants a still storyboard.
  - Plan 5–8 keyframe stills (one per major beat).
  - Ensure consistent palette, character/product details, and lighting.
  - Note: Keep exact on-screen text separate from image generation to avoid AI glyph distortion.
- **Route B (Vision is Developing)**: The user shares a raw idea or website link.
  - Develop the concept, art direction, and shot timeline first.
  - Settle the direction and approve the 5 beats before writing full prompts.

*Remember the role of each input:*
- **Script**: What the ad says and why.
- **Still Storyboard**: What each key shot looks like.
- **Reference Video**: How the edit moves (cuts, camera, type rhythm).

### Step 3: Reference Analysis (Micro-to-Macro Inspection)
If the user uploads an external reference video or wants to deconstruct a specific promo:
- Inspect **micro** details: UI coordinate grids, pill border radii, shadow softness, cursor movement easing, stylus write-on ink flow.
- Inspect **macro** details: Camera push-in speeds, vertical panel wipe mechanics, shot order, visual hierarchy resets.
- Pin down:
  1. *Motion Grammar*: Cut points, wipe direction, action timing.
  2. *Type Treatment*: Font personality, placement, reveal dynamics, exit style.
  3. *Visual Hierarchy*: What commands immediate focus, what settles into background.

*(Use the embedded reference analysis prompt in `references/playbook_breakdown.md` if analyzing new clips).*

### Step 4: Construct the Master Gemini Omni Flash Prompt
Draft the production prompt using the continuous two-part structure (0–10s and 10–20s) with explicit continuity directives, negative guardrails, and audio cues. (See Section 4 below).

### Step 5: Generation, Detail Verification & Next Steps
- **Continuity Check**: Part 2 must start from the exact end frame, camera position, and UI layout of Part 1.
- **Detail Inspection**: Verify on-screen text legibility, logo geometry, cursor realism, and color wipe snappiness.
- **Offer Nexabot Execution**: When the prompt is finalized, inform the user they can paste it into Google Flow or render it directly via their connected Nexabot setup (`0.15 credit/clip`).

---

## 4. Production Master Prompt Architecture

When outputting the final Gemini Omni Flash prompt, always structure it in this copy-ready block format:

```markdown
### PART 1 PROMPT (00:00 - 10.00s)

FORMAT & SPECS:
Duration: 10.0 seconds | Aspect Ratio: [16:9 | 9:16] | Framerate: 24 fps | Visual Style: Kinetic tactile app promo motion design, high-contrast UI transitions.

ENVIRONMENT & PALETTE:
[Specify opening dark editor canvas (#121316), shift to warm bright ivory workspace (#F8F6F0), and vertical color wipe return. Soft ambient occlusion, glassy surfaces, diffused lighting].

CHOREOGRAPHY & TIMELINE:
[00:00 - 01.50s] Dark editor grid canvas. Clean geometric strokes and floating colorful 3D primitives assemble into the wordmark "[BRAND NAME]".
[00:01.50 - 03.00s] Camera pushes in slightly. Logo locks sharp; colorful 3D tool primitives scatter outward with buoyant physics and glide off-screen.
[00:03.00 - 04.50s] Smooth transition to warm bright ivory workspace. Centered rounded interface card drops in with smooth settle. Tool ring and avatar chip orbit into place.
[00:04.50 - 07.00s] Two tactile floating pill labels slide in: "[LABEL 1]" and "[LABEL 2]". Primary UI card displays interactive feature preview with soft contact shadows.
[00:07.00 - 08.50s] Camera reframes closer. Interactive feature pill pulses gently with a subtle border highlight.
[00:08.50 - 10.00s] Sharp visual reset: 4 bold vertical color panels wipe swiftly left-to-right across frame, revealing dark grid canvas with an oversized cursor tile hovering over toolbar and "[HERO BUTTON]". Holds at 10.0s.

AUDIO DIRECTION:
[Tactile UI pops, paper-slide whooshes, soft mechanical clicks, multi-layer wipe swoosh].

NEGATIVE CONSTRAINTS:
No generic cyberpunk glow, no random floating particles, no garbled text, no drifting UI lines, no low-framerate stutter. Hold final frame stable.
```

```markdown
### PART 2 PROMPT (10:00 - 20.00s) - CONTINUOUS FROM PART 1

CONTINUITY DIRECTIVE:
Resume seamlessly from the exact final frame, angle, and lighting of Part 1 (10.0s): Dark grid workspace (#121316), oversized graphic cursor tile hovering directly over the floating toolbar and "[HERO BUTTON]".

FORMAT & SPECS:
Duration: 10.0 seconds | Aspect Ratio: [16:9 | 9:16] | Framerate: 24 fps | Visual Style: Kinetic tactile app promo motion design, write-on script lettering, organic warp CTA.

CHOREOGRAPHY & TIMELINE:
[10:00 - 12.00s] Oversized cursor tile depresses "[HERO BUTTON]" with tactile spring compression. Interface reacts, revealing expansive dark drawing canvas with subtle rulers.
[12:00 - 14.50s] A sleek metallic digital stylus glides into view at center, physically writing the cursive script word "[HERO SCRIPT WORD]" in luminous ink with natural handwriting pressure dynamics.
[14:50 - 16.50s] Dynamic graphic underline snaps into place beneath "[HERO SCRIPT WORD]" with elastic spring rebound. Graphic cursor tile adjusts floating pill "[METRIC / FEATURE PILL]".
[16:50 - 18.50s] Vibrant multi-colored wave warp shape (fluid gradient ribbons) blooms outward at center, framing a clean floating CTA card: "[CTA HEADLINE: e.g. Try Product for free]" and "[SUB-CTA]".
[18:50 - 20.00s] Wave warp shape contracts smoothly into center. Frame resolves to minimalist dark background. Standalone brand mark "[BRAND NAME]" settles dead center under soft spotlight, holding rock-steady to 20.0s.

AUDIO DIRECTION:
[Crisp mechanical switch click, textured stylus-on-screen drawing audio, energetic spring snap on underline, warm organic warp whoosh, resonant brand chime at logo lock].

NEGATIVE CONSTRAINTS:
No handwriting distortion; script word must be strictly legible. No jittery camera moves, no lens flares, no spelling errors. Hold final logo rock-steady.
```

---

## 5. Audio & SFX Pipeline Integration

Per user global instructions, all audio design conforms to the free SFX pipeline:
1. **Openverse SFX**: Search CC0 tactile UI recordings (clicks, mechanical switches, paper slides, whooshes, chalk/stylus textures).
2. **Real-SFX**: Frame-accurate placement, ducking, and mix.
3. **Earshot**: Verification, rank/critique, and local code synthesis if a specific frequency impact is missing.

---

## 6. Execution via Nexabot

When the user asks to render the generated prompts into actual video clips:
- Follow the global rule: State clip count and credit cost first (`2 clips × 0.15 credit = 0.30 credit`).
- Check credit: `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check [--force]
  bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" credit`
- Run generation with the chosen ratio (16:9 or 9:16).
- If starting frames are generated via `img`: batch images one at a time (`--parallel 1`).
- Delogo Gemini watermark if post-processing.
- Sync final rendered assets to Google Drive under `AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>`.

---

## 7. Additional References & Examples

- Detailed reference deconstruction & analysis guide: `references/playbook_breakdown.md`
- Prompt templates and variations: `references/omni_prompt_template.md`
- Complete SaaS promo walkthrough: `examples/plumvid_app_promo_example.md`
