# Motion rules (Mode A / HyperFrames) — read before writing any timeline

These rules make code-only videos move like a motion designer made them, not like a slide deck. They override any ease, transition or "fade in" mentioned in a style recipe or reference file. A style's *signature* (what it looks like) stays; only *how things move* follows this file.

Numbers below are distilled from frame-by-frame measurements of professional motion pieces (public findings from the open-source motionmaxxing project, Apache-2.0), rewritten and adapted for 9:16 shorts.

## 1. Ease presets (paste at the top of every timeline script)

```js
// 30 fps. Author timing in FRAMES, convert with F().
const FPS = 30, F = n => n / FPS;
const E = {
  land:    "power3.out",    // DEFAULT entry: decelerates into place (10–12 f)
  soft:    "power2.out",    // calm entry for big panels, backgrounds, body text (12–16 f)
  snap:    "expo.out",      // fast hit: keyword, number, logo slam (6–9 f)
  settle:  "back.out(1.15)",// tiny late lean past the mark — HERO element only
  exit:    "power2.in",     // leaving accelerates away (6–9 f)
  throw:   "power4.in",     // hard exit before a cut, whip-out (5–7 f)
  move:    "power2.inOut",  // repositioning / camera moves between two rests
  drift:   "none",          // slow constant camera drift / parallax under a scene
};
```

Timing defaults (30 fps):

| What | Frames | Seconds | Ease |
|---|---|---|---|
| Typical element entry | 10–12 | 0.33–0.40 | `E.land` |
| Keyword / number hit | 6–9 | 0.20–0.30 | `E.snap` |
| Element exit | 6–9 | 0.20–0.30 | `E.exit` |
| Opacity (when used at all) | 5–7 | 0.17–0.23 | `E.land` |
| Blur in/out | 7–8 | ~0.25 | `E.land` |
| Stagger between items | 2–4 | 0.07–0.13 | — |
| Camera move between rests | 18–30 | 0.6–1.0 | `E.move` |
| End hold (final frame resolved) | 18–42 | 0.6–1.4 | — |

## 2. The five laws

1. **Land decelerates, leave accelerates.** Every entry ends slow (`E.land`, `E.snap`, `E.soft`). Every exit starts slow and speeds away (`E.exit`, `E.throw`). The same element on the wrong curve looks floaty or thrown. Never use an `.out` ease for an exit or an `.in` ease for an entry.
2. **Overshoot is rare.** At most ~1 in 10 moves may overshoot, and only the hero of a scene (the logo, the big number, the reveal). Use `E.settle` (a small, late lean), never `elastic`, never `back.out(2+)`, never `bounce` — except styles whose signature is bouncy (96 Kawaii, 52 Meme, 32 Stickman physics, 86 Bata mainan) and even there keep it to hero beats.
3. **Nothing grows from zero.** No `scale: 0 → 1`. Things arrive by:
   - decelerating from *larger* than life (`scale: 1.6–3.5 → 1` with `E.snap`; logos/big words crash in from ~3×), or
   - moving in from off-frame or from behind a mask (`y: 120 → 0`, `x: -1080 → 0`, `clipPath` wipe), or
   - being revealed by a draw-on / mask / split.
   Small things (icons, chips) may start at `scale: 0.7` if they also move. Particles/sparks are exempt.
4. **Move, don't fade.** Elements arrive by transform (x, y, scale, rotation, clipPath, mask). Opacity is a helper that rides along for a few frames (`opacity: 0→1` over 5–7 f *together with* a move), not the entrance itself. Aim for at least 4 transform entries for every 1 opacity-only entry. Never dissolve whole scenes.
5. **No dead frames.** Something moves on almost every frame. Under every scene keep a slow layer going (`E.drift` camera push 1.00→1.04, parallax, background gradient shift, grain). A still run longer than ~0.4 s mid-video is a bug unless it is a deliberate beat (silence before a punchline, max 2–3 per video, ≤ 0.5 s).

