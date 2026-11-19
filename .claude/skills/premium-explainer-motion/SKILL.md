---
name: premium-explainer-motion
description: Creates polished, non-flat explainer videos in Claude workflows using purposeful cinematic motion, kinetic typography, animated data, counters, scribble/draw-on effects, liquid fills, and expressive object transitions. Use when planning, prompting, improving, or troubleshooting explainer videos and motion graphics.
---

# Premium Explainer Motion Skill

## Mission
Create explainer videos that feel intentionally art-directed and professionally animated—not like static slides with images drifting across the screen. Every motion choice must clarify the narration, communicate emotion, or move the story forward.

## 1. Reference and brief intake
- If the user provides a reference image or video, identify what it represents:
  - Image = character, object, or visual-style reference.
  - Video = motion, pacing, transition, typography, and editing reference.
  - Image + video = combine the image's identity/assets with the video's motion language.
- Ask for missing essentials only when needed: topic, objective, audience, platform, duration, narration, CTA, visual assets, and style reference.
- If a user already has a clear idea, collect the brief in one compact template rather than asking many questions one at a time.
- Keep the supplied narration verbatim unless the user explicitly requests rewriting. Do not add, remove, translate, or improvise spoken words when voice lock is required.

## 2. Anti-flatness principles
- Do not treat a scene as one static composition. Build motion in layers: foreground, subject, supporting objects, typography, and background/parallax where appropriate.
- Give the viewer a meaningful visual change roughly every 1–3 seconds, while allowing a strong moment to breathe when the story needs it.
- Each scene should contain purposeful camera movement, character/object action, foreground or layered movement, a clear transition, and one memorable visual payoff (WOW moment). Do not force every technique into every scene.
- Use varied rhythm: anticipation, acceleration, impact, pause, and release. Sync key changes to narration and music accents when available.
- Prefer object-driven transitions (an object crosses frame, expands, wipes, transforms, or reveals the next scene) over generic fades.
- Motion must have weight and easing: anticipation before a move, acceleration, overshoot only when appropriate, and a clean settle. Avoid robotic linear movement.
- Avoid gratuitous movement. Every motion should support meaning and hierarchy.

## 3. Advanced Motion Graphics Toolkit
Choose techniques based on the meaning of the narration. Use a few well-executed techniques per scene; do not cram every effect into every scene. State the actual movement and timing in prompts rather than merely naming an effect.

### A. Data Visualization Animation
Use for quantities, comparisons, progress, evidence, trends, and cause/effect.
- Animate bars growing, line graphs drawing on, pie/donut segments filling, charts assembling from axes, and markers traveling along a path.
- Let values count up/down and labels appear in sync with the data.
- Explain what each axis/value means; never invent statistics. If the narration has no data, use a clearly metaphorical visual rather than presenting made-up numbers as facts.
- Example direction: "The bar grows from baseline to the narrated value in 1.2 seconds; the value counts up in sync, then the final bar gives a subtle impact bounce."

### B. Number Counters, Odometers, and Speedometer Motion
Use for counting, speed, elapsed time, workload, milestones, or urgency.
- Animate digital counters, rolling odometer digits, ticking counters, stopwatch hands, and speedometer needles.
- Use only numbers supported by the brief/narration, unless explicitly framed as a symbolic, non-factual illustration.
- Specify start value, end value, duration, easing, and final hold when known.
- Example direction: "The stopwatch hand sweeps rapidly; digits roll upward and snap to a stop on the spoken number, with a short impact and settle."

### C. Scribble, Draw-On, and Whiteboard Accents
Use for emphasis, annotation, discovery, and playful editorial energy.
- Animate hand-drawn lines being written on, circles tracing around a key word/object, underlines drawing left-to-right, arrows sketching into place, and brief cross-outs or check marks.
- Use restrained strokes that feel intentional and legible; coordinate them with the exact narration beat.
- Do not obscure the character, important object, or readable text.
- Example direction: "A coral scribble draws itself around the phrase as it is spoken; a hand-drawn arrow follows and lands on the object."

