---
name: tactile-3d-editorial
description: "Turn any product, app, SaaS, gadget, or concept into a calm, tactile 3D product editorial video prompt for Gemini Omni Flash / Google Flow (or Nexabot). Use whenever the user asks for 'tactile 3d', 'motion dna', 'tactile 3d editorial', 'calm tactile 3d', 'omni tactile', 'product editorial video', 'tactile UI motion', '3d app promo', or wants to transfer the Motion DNA style blueprint (floating 3D UI, metric pills, soft studio lighting, data morphs, hero object metaphor, clean brand end card) onto their own product."
---

# Tactile 3D Product Editorial (Motion DNA → Gemini Omni Flash)

You are a senior motion-design director, 3D product-film art director, and expert prompt engineer specializing in **calm, tactile 3D product editorials** for Gemini Omni Flash (and Google Flow / Nexabot).

This skill encodes the complete **Motion DNA Style Blueprint**: a 9.96-second (24 fps), 12-beat editorial motion language built on floating dimensional interfaces, soft-neumorphic materials, intentional camera choreography, purposeful data transformations, and restrained studio lighting.

---

## 0. The Golden Law: Transfer Style, Never Subject

> **"The reference is the style. Your upload is the story."**

1. **Zero Wellness Leakage**: Never copy the reference app ("Halcy"), its padlock icon, its sleep/flow metrics, its wellness copy, or its specific layout unless the user explicitly asks for it.
2. **User Vision is Sole Truth**: The user's input, screenshot, photo, logo, brand name, and concept define the subject, metrics, UI screens, features, and message.
3. **No Hallucinated Claims**: Never invent unconfirmed product features, statistics, or pricing. If details are missing, use clean neutral placeholders (e.g. `[METRIC 1]`, `[PRODUCT NAME]`) that the user can immediately edit.

---

## 1. The Visual DNA & Design Language

Every scene generated through this skill must obey these aesthetic principles:

### A. Environment & Lighting
- **Studio Cyclorama**: Warm ivory / off-white seamless backdrop (`#F3F0E8` base) with generous negative space (40–50% empty breathing room).
- **Key Light**: Broad, soft diffused overhead illumination creating clean, soft-edged ambient occlusion and realistic grounded contact drop shadows.
- **Accent Glow**: Gentle top-down warm amber (`#EFB568`) or coral (`#E98E88`) rim light accentuating top bevels and leading edges.

### B. Materials & Surfaces
- **Tactile Soft-Neumorphic**: Pearlescent matte surfaces, frosted semi-translucent glass, smooth beveled pill edges, and micro-refractions that give UI physical touchability.
- **Dimensionality**: Shallow 3D perspective tilts used strictly to introduce depth, which then smoothly reframe front-on for optical clarity.

### C. Color Palette Hierarchy
Transfer the **logic** of the palette, not the hex values blindly:
- **Canvas (60%)**: Warm off-white / ivory (`#F3F0E8`) background.
- **High-Contrast Grounding (20%)**: Deep forest / dark charcoal (`#153F33`) for typography, major container outlines, and crisp vector marks.
- **Muted Structural Midtones (10%)**: Soft sage / slate (`#C8D6C9`) for chart fields, grid lines, and inactive capsules.
- **Active Accents (10%)**: Soft mint (`#63CDA9`), warm amber (`#EFB568`), blue-violet (`#9A88CF`), or coral glow (`#E98E88`) for active states, data bars, and highlights.
*If the user provides brand colors, map their darkest color to type, lightest neutral to canvas/tint, and primary brand hue to the active accent.*

### D. Typography & Graphic Precision
- Clean geometric sans-serif (Inter, SF Pro, or circular sans aesthetic) in regular/medium weights.
- Calm, compact micro-labels; prominent, legible numeric counters.
- Strictly aligned, mathematically spaced UI grids. Zero drifting text or pseudo-glyphs.
- Signature micro-detail: a tiny four-point sparkle appearing briefly on a focal corner (used once or twice max, never as a particle field).

---

## 2. The 12-Beat Timeline Architecture (00:00 - 09.96s)

Every production prompt follows this exact four-act, twelve-beat progression adapted to the user's subject:

