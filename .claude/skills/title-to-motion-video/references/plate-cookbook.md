# Plate cookbook — proven visual devices in the template

Each template plate (`C:\Users\fairus\Documents\Motion_as_kit\app\src\scenes\<file>.ts` — the
template, since projects delete their copies in Stage 5) is a working implementation you can copy
and adapt. Match a script beat to the device that fits it, open that file, and reuse the code —
then replace all of its `lineOf`/`wordOf` lookups and template-specific numbers for the new script.
The look is consistent: ink black or bone paper, one signal-orange accent, graph paper, a plotter
pen whose head is the spark, karaoke type that lights on the spoken word.

| Device | What it looks like | Good for | Source |
|---|---|---|---|
| **Bookend** | Black, crop marks, the spark at rest in the centre; flares on the first word | First/last frame (loop) | `hook.ts` A, `verdict.ts` `fin` |
| **Plotter lettering** | Single-stroke text written by the pen word by word | Opening question, handwritten emphasis | `hook.ts` A (`writeWords`) |
| **Kinetic word slam** | A word lands full-frame, steps through Archivo widths/weights, punch-in + shake | Key nouns, the punchline | `hook.ts` B, `crazy.ts` A, `verdict.ts` `drawSlam` |
| **Cross-out** | A familiar UI (timeline, diagram) slides in; the pen strikes it in orange | "without X", "not X" | `hook.ts` C/D |
| **Node diagram** | Hairline boxes + arrows with packets running; a link snipped on "not" | Systems, A→B→C relationships, negation | `hook.ts` D, `crazy.ts` B |
| **Title card + odometer** | Name slams, a number rolls digit by digit per spoken part, spec table types itself | Introducing a product/version/stat | `model.ts` A |
| **Two columns** | Old way (dimming, manual jerks) vs new way (typed as said) | Comparisons, before/after | `model.ts` B |
| **Prompt field** | Text typed exactly on the spoken words, caret-following camera, next-token flicker, ⏎ rush | Quoting a prompt/command/message | `prompt.ts` |
| **Full-bleed colour slams** | One full-frame word per spoken word on a signal field, deadpan readout | Hype moment, "this is where it gets…" | `crazy.ts` A |
| **Construction sheet** | Code listing typed line by line + artboard building each named element; τ rewind/replay | Lists of components, "how it works" | `code.ts` |
| **Film strip → player** | Scanline rasterises a frame; strip snaps a frame per word, accelerates, collapses into a player | Processes over time, "turned into" | `frames.ts` |
| **Paper form / process chart** | Bone-paper FORM with typed boxes, pen arrows on each "to", marker strike, stamp | Step-by-step processes, old vs new pipeline | `pipeline.ts` |
| **Dictionary entry** | pro·ce·dur·al set in Cormorant, deadpan definition | Defining a term | `edits.ts` 1 |
| **Chat + live preview** | Each command typed as said, a two-line diff answer, the preview changes on the spot | Demonstrating commands/edits/features | `edits.ts` 2 |
| **Field of many** | Hundreds of items (keyframe diamonds) worked one by one, then dropped | "hundreds of…", tedium, scale | `edits.ts` 3 |
| **Questionnaire** | FORM with question typed, YES/NO/NOT REALLY ticked by the pen, exceptions list | Q&A, verdicts, honest caveats | `verdict.ts` A |
| **Arc leap + slam + implode** | Spark leaps idea → result over an untouched obstacle; final slam implodes into the bookend | Payoff and ending | `verdict.ts` B |

## Transitions between plates
The template hands over with a motivated move rather than a plain cut: a camera dive into a node
that becomes the next plate (`hook` → `model`, `crazy` → `code`), the prompt field rushing at the
camera (`prompt` → `crazy`), a full-frame keycap becoming the next background. Plan each plate's
last 0.3 s with the next plate's first frame in mind.

## Pacing rules of thumb
- One visual change per stressed word, not per word. Unstressed words just light up in karaoke.
- Big moves (slams, camera whips) on nouns and verbs that carry the idea; small ticks for lists.
- Leave ~0.3–0.6 s of settled frame after a payoff before the next cut.
- On a dense line, let one element build and the camera do the rest.
