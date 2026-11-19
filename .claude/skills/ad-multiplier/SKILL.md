---
name: ad-multiplier
version: 1.5
description: >-
  Produce one or many ad versions from one supplied 4-30 second video. Edit
  mode uses the Ad Multiplier model to replace, add, remove, or modify people,
  animals, products, objects, clothing, backgrounds, attributes, or explicitly
  targeted on-screen text while preserving source motion, framing, cuts,
  timing, aspect ratio, default audio, captions, and other untargeted text,
  including AI-generated adult replacement people when references are missing.
  Recreate mode uses Ad Multiplier Recreate to re-shoot the same ad structure as
  new footage for another market, audience, spoken language, cast, product, or
  setting. Trigger on "ad multiplier", "multiply my video", "multiply my ad",
  "make me 10 variations of my ad", "regenerate my ad with these
  people/product", "recreate my ad for Germany", "remake this ad for Gen Z",
  and equivalent requests. NOT for: dubbing or translating the existing
  footage, ad referencing (an original ad that only borrows a reference ad's
  ideas), video reference, simple video edits, Marketing Studio presets,
  sources outside 4-30 seconds, or Cartesian combinations of independent asset
  lists.
allowed-tools:
  - get_workflow_bundle_file
  - media_upload_widget
  - media_upload
  - media_import_url
  - media_confirm
  - show_medias
  - video_analysis_create
  - video_analysis_status
  - models_explore
  - generate_image
  - generate_video
  - sandbox_exec
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Ad Multiplier

Turn one source ad clip into `N` ordered, independent videos. Upload the source
once. `N` always counts final videos, never people, assets, operations, or
takes.

## Choose the mode first

- **Edit** (default): targeted changes to the source footage — replace, add,
  remove, or modify people, products, objects, clothing, backgrounds,
  attributes, or targeted text — while its motion, timing, and audio survive.
  One output may contain several simultaneous edits. Follow Stages 1-7 below.
- **Recreate**: the same ad re-shot as new footage for another market,
  audience, spoken language, cast, product, or setting. Load
  [recreate.md](references/recreate.md) once with `get_workflow_bundle_file`
  and follow it instead of Stages 1-7 and their output contract. The runtime
  contract below still applies: submit each output with `generate_video`, one
  at a time, and let its original widget show the final result.
- **Hook or CTA only**: a new opening hook, closing call to action, or both,
  with the rest of the ad kept. Follow the "Hook or CTA only" section of
  [recreate.md](references/recreate.md), under the same runtime contract.
- If the request fits both, ask one question: keep the original footage and
  change named targets, or re-shoot the ad as new footage?

## Runtime contract

- Use only tools exposed by the current Full MCP host. Use native client
  elicitation when available; otherwise ask one concise normal-chat question.
  Never invent a question tool.
- For local attachments in an Apps-capable client, call `media_upload_widget`.
  When the client can provide bytes, use `media_upload`, PUT to its `upload_url`,
  then call `media_confirm`. Import an authorized HTTPS media URL with
  `media_import_url`. Retain every confirmed `media_id` and hosted HTTPS URL.
- Run downloads, `ffprobe`, `ffmpeg`, remuxing, and QC only through
  `sandbox_exec`, never through a client-local shell.
- The sandbox is ephemeral. A finalization call must download its inputs,
  create and verify its outputs, and PUT them to previously reserved
  `media_upload` slots in the same `sandbox_exec` command. Confirm only after
  each PUT returns HTTP 200.
- Submit exactly one position at a time with `generate_image` or
  `generate_video`, always with `count:1`, and retain its returned `job_id` under
  the stable output position. Do not use batch submission, batch waiting, or a
  multi-result gallery in this workflow.
- `generate_image` and `generate_video` each render their own self-updating
  generation widget. Do not invoke another display or polling tool for a job
  submitted by this workflow. If its original widget is still pending, stop and
  tell the user it will update automatically; never resubmit the pending job.
- In edit mode, never treat an Ad Multiplier generation widget as the final
  deliverable; final videos are confirmed uploads after audio restoration and
  QC.
- `unlim_choice` means no job was submitted. Ask its exact question and resubmit
  the unchanged request with the user's `use_unlim` choice. Never choose for
  the user or silently change a locked model/configuration.

## Edit mode: non-negotiable output contract

- Accept exactly one measured source video of **4.0-30.0 seconds inclusive**.
  Do not trim, split, loop, freeze, or clamp an out-of-range source.
