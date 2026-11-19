---
name: 11-video-effects
description: 11 free video effects built in code for Remotion (Orbit, Vertigo, Zoom-through, Headlines, Paper Cut, Charts, Phone Screens, Frame Break, Pullback, Glitch, Typewriter). Use when building Remotion scenes, transitions, scroll-stopping hooks, kinetic typography, motion graphics, or video effects in code.
---

# The 11 Video Effects (Remotion in Code)

Eleven motion and video effects designed to be built entirely in code with Claude Code or Antigravity inside a Remotion project — no camera, no external editing timeline, zero render hallucinations. Every effect can be customized with your brand colors, typography, and assets.

## Quick Reference Table

| # | Effect | Visual Signature | Ideal Timing / Use Case |
|---|--------|------------------|-------------------------|
| 01 | **Orbit** | 3D phone flies up while blurred feed scrolls rapidly | First second hook (scroll stopper) |
| 02 | **Vertigo** | Dolly-zoom: subject locked in scale while corridor recedes | Dramatic revelation, impactful shock line |
| 03 | **Zoom-through** | Crash-zoom penetrating through a tile into a lit grid | Fast seamless scene transition (6 frames) |
| 04 | **Headlines** | Tilted 3D wall with 4 columns scrolling contra-directionally | Social proof, news buzz, trend volume |
| 05 | **Paper Cut** | Cream paper slaps down with bounce, letterpress word stamp | Mid-video tactile reset, texture contrast |
| 06 | **Charts** | 16 bars grow in staggered wave with height/color/blur ramp | Growth claims, data metrics, statistics |
| 07 | **Phone Screens** | 3D phone with gentle feed scroll & expanding concentric rings | Product demo, app preview, UI showcase |
| 08 | **Frame Break** | Character breaks frame border; poster shatters into 5x5 tiles | Mid-video pattern interrupt, surprise punchline |
| 09 | **Pullback** | Camera starts macro on 1 row, cranes up to reveal entire grid | Detail-to-macro reveal, "the big picture" |
| 10 | **Glitch** | 8-frame RGB split and horizontal sliced jitter bands | Section change, error/glitch reveal, beat drop |
| 11 | **Typewriter** | Monospace terminal typing with blinking cursor & sync clicks | Call-to-action, code build, closing punchline |

---

## Detailed Effect Catalog & Remotion Prompts

### 01. Orbit
- **What it is:** A tall 3D phone mockup flies up through the frame, rotating subtly in 3D perspective while its inner screen feed scrolls at high blur speed. A bright floating label rides pinned to the top edge.
- **When to use:** The first 0–2 seconds of a short-form video (Reels, TikTok, Shorts) to break user scrolling inertia.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A 3D phone flies up the frame and turns slowly while its feed of blurred tiles scrolls fast. A bright label rides on the phone's top edge.
  ```
- **Remotion Implementation Notes:**
  - Container with `perspective: 1200px`.
  - Phone wrapper animated with `spring({ frame, fps, config: { damping: 12, mass: 0.8 } })` on `translateY` and `rotateY` (e.g. -15deg to +5deg).
  - Feed container uses `translateY` with `filter: blur(4px)` during flight, settling into crisp focus.

---

### 02. Vertigo (Hitchcock Dolly-Zoom)
- **What it is:** Classic "Vertigo" / dolly-zoom optical illusion. The focal subject (card or badge) remains identically sized on screen while the camera perspective pulls back, stretching an infinite corridor of surrounding wall/floor/ceiling cards into deep 3D perspective.
- **When to use:** A moment of realization, a critical problem statement, or a headline you need the viewer to remember.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A long corridor of cards lines the walls, floor and ceiling, receding to a glowing vanishing point. Keep the center card the same size while the camera dollies back.
  ```
- **Remotion Implementation Notes:**
  - Counteract camera retreat (`translateZ` or `scale` of world) by scaling the focal element inversely: `subjectScale = 1 / cameraScale`.
  - Four planes (left wall, right wall, ceiling, floor) positioned with CSS 3D transforms (`rotateY(90deg)`, `rotateX(90deg)`).

---

### 03. Zoom-through Transition
- **What it is:** High-velocity crash zoom that plunges straight into the center tile of a grid, dissolving/passing through its glass surface to seamlessly emerge inside a secondary illuminated layout.
- **When to use:** Transitioning between major concepts without a plain cut or slide.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion transition. In 6 frames, crash-zoom into the center tile, pass through its surface as if it were a window, and land in a second lit grid behind it.
  ```
- **Remotion Implementation Notes:**
  - Fast curve across exactly 6 frames (or 0.2s).
  - Rapid scale from `1.0` to `18.0` with `opacity` dropping to 0 at frame 4. Scene 2 scales down from `2.5` to `1.0` and fades in from frame 3.

---

### 04. Headlines (Wall of Press)
- **What it is:** A bold 3D wall tilted along the X/Y axes displaying four columns of high-contrast headline cards. Alternate columns scroll continuously in opposite directions (column 1 & 3 scroll up, column 2 & 4 scroll down).
- **When to use:** Establishing social proof, showing market consensus, or visualizing press coverage.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A wall tilted back in 3D holds four columns of bold headline cards. Scroll neighboring columns in opposite directions. Headlines: [your headlines].
  ```
- **Remotion Implementation Notes:**
  - Parent wrapper: `transform: perspective(1000px) rotateX(20deg) rotateZ(-5deg)`.
  - Staggered loop using `frame * speed % columnHeight` for endless seamless looping.

---