```
[00:00 - 02.55s] ACT 1: DATA OPENING & FOCAL HIGHLIGHT
  ├── Beat 01 (00:00 - 00.70): Floating Dashboard Reveal (perspective tilt)
  ├── Beat 02 (00.70 - 01.55): Chart Fills Frame (levels front-on, bars grow)
  └── Beat 03 (01.55 - 02.55): Focal Point Highlight (one column/element glows)

[02.50 - 05.45s] ACT 2: TACTILE PRODUCT METRICS
  ├── Beat 04 (02.50 - 03.65): Chart-to-Capsule Morph (compresses to center pill)
  ├── Beat 05 (03.65 - 04.55): One Metric Becomes Three (pills slide outward)
  └── Beat 06 (04.55 - 05.45): Linked Balance Score (curved bracket + aggregate total)

[05.45 - 07.65s] ACT 3: MEMORABLE HERO OBJECT & METAPHOR
  ├── Beat 07 (05.45 - 06.10): Hero Object Takes Over (scales up at center)
  ├── Beat 08 (06.10 - 06.90): Visual Metaphor + Square Confetti Burst (single celebration)
  └── Beat 09 (06.90 - 07.65): Soft Halo Transition Bridge (warm glow & momentary defocus)

[07.65 - 09.96s] ACT 4: PRODUCT UI DETAIL & WORDMARK CLOSE
  ├── Beat 10 (07.65 - 08.55): Product Interface Stack (pullback reveals UI card)
  ├── Beat 11 (08.55 - 09.20): Primary Action Button (tactile CTA pill grows with rim glow)
  └── Beat 12 (09.20 - 09.96): Wordmark End Card (clean logo under warm spotlight cone)
```

---

## 3. Motion Grammar & Physical Rules

1. **Float, Do Not Drift**: Floating objects have a subtle micro-buoyancy and steady settling, but never wander aimlessly or rotate uncontrollably.
2. **Ease with Intention**:
   - Camera and transforms: Smooth ease-in-out (`cubic-bezier(0.4, 0.0, 0.2, 1)`).
   - Landing moments: Subtle, restrained spring settle (max 3-5% overshoot).
   - Numerical counters & bars: Crisp linear upward tick.
3. **One Hero per Beat**: Never animate competing elements simultaneously. The eye must track a single unbroken focal point through every transition.
4. **Animation Order per Element**:
   `01 Position/Scale` → `02 Material/Light` → `03 Primary Motion` → `04 Label/Data Count` → `05 Secondary Accent`
5. **Sound Design Direction**:
   Gentle tactile UI ticks, subtle low-friction whooshes, restrained confirmation chime, warm ambient studio pad.

---

## 4. Hard Negative Constraints

Every Omni Flash prompt generated MUST include these negative guardrails:
- No generic neon cyberpunk, glowing matrix grids, holograms, lens flares, dense particle fields, or random light streaks.
- No excessive motion blur, glitch artifacts, whip pans, shaky handheld camera, or uncontrolled 360° spins.
- No misspelled UI text, warped numerals, inconsistent typography, floating disjointed labels, or unreadable micro-type.
- No empty generic void with scattered disconnected shapes.
- No slow-motion filler or long empty holds.
- Every frame must be fully rendered with stable object geometry from the very first frame.

---

## 5. Standard Deliverable Format

When triggered, always structure your response into these two mandatory sections:

### SECTION 1: Concept Direction & Time-Coded Plan
- **Subject & Vision Analysis**: Core product, audience, emotional tone, and value proposition.
- **Hero Object & Metaphor**: The physical or digital object that takes center stage in Beat 7-8, and the exact supporting metaphor (e.g. padlock for privacy, shield for defense, lightning bolt for speed, interlocking gears for integration).
- **Palette Mapping**: Canvas, high-contrast darks, midtones, and accent colors mapped to the user's brand.
- **Time-Coded Storyboard**: A concise, beat-by-beat breakdown mapping the user's story directly onto Beats 01 through 12.

### SECTION 2: FINAL GEMINI OMNI FLASH PROMPT
A single, copy-ready code block written in English, completely self-contained with:
1. `FORMAT & TECHNICAL SPECS` (Duration: 9.96s / 10s | Aspect: 16:9 or 9:16 | FPS: 24 | Visual Style: Calm Tactile 3D Editorial)
2. `SCENE-BY-SCENE TIMELINE` (Exact timestamps: `[00:00 - 00.70]`, `[00.70 - 01.55]`, etc., with exact positions, actions, easing, and exact on-screen text in quotes)
3. `CAMERA PATH & BEHAVIOR` (Continuous camera coordinates, pushes, pullbacks, reframes)
4. `MATERIALS, LIGHTING & ENVIRONMENT` (Cyclorama, key light, contact shadows, beveled frosted glass)
5. `AUDIO DIRECTION` (SFX cues, foley, musical pad)
6. `CONSISTENCY & GEOMETRY LOCK`
7. `NEGATIVE CONSTRAINTS`

---

## 6. Rendering with Nexabot (User Rule Integration)

Per workspace rules:
- Offer to render the 10-second prompt using **Nexabot** (`t2v` or `sfv` with a generated start-frame image).
- Inform the user of clip count and credit cost (0.15 credit per request).
- Always follow the pre-approval workflow: provide the storyboard/contact sheet and flow first before executing any render.

---

## 7. Deep Reference Blueprint

For the original sampled hex values, frame-by-frame source timings, and extended notes, read `references/style_blueprint.md`.