- Supported operations are replace, add, remove, attribute change, clothing
  change, background/location change, an explicitly requested on-screen-text or
  graphic edit, and user-timed edits. Preserve every caption, subtitle, UI
  element, motion-design graphic, label, branding mark, and other on-screen text
  unless the user explicitly targets it or it is physically attached to a
  replaced target. Never automatically remove, add, or regenerate captions.
- Keep source motion, performance, choreography, camera, cuts, lighting, pacing,
  display aspect ratio, exact final duration, and original default audio.
- A person replacement covers every appearance of that mapped source person.
  The original must not survive through cuts, entrances, exits, occlusions,
  motion blur, transitions, reflections, or shadows. Preserve every unmapped
  person.
- For a person identity replacement, its mapped `@ImageN` is authoritative for
  the complete visible look: face, head, hair, skin tone, body/build/stature,
  grooming, clothing, footwear, and wearable accessories. The replaced source
  person's clothes and wearables do not survive. Override only the clothing
  portion when a separately attached garment or full-outfit image maps to that
  person or the user explicitly requests different clothing, including retaining
  named source clothing. A Soul-generated or studio-background person image
  follows this same whole-look rule and is never identity-only by default.
- Preserve output order from planning through prompts, generation, QC, and
  delivery. Zip ordered lists. Never create a Cartesian product or invent a
  persistent variant registry.
- If each of `N` outputs replaces two people and neither has a reference, create
  `2N` distinct replacement people and pair two with each output.
- Ad Multiplier renders silently with `mode:"video_edit"` and
  `generate_audio:false`; verified finals receive only the source's default
  audio. A source with no audio produces silent finals.
- Retry each failed generation position at most once. Continue with independent
  successes and report every failed output.

## Stage 1 — resolve intake once

As soon as a source is supplied, collect all still-missing fields in one turn:

1. the requested edit and ordered output list or explicit `N`;
2. whether replacement reference images exist: all, some, or none;
3. final resolution: `720p` (recommended/faster) or `1080p`.

Do not ask again for information already explicit. If references are promised,
wait for them before paid generation. If the target, time range, reference
mapping, or list-to-output assignment is ambiguous, ask one bundled mapping
question rather than guessing.

## Stage 2 — register, probe, and analyze the source once

1. Resolve one confirmed source `media_id` plus its hosted HTTPS URL. Reuse an
   existing confirmed upload from `show_medias` when the user identifies it.
2. In one `sandbox_exec` call, download that trusted hosted URL and run:

   ```bash
   ffprobe -v error -show_streams -show_format -of json -- source.mp4
   ```

   Apply the exact normalization and range checks in
   [media-pipeline.md](references/media-pipeline.md). Retain only the returned
   measurements; the downloaded sandbox file is not durable.
3. Call `video_analysis_create` once with `video_input_id:<source media_id>`,
   then poll its id with `video_analysis_status` every 30-60 seconds until
   `completed` or `failed`. Use the returned scenes as the timed source caption.
   Do not start a second analysis while the first is pending.
4. Retry analysis once only if it fails, returns no usable scenes/timing, omits
   a requested target, or lacks observable evidence for either required
   casting-presentation or hairstyle axis. Stop before generation if the second
   result is unusable. Missing stature/build never triggers this retry.

For every source person that will be replaced, derive a required two-axis
`source_visual_casting_profile` only from observable evidence in the analysis:
apparent racial/ethnic casting presentation plus hairstyle length, texture, and
shape. These are fictional visual casting descriptors, not claims about real
identity. The video-analysis contract does not guarantee a stature/build field.
Stature and build are optional, non-gating appearance context: carry either only
when the user supplies it or the analysis states it unambiguously; otherwise
omit it without asking. Never ask the user, block generation, reject an image,
or regenerate solely because stature or build is unavailable or unchanged. If
either side of a required two-axis contrast is unclear after the one retry, ask
for a clearer source or for both the visible source trait and desired replacement
trait; do not guess.

## Stage 3 — plan ordered outputs

- Preserve explicit `N`; otherwise infer it from the ordered output list, or use
  one for a single edit request.
- Map edits on existing content to analysis target descriptions plus a unique
  plain-language anchor and natural visible ranges. An `add` instead uses a
  caption-grounded placement and timing.
- A person identity replacement is global across that person's appearances. If
  the user asks for a partial person replacement, ask them to choose either a
  full identity replacement or a non-identity attribute edit.
- Resolve each person reference's appearance authority before prompt writing.
  Default to `complete_look`; record a `clothing_override` only for a separately
  mapped garment/full-outfit image or an explicit user clothing instruction.
  Source wardrobe inferred from the video is never an override. A clothing
  override inside an identity replacement does not cancel global exclusion of
  the original person.