### 05. Paper Cut
- **What it is:** A tactile, physical stop-motion aesthetic. A warm cream textured paper sheet slaps onto a dark background with an organic elastic bounce, after which typography stamps onto it sequentially like a mechanical letterpress.
- **When to use:** Breaking visual fatigue in dark-mode videos; introducing key quotes, warnings, or human truths.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A cream paper sheet slaps down on a dark stage with a small bounce. Press these words onto it one at a time like a letterpress, in sync with the voice: [your words].
  ```
- **Remotion Implementation Notes:**
  - Sheet entrance: `spring({ frame, fps, config: { damping: 10, mass: 0.5, stiffness: 180 } })`.
  - Words rendered with subtle ink bleed shadow: `text-shadow: 0 1px 0 rgba(0,0,0,0.4)` and snappy opacity/scale stamp.

---

### 06. Charts (Staggered Wave)
- **What it is:** A sleek dark-mode analytics dashboard where 16 vertical data bars grow from the bottom baseline in a rapid cascading wave. Bars dynamically shift height, color hue, and glow/blur across the sequence.
- **When to use:** Demonstrating revenue growth, performance benchmarks, user adoption, or KPI spikes.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A dark dashboard panel where 16 bars grow from the baseline in a staggered wave. Height and color build from first bar to last, and a second wave follows.
  ```
- **Remotion Implementation Notes:**
  - Map across 16 bars with `delay = index * 2` frames.
  - Height interpolated with `spring` or cubic bezier easing (`scaleY` with `transform-origin: bottom`).

---

### 07. Phone Screens & Ripples
- **What it is:** Floating 3D mobile mockup showcasing a fluidly animated user experience. Concentric radar-like pulses or ripples emit from behind the device, while contextual annotations/labels pop up on the flanks.
- **When to use:** Product demos, mobile UI features, or user testimonials.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A 3D phone in the center shows a gently scrolling feed, with concentric rings breathing out from behind it. Small labels pop in on each side: [your labels].
  ```
- **Remotion Implementation Notes:**
  - 3–4 concentric SVG circles or div borders expanding from `scale(0.8)` to `scale(2.2)` with decaying opacity (`1 -> 0`).
  - Staggered timing on left/right annotation pills.

---

### 08. Frame Break
- **What it is:** A framed artwork or poster containing a character/graphic. The subject leans forward and breaks through the border into outer space; the surrounding frame shatters into a 5x5 grid of 25 spinning fragments.
- **When to use:** Pattern interrupt, shocking twist, comedic beat, or disruptive product claim.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A character inside a framed poster leans past the edge, then bursts through. The poster cracks into a 5x5 grid of tiles that spin away from the center.
  ```
- **Remotion Implementation Notes:**
  - 5x5 CSS grid where each tile gets calculated trajectory `(x - centerX, y - centerY)` multiplied by force.
  - Z-index layering: Character pops to top z-index as tiles disperse in 3D.

---

### 09. Pullback (Macro to Micro)
- **What it is:** Camera starts extremely close on a single card row or line item, then rapidly cranes up and backward, flooding the frame with dozens of rows and columns to expose the massive scale of a full matrix.
- **When to use:** Transitioning from an individual detail/feature to the comprehensive platform view.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. Start tight on one row of a dark grid and crane up fast so row after row floods in, until the whole board of cards fills the frame.
  ```
- **Remotion Implementation Notes:**
  - Camera `scale` moves from `3.5` down to `1.0`, `translateY` moves synchronously from target row offset to `0`.

---

### 10. Glitch (RGB Split & Slice)
- **What it is:** High-energy digital glitch lasting 6–10 frames. The image slices into uneven horizontal ribbons that jitter horizontally, coupled with red/cyan chromatic aberration and scanline interference, snapping back clean.
- **When to use:** Hard scene cut, exposing an error/myth, or landing a hard sound effect/bass drop.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion transition. For 8 frames, split the red and blue channels and slice the image into horizontal bands that jump sideways, then snap back clean.
  ```
- **Remotion Implementation Notes:**
  - CSS `clip-path: polygon()` horizontal slices with random `transform: translateX(Npx)`.
  - Color split via `mix-blend-mode: screen` with red and cyan translated copies.

---

### 11. Typewriter (Terminal Build)
- **What it is:** Minimalist, retro or high-tech terminal window. A command or punchline types out character-by-character at variable human speeds, backed by a blinking block/bar cursor and frame-accurate click timing.
- **When to use:** Final CTA, code terminal demos, developer messaging, or closing punchlines.
- **Claude / Remotion Prompt:**
  ```text
  Build a Remotion scene. A terminal window where this line types out at a natural speed with a blinking cursor, and each keystroke is timed for a click sound: [your line].
  ```
- **Remotion Implementation Notes:**
  - `text.slice(0, Math.floor(frame / framesPerChar))`.
  - Blinking cursor: `Math.floor(frame / 15) % 2 === 0 ? '█' : ' '`.
  - Pair each character advance with an audio tick from the SFX library.

---

## Best Practices for Remotion Generation

1. **Deterministic Frames**: Always calculate animations from `useCurrentFrame()` and `useVideoConfig()`. Never use `setInterval`, `requestAnimationFrame`, or CSS keyframe animations without frame locking.
2. **Smooth Physics**: Use Remotion's built-in `spring()` for all natural momentum (damping: 10–14, mass: 0.8–1.2).
3. **Sound Synchronization**: Pair impacts (the Paper Cut slap, Glitch hit, Typewriter keystroke, Orbit whoosh) with corresponding SFX via the global SFX pipeline (`openverse-sfx` / `real-sfx`).