## 3. Cuts and transitions

- **Default scene change = hard cut on motion.** The outgoing scene is still moving when it cuts (end its last tween *after* the scene's `data-duration` ends, or throw an element out with `E.throw` across the cut), and the incoming scene starts already moving (its first tween starts at frame 0 of the scene, not after a pause).
- Hard cut is ~90% of scene changes. Use a *designed* transition (whip, zoom-through, match-cut, flash, wipe) on **at most 2–3 key moments** per video: hook → body, the reveal, body → CTA. Not on every cut.
- No fade-to-black or cross-dissolve between beats unless the style's signature asks for it (19 Siluet senja, 4 Dokumentari, 18 Filem bisu — and only at act breaks).
- Cut on the beat: place cuts on music beats / VO phrase starts (`vo_segments.py`), so motion and sound land together.
- The ending gets *smaller* and calmer: last scene resolves, holds 0.6–1.4 s, no long static end card (the QA script fails > 1.4 s).

## 4. Composition (anti-slop)

These are the most common "AI video" tells. Avoid them unless the style's signature is literally that element (see exemptions in the lint).

- **No page chrome:** no brand/label text parked in a corner, no "02 / 05" scene counters, no fake timecodes, corner brackets, header/footer bars, or progress bars.
- **No deck layouts:** no kicker (small tracked-caps line) above a headline, no "headline block on the left + card/phone on the right" repeated scene after scene. Make the type or the object *be* the picture: full-bleed type, one hero element filling ≥ 55% of the frame width.
- **One hero per frame.** Two panels only if one is at least twice the other's area, or the camera moves between them.
- **No letter-by-letter typed headlines** (typewriter + caret). Reveal words or lines instead. Typing is only for styles that are literally typing (3 Fake chat, 60 Phone/Google search, 61 Terminal, 65 Win95, 72 Thread post, 15 Reddit).
- **No vibe-coded UI cards:** rounded grey card + status dot + "label · value" rows + "Good morning" header. If a UI is needed, draw a specific, believable one for the topic.
- **Grounds are surfaces, not swatches:** a background has light (gradient, glow), depth (blur layer, shadow) or texture (grain, paper, halftone). Don't switch to a different flat colour every scene.

## 5. Patterns (copy and adapt)

```js
// Entry: moves in, decelerates, opacity rides along briefly
// (two tweens: the move takes 11 f, the opacity is done after 6 f)
tl.fromTo(el, {y: 110}, {y: 0, duration: F(11), ease: E.land}, t);
tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: F(6), ease: E.land}, t);

// Hero crash-in from oversize (logo / big number)
tl.fromTo(hero, {scale: 3, opacity: 0}, {scale: 1, opacity: 1, duration: F(9), ease: E.snap}, t);
tl.to(hero, {scale: 1.03, duration: F(40), ease: E.drift}, t + F(9));   // keep it alive

// Exit accelerates away, ideally across the cut
tl.to(el, {y: -140, opacity: 0, duration: F(7), ease: E.exit}, sceneEnd - F(4));

// Word stagger (no typewriter)
tl.fromTo(words, {y: 60, opacity: 0}, {y: 0, opacity: 1, duration: F(10), ease: E.land, stagger: F(3)}, t);

// Camera drift under every scene
tl.fromTo(sceneCam, {scale: 1}, {scale: 1.045, duration: sceneDur, ease: E.drift}, sceneStart);
```

## 6. Checks

- Before render: `python <skill>/scripts/slop_lint.py index.html --style <N>` — fix every ERROR; WARN = look again.
- After render: `python <skill>/scripts/look.py <slug>.mp4 --expect-duration <s> [--audio]` — fix every FAIL, then re-render. Quote its numbers in the final summary in one line (e.g. "QA: still max 0.23 s, end hold 0.9 s, 14 cuts").