- `remove` needs no asset and describes the revealed background. `add` states
  placement, scale, motion, and interaction. Attribute edits change only the
  named property. Preserve captions, subtitles, UI, motion design, labels,
  branding, and every other source text element exactly as shown unless the
  user explicitly requests a specific text or graphic edit or that text is
  physically attached to a replaced target. A targeted text edit preserves
  source typography, placement, animation, and timing unless the user changes
  them. Do not introduce blanket text cleanup or caption generation.
- Resolve every user-dependent choice during planning. A final Ad Multiplier
  prompt states only the resolved edit and contains no branches, alternatives,
  or meta-conditions. A targeted text edit becomes one explicit operation while
  all untargeted text receives an unconditional preservation instruction.
- Shared assets/instructions may repeat across outputs. Ordered replacement
  lists pair by output position only.

## Stage 4 — acquire replacement references

### User-supplied images

Resolve each image to a confirmed media id and hosted HTTPS URL. Keep one fixed
order. The URL is for visual inspection; the media id is the downstream
generation input. Never substitute one for the other.

### Missing adult human references — Soul 2.0

Use Soul 2.0 (`soul_2`) only for a requested human replacement that lacks a
user image. It is not a fallback for animals, creatures, robots, products,
objects, backgrounds, removals, attributes, text edits, children, or teens.

1. Load the live contract once with
   `models_explore({action:"get",model_id:"soul_2"})`.
2. Submit one distinct `generate_image` call per missing adult slot, one
   position at a time. Use no `medias` and no `soul_id`; use `count:1`,
   `aspect_ratio:"3:4"`, and `quality:"2k"`. Soul 2.0 is prompt-driven: put the
   adult age band, presentation, period-appropriate wardrobe, and visual genre
   directly in the positive prompt. Use only the live Soul 2.0 fields shown
   below; do not add structured demographic or cinematic controls. If either
   required axis cannot map after the one permitted analysis retry, ask; never
   ask for stature/build. For a source under 20, require a user reference or
   explicit consent to recast the role as an adult.
3. Before each request, build a positive two-axis contrast plan against that
   slot's source person. Every generated replacement must have both: a clearly
   different apparent racial/ethnic casting presentation and a different
   hairstyle, including length, texture, and shape. Stature/build never gates
   this plan. Do not force a different body type, body proportions, face shape,
   or facial geometry. Those traits come naturally from the generated image.
   Generated people in the same request set must also remain visibly distinct
   from one another.

   Write each Soul prompt as one cohesive **140-190 word natural-language
   paragraph**, not a tag list, fragment stack, or compressed semicolon
   checklist. Resolve every field before writing; never submit bracketed
   placeholders or slash-separated alternatives. The replacement must be
   strikingly beautiful, handsome, or otherwise conventionally attractive. Use
   the matching concrete phrase for the requested presentation: `strikingly
   beautiful`, `strikingly handsome`, or `conventionally attractive`. Include these four
   anchors or close positive paraphrases in fluent prose: `with high model
   facial features`, `symmetrical features`, `well-proportioned figure`, and
   `natural skin texture`. Never default an unspecified presentation to the
   worked example's woman; resolve it from the request/source mapping or ask.
   Beauty and realism are quality floors, not additional contrast axes.

   Build the paragraph in this order:

   1. **Subject and pose:** open with a straight-on, eye-level, full-body portrait
      of exactly one adult age 20+. State the positive replacement casting traits,
      skin tone, hairstyle length/texture/shape, facial quality, posture,
      expression, and direct camera gaze. Add stature/build only when it is
      user-specified or unambiguously available; never invent it as a contrast.
      Describe the selected casting presentation through concrete visible traits;
      never write only "different" or "contrasting," and never mention the source
      person's traits in the Soul prompt.
   2. **Wardrobe:** name a complete stylish, period-appropriate outfit from top
      through footwear, using opaque, well-structured fabrics plus at most two
      restrained accessories. Keep the entire outfit and both feet visible.
   3. **Studio and composition:** place the subject alone against a seamless
      matte-white studio backdrop whose white floor blends cleanly into the wall.
      Center the figure in balanced vertical framing with generous negative space
      and no props, furniture, text, logos, or visual clutter.
   4. **Lighting and palette:** use soft, evenly diffused high-key natural studio
      lighting, gentle grounded shadows, controlled highlights, and no harsh
      contrast or overexposure. State a restrained outfit-led color palette.
   5. **Capture and finish:** specify a professional high-resolution digital
      camera, deep depth of field, ample dynamic range, minimal noise, and
      razor-sharp head-to-toe focus. Close with authentic skin detail, realistic
      human anatomy, natural hands and limbs, and no plastic retouching,
      distortion, or exaggerated traits, plus a crisp modern editorial mood.

   For multiple missing people, vary the concrete pose, outfit silhouette,
   accessories, palette accents, and both casting axes while preserving this
   studio/camera quality standard. The worked request below demonstrates prose
   form only. Rebuild every subject detail from the slot's approved contrast plan;
   do not copy its woman, age, casting presentation, hair, skin tone, or wardrobe.
   Submit the completed paragraph as-is; Soul 2.0 has no model-side prompt
   enhancer in this connector.

   ```json
   {"params":{"model":"soul_2","prompt":"A straight-on, eye-level full-body portrait features a strikingly beautiful 24-year-old Afro-Caribbean woman with supermodel facial features, symmetrical features, a well-proportioned figure, warm deep-brown skin with natural texture, and long dark softly waved hair. She stands poised with shoulders back, one foot angled outward, arms relaxed, and a direct camera gaze. She wears a structured matte-black blazer, opaque high-neck top, tailored wide-leg trousers, pointed-toe heels, thin gold chain, and small stud earrings. Her complete outfit and both feet are visible. A seamless matte-white studio backdrop and matching floor contain no props, furniture, text, logos, or clutter, leaving generous negative space around her centered figure. Soft, evenly diffused high-key natural studio lighting creates gentle grounded shadows, authentic skin detail, and controlled highlights without harsh contrast or overexposure. A crisp black, white, and subtle gold palette supports the modern fashion-editorial mood. Captured on a professional high-resolution digital camera with balanced vertical framing, deep depth of field, ample dynamic range, minimal noise, and razor-sharp focus from face to footwear, the image preserves realistic anatomy, natural hands and limbs, and a photogenic unretouched editorial finish without distortion or exaggerated traits.","count":1,"aspect_ratio":"3:4","quality":"2k"}}
   ```

   This text-only Soul 2.0 request receives neither `@Video1` nor media inputs.
   Words such as "different" or "contrasting" without explicit positive
   replacement traits do not satisfy the gate.