### D. Liquid Fill / Rising Level Animation
Use to represent filling capacity, growing workload, increasing pressure, progress, or reaching a limit.
- Animate liquid rising visibly from the bottom of a transparent container, bottle, meter, or silhouette; add a gently oscillating surface, small bubbles, and a clear final level when appropriate.
- Make the rising level continuous and easy to read. The container should stay stable while the liquid surface rises; use clipping/masking so the fill stays inside the shape.
- Match the metaphor to the narration. For workload, the liquid can rise toward the rim; for progress, it can fill a gauge. Do not imply literal facts when it is only a metaphor.
- Example direction: "A clear glass fills from 10% to the brim over 2 seconds; the waterline ripples slightly, two bubbles rise, and the final level holds as the narration lands."

### E. Kinetic Typography
- Animate key words with scale, position, tracking, masking, rotation, or staggered character/word reveals.
- Use only short keyword phrases, usually 2–5 words on screen at once. Avoid long paragraph overlays.
- Choose a typographic motion that reflects meaning: a heavy word lands with impact; a delicate word draws on; a question reveals in stages.
- Maintain readability, contrast, safe margins, and consistent type hierarchy.

### F. Shape Morphing and Icon Animation
- Transform one shape or icon into another when the relationship is understandable: home → calendar → clock, for example.
- Use pop, bounce, squash-and-stretch, rotation, path motion, and controlled morphing with consistent design language.
- Avoid random icon confetti or transformations that do not connect to the story.

### G. Object-Driven Transitions and Motion Collage
- Move objects across the frame to wipe/reveal the next scene; scale an object until it fills the frame; transform an object into the next visual; or use foreground elements for depth.
- Combine layered cutout assets with parallax and independent movement.
- Use transitions to connect ideas, not just decorate cuts. Specify what crosses the frame, direction, speed, and what it reveals.
- For faceless cartoon assets on transparent backgrounds, animate each character/object as an independent cutout layer where possible. Keep the character's proportions and identity consistent.

### H. Motion Accents and Impact
- Use speed lines, burst shapes, squash-and-stretch, short camera punches, controlled shake, impact rings, and elastic settling when motivated.
- Use sparingly to emphasize a reveal, surprising fact, or key phrase. Avoid constant bouncing and noisy sticker overload.

## 4. Kinetic text and graphic timing
- Align text and graphic motion with the exact phrase being spoken.
- Use short on-screen keywords rather than duplicating the full voice-over.
- Give important words a clear entrance, readable hold, and exit; do not flash text so quickly that it cannot be read.
- If no text is needed, communicate the idea with animated objects, charts, or visual metaphor instead.
- Never add unsupported statistics, claims, labels, or numbers.

## 5. Reference-video analysis
When a reference video is supplied, analyze its visual language before writing prompts:
- shot length and pacing;
- camera moves and framing;
- kinetic typography style;
- graphic and data-animation techniques;
- transitions and wipes;
- color, line weight, texture, lighting, and depth;
- sound design and sync points if audible.
Extract reusable style principles without copying unrelated content. State which qualities should be carried into the user's video.

## 6. Scene construction and continuity
- Build a scene-by-scene plan that matches the requested total duration.
- Each scene should normally last 8–10 seconds unless the user's format or exact timing requires a different length. Shorter internal beats can change every 1–3 seconds.
- Each scene must move the story forward and contain one clear visual payoff.
- Maintain continuity of characters, objects, color, lighting, motion direction, and emotional tone.
- Explain how the end of each scene transitions into the next.
- Keep all prompts concrete and production-oriented: subject + action + camera + layered motion + graphic technique + timing + transition + continuity.

## 7. Character and asset consistency
- For character reference images, preserve identity and visible attributes: face or faceless design, age, gender presentation, hairstyle/hijab, skin tone, outfit, accessories, and body proportions as applicable.
- For faceless cartoon cutouts, preserve the faceless look in every shot; do not generate eyes, nose, or mouth. Keep outlines, palette, proportions, and shading consistent.
- For transparent assets, request isolated subjects with no scenery or background. If transparency cannot be guaranteed, say so and suggest a transparent PNG workflow rather than pretending the background is transparent.
- Do not regenerate a different character between scenes.
- Use foreground/background movement only when it adds depth; a transparent asset itself should remain clean and separable.

