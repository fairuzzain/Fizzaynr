# Prompts - editorial collage motion graphic

Source: ANDR3 AI, "AI Motion Graphics Videos" (X article, 24 Jun 2026). Their chain is
Pinterest "collage art" refs → ChatGPT as creative director → Gemini Omni in Google Flow → 2+ takes →
best parts combined in an editor. Here Claude is the creative director and Nexabot (Veo) renders.

## 1. Creative-director pass (Claude does this, no tool)

Look at every style reference and write `style.md` for the run: the visual language described
**directly**, as if already fully understood. Never write "reference", "uploaded image", "style
reference" or "based on the references" in style.md or in any clip prompt - Veo has never seen them.

Cover, in concrete words (materials, colours, edges, how things move):
- Animation - frame rate feel, jitter, how objects swap and reposition
- Typography look (Veo will NOT draw it - it is added in post; style.md only says where labels sit)
- Camera - zooms, punch-ins, whip pans, pullbacks, board rotations, macro texture shots
- Movement - how paper, tape, photos, cutout heads and the paper puppet move
- Texture - halftone, paper grain, torn edges, tape, stamps, drop shadows
- Mood and palette (2-4 colours, one main accent)

No references given → use the default style below unchanged.

### Default style (from the source article)
- **Animation:** agile stop-motion at 12 frames per second, no motion blur, snappy frame-by-frame
  movement, intentional handmade jitter, fast object swaps and paper repositioning.
- **Camera:** dynamic fast zooms, punch-ins, whip-pan transitions, crash zooms, snap pullbacks,
  rotating collage-board transitions, close-up macro shots of paper texture, tape, stamps and cutout edges.
- **Movement:** organic paper cutout motion, visible drop-shadow shifts, stop-motion layer sliding,
  Polaroid frames slapping onto the board, torn-paper wipes, tape strips peeling and snapping down,
  cutout heads bouncing, rotating and scaling, a full-body paper character moving like a puppet.
- **Mood:** highly energetic, bold, tactile, cinematic editorial; fast, playful, premium, handmade.
- **Palette:** off-white paper, charcoal black, electric yellow accents; occasional muted red or teal
  only for contrast, yellow stays the main accent.
- **Typography (post, not Veo):** fast kinetic pop-ups, bold condensed type, stamp texture,
  word-by-word impact timing, oversized editorial headlines, paper-label captions, black ink on
  electric yellow.

## 2. Scene plan (the article's OUTPUT list, one row per beat)

For every beat (≈ 6-9 s of voice-over, one Veo clip) decide:
shot · composition · camera move · object movement · character treatment (floating head cutout /
full-body paper puppet / Polaroid frame / none) · transition into the next beat · texture focus ·
the 1-3 emphasis words that pop in post · timing (where in the beat the hit lands).

Vary the character treatment across beats: open on a floating head, use the full-body puppet for
action lines, the Polaroid for "proof"/memory/fact lines, macro texture shots as breathers.

## 3. Clip prompt template (one per beat)

```
STYLE: Premium editorial paper-collage motion graphic, agile stop-motion at 12 frames per second,
no motion blur, snappy frame-by-frame movement with handmade jitter. <palette + texture lines from style.md>.

IDENTITY: <only when a presenter photo is attached> The person is the exact same person shown in the
attached photo - same face, age, ethnicity, facial structure, hairstyle and facial hair. Extract their
face and body from the photo and reuse that identity in every cutout, floating head, Polaroid and
paper puppet; keep the face recognisable even with halftone and paper texture. Never invent a new face.

SHOT: <composition, what is on the board, character treatment, object movement, beat by beat
inside the ~8 s clip: 0-3 s ..., 3-6 s ..., 6-8 s ...>

CAMERA: <one main move + one snap, e.g. "slow push-in, then a crash zoom onto the cutout head at 5 s">

TRANSITION OUT: <torn-paper wipe / whip pan / board rotation / tape snap>

AUDIO: paper rustle, tape snaps, soft stop-motion clicks, light whooshes on the moves. No voice, no music.

AVOID: readable text, letters, numbers, logos, captions, subtitles, watermarks; plain unprinted paper
labels and blank stamps only. No smooth 3D render, no motion blur, no extra people, no face changes.
```

Rules:
- Keep "no readable text" in every prompt: Veo garbles words and starts adding stray labels after
  ~4-5 s. All words are added in post by `build.py`.
- One camera idea per clip. Describe actions with times; Veo follows 2-3 timed actions well, not 6.
- Safety-filter rejection (refunded): reword neutrally and resend.
- Presenter beats use `i2v` with the presenter photo only (a clean photo, no text on it - `i2v` copies
  text from ingredient images). Beats without the presenter use `sfv` from a text-free Nexabot `img`
  start frame (prompt: the board composition, "no text, no letters").

## 4. Two takes

The article's key habit: generate at least two versions and keep the best of each. Default is
**2 takes per beat** (`s01_a`, `s01_b`), the same prompt with one line changed (camera move or
treatment). Pick per beat from the contact sheets; you can use part of each take.