4. Retain the returned job id and let its original `generate_image` widget poll
   and display that position automatically. Do not invoke another display or
   polling tool. Retry only a terminal-failed position once. Inspect each
   completed result against its mapped source profile, contrast plan, and
   quality gate.
   Regenerate a named position once if either required axis is unchanged, vague,
   or missing, or if the person is not attractive, photogenic, natural-looking,
   and anatomically realistic. Never offer a failed-contrast or failed-quality
   candidate for approval.
5. Ask for approval of the candidate shown in its original generation widget.
   Continue only after approval; regenerate named people or stop as requested.
6. After approval, retain its `result_url` for visual inspection, completed
   generated-person image `job_id` for direct Ad Multiplier image media, and
   approved positive two-axis profile. Use the approved image directly without
   re-uploading it. It is a normal positional image reference in both the prompt
   contract and Ad Multiplier; the Full MCP generation resolver turns the
   completed job id into `image_job` media.

## Stage 5 — write one final edit prompt per output

Load [prompt-writer.md](references/prompt-writer.md) once with
`get_workflow_bundle_file`, then apply it directly. There is no enhancer service
in Full MCP. Build one in-memory asset manifest per output:

1. user-uploaded references first as `@Image1..@ImageK`, matching the exact
   downstream Ad Multiplier media order;
2. approved generated-person references afterward, beginning at `@Image(K+1)`,
   with completed job ids in the matching later Ad Multiplier image-media positions.

When `K=0`, the first approved generated-person reference is `@Image1`. Every
attached image is a downstream Ad Multiplier input and keeps the same canonical
`@ImageN` position in the visual inspection order, manifest, final prompt, and
Ad Multiplier media list.

```json
[
  {"tag":"@Image1","asset_key":"uploaded_product","role":"product","target_id":"product_1","target":"the can held by the woman","state":"whole clip","complementary_of":null},
  {"tag":"@Image2","asset_key":"output_1_replacement_person_1","role":"person","target_id":"person_1","target":"the woman in the gray jacket","state":"whole clip","complementary_of":null,"appearance_authority":"complete_look","clothing_override":null,"replacement_casting_profile":{"apparent_racial_ethnic_presentation":"<positive fictional casting description>","hairstyle":"<positive length, texture, cut, and shape description>"}}
]
```

Include `replacement_casting_profile` only for an approved generated person and
copy both required values exactly from the approved contrast plan. Every person
entry uses `appearance_authority:"complete_look"`. Replace `clothing_override`
with a resolved separate clothing tag/instruction only under the Stage 3
precedence; otherwise keep it `null`.