## 8. Audio and timing
- Keep narration exactly as supplied when voice lock is requested.
- Specify where music builds, where impacts/whooshes occur, and when effects should stop so dialogue remains clear.
- Avoid sound effects on every movement. Use selective whooshes, ticks, marker sounds, liquid sounds, and impacts when they support the action.
- Ensure scene timings add up to the requested total duration. Do not claim exact duration, frame rate, resolution, or export settings have been verified unless the actual render/export has been inspected.

## 9. Production honesty
- Distinguish between a prompt/specification and a rendered video. Do not claim to have produced or verified an MP4 unless an actual file was generated and checked.
- If the target tool may not support complex masking, exact timing, layered compositing, or reliable text, provide a practical fallback: separate transparent assets, simple graphic elements, or post-production instructions.
- Prefer effects that can actually be executed by the user's tool; specify an alternate implementation if a requested effect is unreliable.

## 10. Quality-control checklist
Before finalizing the plan/prompts, verify:
- Is there meaningful visual change every 1–3 seconds?
- Does each scene include a distinct visual payoff?
- Are camera, character, object, typography, and foreground motions explicitly described?
- Are chart values factual or clearly metaphorical?
- Are counters using supported values?
- Are scribbles/draw-on strokes timed to narration and legible?
- Does a liquid fill visibly rise and remain inside the container?
- Does each transition connect the story to the next scene?
- Is on-screen text concise and readable?
- Are character and visual styles consistent?
- Do scene durations sum to the target runtime?
- Are tool limitations and unverified output settings stated honestly?

## 11. Recovery mode: "the video feels flat"
When the user says a result feels flat, do not simply add more camera movement. Diagnose the visual rhythm and revise:
1. Replace static layouts with staged reveals and object interactions.
2. Add a few relevant advanced techniques: animated chart/counter, draw-on scribble, liquid fill, kinetic type, morph, or object wipe.
3. Add depth with foreground layers and parallax where appropriate.
4. Improve timing: anticipation → action → impact → readable hold → transition.
5. Tie every effect to a specific narration phrase.
6. Remove random effects and repetitive transitions.
7. Provide a revised scene prompt with exact action, approximate timing, and continuity.

## 12. Default output format
Unless the user requests another format, respond with:
1. Creative Direction
2. Selected Style
3. Editing Direction
4. Scene Breakdown
5. Separate production-ready prompt for each scene, including:
   - Scene number and duration
   - Character/asset lock
   - Voice/narration lock
   - Visual direction
   - Character performance
   - Camera direction
   - Motion direction
   - Graphic/motion technique
   - Transition
   - Text on screen
   - Negative prompt
   - Continuity

## Negative prompt baseline
Avoid slideshow layouts, PowerPoint aesthetics, flat/static compositions, static camera, frozen characters, weak transitions, generic AI animation, inconsistent character identity/outfit/lighting, excessive text, random stickers, robotic movement, unsupported data, illegible typography, and effects unrelated to narration.

## 13. Effect Library: 10 Practical Explainer Effects
Use this library when planning a scene. Pick effects that serve the story; do not force all ten into every video. For every chosen effect, specify the subject, movement, direction, approximate timing, easing/impact, narration cue, and transition/continuity.

### 1. Text Behind Object
**Purpose:** Create depth by placing typography behind a foreground character or object.
**Execution:** Separate the foreground subject from the background with a mask/rotoscope or use a layered cutout asset. Place text between the background and subject so the subject visibly occludes part of the text. Animate text with a restrained slide, scale, or reveal.
**Example:** A faceless cartoon character stands in front of the large words “TAK KENAL WAKTU”; the body naturally covers part of the lettering.
**Fallback:** If reliable masking is unavailable, use a pre-cut transparent character PNG over the text instead of asking the generator to invent accurate occlusion.

### 2. Zoom In / Zoom Out
**Purpose:** Guide attention, reveal context, or change emotional distance.
**Execution:** Animate virtual camera framing or scale smoothly with easing. Zoom in toward a meaningful detail; zoom out to reveal the wider composition. State the start framing, target, direction, and approximate duration.
**Example:** Begin with the whole house, then move closer to a pile of laundry as the narration mentions workload.
**Avoid:** Repeating identical zooms in every scene.

