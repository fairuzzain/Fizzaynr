# Recreate mode — Ad Multiplier Recreate

Recreate re-shoots one supplied 4-30 second source ad as new footage for
another market, audience, spoken language, cast, product, or setting, while the
backend keeps the source's structure: its beats, order, timing, pacing, aspect
ratio, and capture style. Each output is one `ad_multiplier_v2` generation.
The same model can also regenerate only the source's hook, its CTA, or both,
and stitch them back in; see [Hook or CTA only](#hook-or-cta-only).

The backend owns the creative work and every decision. For every job it
analyzes the source, reads the prompt and the images, decides the language,
product, cast, image roles, audio, and setting from them, writes the generation
prompt, renders `ceil(source duration)` seconds at the source aspect ratio (an
unlisted ratio such as 4:5 renders at the nearest supported one), and restores
the source audio when it keeps it. Therefore, in this mode:

- do not run `video_analysis_create`, write a video prompt, or call
  `seedance_2_5` or `ad_multiplier` directly;
- do not trim, remux, caption, or QC the result in the sandbox: a completed job
  is the final deliverable;
- send only `prompt`, `medias`, `resolution`, and `count`, plus `mode` and
  `section` for a hook or CTA only; never send `duration`, `aspect_ratio`,
  `generate_audio`, `language`, `audio`, `use_unlim`, or `use_free_gens`. Any other field is ignored, so an instruction
  that is not in the prompt is lost. This model is paid with credits only and
  rejects unlimited and free generations.

## Choose recreate only for a new performance

Use recreate when the user wants the same ad made again with new footage: a
local cast and setting, a new spoken language, a different audience, their own
product in a source ad's structure, or several such market versions. Stay in
edit mode when the source footage, motion, and audio must survive and only
named targets change. Use [Hook or CTA only](#hook-or-cta-only) when only the
opening or the closing call to action should be new and the rest must stay.
Route elsewhere for dubbing or translating the existing footage, reframing, or
an original ad that only borrows a reference ad's ideas with a new script.

## Intake — ask only for what is missing

The backend never asks, so the prompt must carry the request. Ask once, in one
question, only when the user has not given:

1. the source video (4.0-30.0 seconds);
2. what changes: the target market or audience, the spoken language, a new
   product, or new people.

Without other instructions, make 1 output at `720p`. Ask nothing the user already
stated, and never ask about audio, setting, image roles, or the product mode:
the backend decides them. Never invent product facts, prices, offers, or claims.
Ordered lists pair by output position; never build a Cartesian product.

Do not generate people for this mode. When the user wants a different person
and gives no photo, describe that person in the prompt: the backend generates
one adult likeness itself, at no extra charge, and casts it; describe any
further person in words. With a photo, pass it as an `image` media
and say in the prompt whom it replaces. A new performer or a new spoken
language gets a new voice; the source voice and music stay only when nobody
who speaks changes, unless the prompt asks otherwise.

## Map each output to one request

| Field        | Value                                                                                                                                                                                                                                    |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`      | `"ad_multiplier_v2"`, with `count:1` per output                                                                                                                                                                                          |
| `prompt`     | That output's whole request in the user's words, at most 4000 characters: the market or audience, the spoken language, a replacement product's name and the facts the user gave, who each image is, lines to say exactly in quotes, and any explicit audio or setting wish. Add no invented facts. |
| `medias`     | The source as `role:"video"`, then up to 20 images as `role:"image"`. Images need no role: the backend classifies them as product, person, wardrobe, location, prop, logo, or style, and the prompt's words about an image win. |
| `resolution` | `720p` unless the user asked for `1080p` or `480p`.                                                                                                                                                                                      |

```json
{"params":{"model":"ad_multiplier_v2","prompt":"Recreate this ad for the German market in German, with the presenter in the image replacing the main presenter.","count":1,"resolution":"720p","medias":[{"value":"<source media id>","role":"video"},{"value":"<presenter image media id>","role":"image"}]}}
```

Every output is an independent backend analysis and render, so two outputs
with the same inputs still differ. Each output costs `ceil(source seconds)` at
the Seedance 2.5 per-second rate for the chosen resolution.

## Hook or CTA only

When the user wants a new opening hook, a new closing call to action, or both,
and the rest of their ad kept as it is, send the same request with
`mode:"sections"` and `section:"hook"`, `section:"cta"`, or `section:"both"`.
One output with `section:"both"` replaces the hook and the CTA together.

The backend finds each section in the source (the first hook, the last CTA),
cuts at the end of the shot that finishes it, never inside a spoken word, renders each new section in the source's
setting at a length it picks (a hook 4-15 seconds, a CTA 4-5), and stitches them
in with hard cuts. The rest of the source is untouched, so the result is
`source length - removed sections + new sections` seconds long. When the source
has no clear hook or CTA, the new one is added before (hook) or after (CTA) the
whole ad and nothing is removed. The prompt says what the new hook or CTA should
do or say; leave out changes to the rest of the ad, which a sections run cannot
make.

A sections output reserves its longest length (hook 15 seconds, CTA 5, both 20)
at the Seedance 2.5 per-second rate and is charged only for the seconds it
renders; the rest comes back. With `section:"both"`, if one part fails the
output still completes with the source kept in place of that part, only the
rendered part is charged, and the job's `failed_sections` names the part that
failed; if both fail, the job fails and nothing is charged.

```json
{"params":{"model":"ad_multiplier_v2","mode":"sections","section":"hook","prompt":"New hook: open on a close-up of the product with the question \"Still tired at 3 pm?\"","count":1,"resolution":"720p","medias":[{"value":"<source media id>","role":"video"}]}}
```

## Failures

| Failure                                                              | Required response                                                                                      |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 422: source duration                                                 | Nothing was charged. Report the measured problem and stop, or fix the input. Never resubmit unchanged. |
| 403: `minimum_pro_plan_required`                                     | This model needs a Pro plan or higher. Tell the user and stop; nothing was charged                     |
| 403: not enough credits                                              | Report the balance needed (a sections run needs its longest length up front) and stop                  |
| 422: parameter validation                                            | Correct the mapping once and resubmit that output only                                                 |
| Job failed with `prompt_enhance_failure: INPUT_ERROR: <reason>`      | Report the reason and fact, ask the user for it, put the answer in the prompt, and resubmit once       |
| `nsfw` or `ip_detected`                                              | Report it and do not resubmit                                                                          |
| Other terminal failure                                               | Retry that output once with the same request                                                           |
| Some outputs pending                                                 | Report them as pending and never duplicate them                                                        |

## Delivery

Deliver completed result URLs in output order, labeled `Output 1`,
`Output 2`, and so on. For each, state the change it was asked for and the
chosen resolution; do not guess decisions the backend made. Report `completed/total`, failures, and
pending outputs. A job stays `queued` for the first few minutes while the
backend analyzes and plans it; that is not a stall. Do not claim that captions were added; recreate renders
contain no captions. For a hook or CTA output, say which part was replaced and
that the rest of the source is unchanged; when `failed_sections` names a part,
say that part could not be made and the source keeps its own there.