Do not write manifests or prompts to disk. If a reference cannot be visually
inspected, use an authoritative user description or ask rather than inventing
identity details. Preserve each finished prompt byte-for-byte after validation:

- non-empty and at most 3900 characters;
- every required `@Image1..@ImageN` occurs at least once;
- no undeclared image tag, raw media id, job id, or URL survives;
- every requested operation is covered;
- the exact unconditional source-text preservation block beginning `Preserve every caption,
  subtitle, and other untargeted on-screen text element from @Video1 exactly as
  it appears` occurs exactly once;
- no automatic text-removal or caption-generation instruction appears;
- every generated person's declaration and render instructions preserve all
  required two-axis values plus the complete visible look from the approved image,
  including clothing, footwear, and wearable accessories;
- no mapped source clothes or wearables survive or receive unchanged-content
  protection without a resolved `clothing_override`;
- no unresolved user/request condition appears, every replacement alias comes
  from its declared `@ImageN` rather than `@Video1`, and all tags use exact
  canonical case;
- every replaced source person's complete exclusion is explicit.

Rewrite one invalid prompt once against the same plan, then fail only that
output before generation.

## Stage 6 — submit silent Ad Multiplier edits

For each output, send the source video first, then every image reference in the
same order used by the manifest and prompt. A user image uses its confirmed
media id; a generated-person image uses its completed generation job id. The
prompt refers to both only by their canonical `@ImageN` tags.

```json
{"params":{"model":"ad_multiplier","prompt":"<validated prompt verbatim>","count":1,"duration":8,"duration_policy":"strict","aspect_ratio":"auto","resolution":"720p","mode":"video_edit","generate_audio":false,"medias":[{"value":"<source media id>","role":"video"},{"value":"<@Image1 confirmed user media id>","role":"image"},{"value":"<@Image2 approved generated-person job id>","role":"image"}]}}
```

Use `model:"ad_multiplier"` for every edit request; never call
`model:"seedance_2_5"` directly in this workflow. The numeric duration is
illustrative: always use `ceil(SOURCE_DURATION)`. Use
the chosen resolution. Submit outputs one at a time in order with
`generate_video`. Retain each accepted job id under its output index. Retry only
a rejected or terminal-failed position once with the same approved identity and
scope; never retry a pending position.

After each submission, rely on its original `generate_video` widget to poll and
render that Ad Multiplier position. Do not invoke another display or polling
tool. State that the widget preview is silent and still requires final audio
restoration and QC, then continue to the next output only after the current
position is terminal.

Do not extract audio in a separate early sandbox call: it would not survive the
remote render. Finalization re-downloads the immutable source and extracts its
default audio in the same producing sandbox call.

## Stage 7 — finalize, upload, and verify

For each completed Ad Multiplier job, retain its trusted HTTPS `result_url` for
processing; never deliver the raw silent widget preview as the final result.
Process at most 4 completed outputs per sandbox call.

1. Load [media-pipeline.md](references/media-pipeline.md).
2. Reserve one final MP4 slot per output with `media_upload` before the sandbox
   call.
3. In one self-contained `sandbox_exec` command, download the trusted source
   and raw results, extract the source's default audio once, trim/remux each
   result, run all duration/aspect/resolution/audio gates, and PUT each passing
   final to its own reserved `upload_url`. Do not reuse or reconstruct an upload
   URL.
4. Call `media_confirm` only for outputs whose PUT returned HTTP 200.

Deliver only confirmed final upload URLs, in original output order, labeled
`Output 1`, `Output 2`, and so on. State `completed/total`, concise failure and
pending counts, selected resolution, exact source duration, and whether source
audio was restored or the source was silent. Never expose raw Ad Multiplier URLs,
silent generation artifacts, generated-person references, prompts, manifests,
local paths, or job/element ids as deliverables.

## Failure boundaries

| Failure | Required response |
| --- | --- |
| Source outside 4-30s | Stop; report measured duration and accepted range |
| Source upload/probe fails | Retry once when safe; otherwise stop before spend |
| Analysis invalid twice | Stop before generation |
| Ambiguous mapping | Ask one bundled mapping question |
| Generated-person image position fails twice | Fail each dependent whole output or stop |
| User rejects generated people | Regenerate named people or stop |
| Approved generated-person direct reference unavailable | Fail every dependent output before Ad Multiplier |
| Prompt validation fails twice | Fail only that output before Ad Multiplier |
| Ad Multiplier position fails | Retry only that position once |
| Source is silent | Produce a silent verified final |
| Audible source extraction fails | Do not deliver a silent substitute |
| Download/remux/QC/upload fails | Isolate that output; keep verified successes |
| Some outputs remain pending | Report pending; never duplicate them |