### 3. Snap Zoom
**Purpose:** Deliver a quick, emphatic attention shift or surprise.
**Execution:** Use a very fast punch-in or punch-out, optionally with brief motion blur, impact, and a tiny overshoot before settling. Keep the focal target clear and readable.
**Example:** On the spoken question “Bukan pekerjaan?”, snap-zoom to a large question mark.
**Distinction:** A snap zoom is abrupt and punchy; a standard zoom is smoother and more gradual.

### 4. Pop-Up Chat
**Purpose:** Introduce a question, comment, message, or social reaction.
**Execution:** Bring a chat bubble in from a clear direction, scale it from small to full size with a subtle bounce, and hold long enough to read. Add typing dots or a notification only if useful.
**Example:** A bubble appears: “Emangnya ibu rumah tangga kerja?”
**Text rule:** Keep each message concise and avoid fake platform branding unless requested.

### 5. Chat Takeover
**Purpose:** Turn a chat bubble into a full-frame transition or visual reveal.
**Execution:** Start with one or more small bubbles, expand one until it covers most or all of the frame, then reveal the next scene through the expanding shape or its color. Specify the exact direction and what the takeover reveals.
**Example:** The question bubble expands to fill the screen, then transforms into a montage of household tasks.
**Distinction:** Pop-Up Chat remains an overlay; Chat Takeover takes over the composition and transitions scenes.

### 6. Checklist Pop
**Purpose:** Show a sequence of tasks, steps, or completed items quickly.
**Execution:** Reveal checklist rows one at a time. Animate each checkmark with a draw-on stroke or short scale-pop, with a slight stagger between rows. Keep the list readable.
**Example:** “Memasak ✓”, “Mengurus anak ✓”, “Membersihkan rumah ✓”, “Mengatur keuangan ✓”.
**Avoid:** Showing so many items at once that the viewer cannot read them.

### 7. B-Roll Overlay
**Purpose:** Add supporting visuals while preserving the main subject or narrative context.
**Execution:** Layer short supporting footage, illustrations, or transparent cutout assets over or beside the main scene. Use clear entrances/exits, consistent visual style, and independent motion where possible.
**Example:** While a character narrates, cooking, laundry, and childcare cutouts appear in sequence around them.
**For transparent cartoon assets:** Treat each cutout as an independent layer so objects can move separately.

### 8. Growth Curve
**Purpose:** Visualize growth, accumulation, progress, or an increasing trend.
**Execution:** Draw a curved line from its starting point, animate a marker along it, and reveal supporting labels or icons in sync. Use real values only when sourced; if the curve is metaphorical, make it clear it is illustrative rather than factual.
**Example:** A curve rises as icons representing household tasks accumulate throughout the day.
**Fallback:** If precise path animation is unavailable, use a sequence of growing bars or a simple line reveal.

### 9. Orbit
**Purpose:** Create circular motion, dimensionality, or show multiple elements connected to a central subject.
**Execution:** Specify whether the camera or the objects are orbiting. For object orbit, animate icons around a central character on a controlled circular path with subtle scale/depth changes. For camera orbit, describe the arc and what stays in focus.
**Example:** Icons for dishes, laundry, a clock, and money orbit a faceless cartoon housekeeper to represent many responsibilities.
**Avoid:** Unmotivated spinning or orbiting that distracts from the narration.

### 10. Glow Body Effect
**Purpose:** Highlight a character or communicate a meaningful emotional or symbolic shift.
**Execution:** Apply a controlled outer glow or luminous outline to the character silhouette, then animate its intensity gently (fade-in, pulse, or fade-out). Keep facial/character design and outfit unchanged. Choose color to fit the scene's emotion.
**Example:** A warm golden outline appears around the character as the narration emphasizes the value of domestic work.
**Fallback:** If the video model cannot keep a glow attached to the silhouette, use a separate transparent outline/glow layer in compositing.

## Effect Selection and Prompting Rules
- Select only effects that clarify a particular narration beat or visual idea; a few well-executed effects are stronger than all ten used indiscriminately.
- State the effect name and its actual visual behavior. Do not rely on the effect label alone.
- Include approximate timing, direction, easing, focal point, layering/masking needs, and how the effect ends or transitions.
- Preserve readable text and stable character identity during fast moves.
- Keep the design language consistent across effects: palette, stroke width, typography, shadows, and motion character.
- Be honest about generation limitations. If accurate masks, path animation, or compositing are unreliable, specify a separate-layer or post-production fallback.
