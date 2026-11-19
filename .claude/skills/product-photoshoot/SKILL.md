---
name: product-photoshoot
version: 1.0
description: |
  Create finished product photography and brand-marketing stills: studio packshots, lifestyle scenes, product-with-person closeups, Pinterest pins, hero banners, social carousels, static ad packs, virtual model try-ons, conceptual CGI-style product images, and restyles. Load for product photoshoots, packshots, catalog or Shopify product imagery, and product-led campaign stills. Do not use for Amazon-compliance listing sets, video ads, thumbnails, generic portraits, or UGC videos.
allowed-tools:
  - get_workflow_bundle_file
  - media_upload_widget
  - media_import_url
  - generate_image_batch
  - jobs_wait
  - show_generation_by_ids
  - models_explore
  - ask_user_question
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Product Photoshoot

Produce final, polished product stills. The product remains the visual hero in
every mode. Select one mode, load that mode's reference, build
structured prompts, generate indexed images, optionally inspect them, and show
only the final ledger. Refine observed defects or specific user-requested changes.

## Scope

| Mode | Intent | Reference |
|---|---|---|
| `product-shot` | Neutral or styled studio packshot, catalog, Shopify | `references/product-shot.md` |
| `lifestyle-scene` | Product in a real environment or in use | `references/lifestyle-scene.md` |
| `closeup-product-with-person` | Tight product + hands or partial face | `references/closeup-product-with-person.md` |
| `pinterest-pin` | Pinterest-native vertical still | `references/pinterest-pin.md` |
| `hero-banner` | Wide web, email, or campaign header | `references/hero-banner.md` |
| `social-carousel` | 3–10 connected product slides | `references/social-carousel.md` |
| `ad-creative-pack` | Coordinated static paid-social variants | `references/ad-creative-pack.md` |
| `virtual-model-tryout` | Product worn or used by a generated adult model | `references/virtual-model-tryout.md` |
| `conceptual-product` | Surreal, floating, splash, sculptural, CGI-style still | `references/conceptual-product.md` |
| `restyle` | Change an existing image's aesthetic while preserving subject | `references/restyle.md` |

Do not absorb adjacent workflows. Amazon main images, listing infographics, and
A+ content need a compliance-specific workflow. A moving product ad remains a
video-generation request. A YouTube or Instagram video cover belongs to
`thumbnail-generation`. Creator-led reviews, unboxings, tutorials, and try-ons
belong to the matching UGC workflow.

## Intake

Parse the brief before asking anything: product description or confirmed image,
mode/use case, requested variant or slide count, visual direction, aspect ratio,
exact text, brand palette, and explicit hands-off intent.

### Silent defaults

If the user says `full auto`, `auto approve`, `no questions`, `just do it`,
`go ahead`, or equivalent and supplies either a product image or a usable text
description, ask nothing. Use:

- 3 variants;
- `clean-studio` for an otherwise unspecified product shot;
- `1:1` when the use case does not imply another ratio;
- colors visible on the product or already stated in context, otherwise neutral;
- relevant craft descriptors from `references/photographer-references.md`.

State the resolved recipe in one sentence, then proceed. Do not phrase it as a
question.

### Questions

Ask only for a user-owned gap that prevents useful generation. Bundle up to
three short questions in one `ask_user_question` call when that host tool is
available; otherwise ask one concise normal-chat question. Never split one
known intake into repeated question turns.

Priority order:

1. `product_description`: no confirmed product image and no usable description;
2. `preset`: style cannot be inferred from the brief, product, or use case;
3. `variant_count`: only when quantity materially affects the deliverable;
4. `aspect_ratio`: only when the named destination is genuinely ambiguous;
5. `iteration_triage`: a vague rejection that names no defect.

Default omitted variant count to 3, omitted generic ratio to `1:1`, and omitted
palette to product-derived or neutral. Do not ask merely to expose those defaults.
Every choice question must permit a free-text alternative.

Never ask about model, resolution, prompt structure, negative prompts,
refinement, photographer names, lenses, Kelvin, f-stop, lighting terminology,
or internal brand context. Those are locked craft decisions.

## Input media

- A local product image must arrive through
  `media_upload_widget({type:"image",multiple:false,min_files:1,max_files:1})`.
  End the turn after opening the widget; resume when it returns a confirmed
  `media_id`. Do not ask the user to attach a local file directly to a remote MCP
  host.
- Import a user-authorized HTTPS image with `media_import_url` and keep the
  returned confirmed `media_id`.
- Reuse a completed generation job ID directly when the source is already in the
  current Higgsfield session.
- A text-only product is allowed when its category, form, packaging, material,
  color, label treatment, and distinctive features are sufficiently described.
- `restyle`, `virtual-model-tryout`, and `closeup-product-with-person` require a
  source product/image reference; do not invent it.

Use brand and product facts already present in conversation. Do not search for a
local `.memory` directory or invent missing claims, materials, pricing, brand
colors, label copy, or product features.

## Route and load references

Select the mode by deliverable intent. Platform/format beats environment:
Pinterest pin over lifestyle, banner over lifestyle, carousel over scene, and
closeup-with-person over generic lifestyle. `restyle` applies only when the
subject and composition should remain substantially unchanged.

Then load, through `get_workflow_bundle_file`:

1. the selected `references/<mode>.md`;
2. `references/typography.md`;
3. `references/photography-vocabulary.md`;
4. `references/photographer-references.md`;
5. `references/negative-prompts.md`;
6. `references/refinement-pass.md`.

Do not load all ten mode files.

## Prompt contract

Before the first submission, call
`models_explore({action:"get",model_id:"nano_banana_pro"})` once to verify
image-reference and 2K support. If either is unsupported, stop and report the
mismatch; do not switch model or drop the product reference.
Use `medias[].role:"image_references"` for product images and refinements.

- Model is always `nano_banana_pro`; do not substitute another model.
- Assemble prompts in English from the selected mode's named-section template.
  Preserve exact user-requested on-image strings in their original language.
- Set `resolution:"2k"`, `count:1`, and end every prompt with the literal line
  `resolution: 2k`.
- Append the relevant negative-prompt blocks.
- Follow the typography three-case rule. Do not reserve fake empty bands unless
  the user explicitly wants overlay space.
- Keep each variant materially distinct in composition, preset, hook, or scene;
  do not use `count:N` for distinct prompts.

### Sanitize style references

Photographer, publication, retailer, competitor, and third-party studio names
are internal craft anchors only. Read their descriptors, then put only concrete
lighting, palette, composition, surface, and photographic-register language in
generation prompts. Never expose those names in prompts, questions, progress,
errors, logs, or delivery notes. A user's own brand name may appear only when it
is literal text on the product being preserved.

Before every submission verify that the prompt contains no photographer name,
publication title, retailer/competitor name, or internal preset/mode codename.

## Keep one product identity across the set

When the user requests several views of one text-only product, generate the
first requested image (index 0) first and wait for completion. If an existing
viewer is available, inspect it as described under Optional visual QA. Reuse
that completed image's job ID as the image reference for every remaining first-pass variant.
Do not generate a separate reference image. Change only the scene, lighting,
and camera across the set. With a supplied product image, use that
same reference for all first passes instead. For a new unrelated product, start
a separate set rather than borrowing another product's reference.

## Generation runtime

Use the headless batch path for both internal and multi-image stages. Stable
indices identify variants/slides across first pass, refinement, and delivery.
Split submission groups at six requests and wait groups at eight jobs.

Each first-pass request is:

```json
{
  "index": 0,
  "params": {
    "model": "nano_banana_pro",
    "prompt": "<assembled mode prompt>\n\nresolution: 2k",
    "aspect_ratio": "<mode ratio>",
    "resolution": "2k",
    "count": 1,
    "medias": [{"value": "<confirmed media_id when present>", "role": "image_references"}]
  }
}
```

Omit `medias` for a valid text-only product. Submit with
`generate_image_batch`. Wait with
`jobs_wait({jobs:[...],timeout_seconds:15})`; when `all_terminal:false`, wait
the returned `poll_after_seconds` and poll only active or retryable
lookup-failed jobs. Freeze completed indices. Retry only a failed or rejected
index, never the whole set.

Use `references/refinement-pass.md` for an observed quality-gate failure or a
specific user-requested correction. Submit a focused refinement
at the same index and aspect ratio with the latest completed job ID for that index as the
single `image_references` reference. Preserve subject, product, composition, and all
passing qualities. Run at most two refinements per index. When viewing a carousel or ad
pack, audit set coherence first and refine only broken indices.

Deliver the first pass when no observed defect or specific correction requires
a refinement. If a user requests an unspecified refinement and you cannot view
the image, ask what to change instead of inventing a defect.

After every final index is terminal, call `show_generation_by_ids` exactly once
with only the final job for each stable index, in order. Do not display first
passes, rejected attempts, or superseded refinements in the final gallery.

If a submission returns `unlim_choice`, no job was created. Ask its exact
message and resubmit the unchanged request with the user's chosen `use_unlim`
value.

## Waiting and stopping

Keep an indexed ledger of submitted job IDs and their last observed status.
Use `timeout_seconds:15` during active polling and respect `poll_after_seconds`
when the host can delay. Do not use sandbox sleep or invent a delay tool. After
12 active `jobs_wait` calls for this requested set, stop polling, retain the
existing IDs, and tell the user which outputs are still pending. Resume those
same jobs only on a later user turn; never submit replacements for slow jobs.
A timeout or retryable lookup error is not permission to regenerate. Retry a
terminal technical failure or rejected submission at most once per index;
stop on safety, permission, quota, or billing errors instead of retrying them.
Count failed submissions and refinements toward a total of three generation
submissions per index. Do not reset this budget by rebuilding the prompt.

## Optional visual QA

Viewing is optional, not a prerequisite for generation or delivery. If the host
already provides an image viewer and the result is accessible, use it to inspect
the completed image and its source reference. Do not install tools or block
delivery to obtain a viewer. If fetching or viewing is unavailable, skip the
audit and explicitly state that the outputs were not visually inspected.

Only actual image content supports a visual audit; a URL, widget, status, or
prompt does not. Compare product shape, markings, colors, materials, composition,
and requested text with the brief and reference. Do not claim tiny text or
full-resolution sharpness is verified from a thumbnail. Without pixels, never
claim quality gates passed or spend credits on speculative visual refinements.
A specific user-requested correction may still be applied without viewing it.

Each refinement references the latest completed job for that SAME index,
never another variant or an older superseded attempt. Re-inspect the refinement
if viewing is available; otherwise disclose that its visual result is unverified.
When the budget is exhausted, deliver the best available completed version with
any known remaining limitation. If an index has no completed result, report it
as failed or pending; never claim the requested set is complete.

## Delivery

Return the final images and one compact sentence naming the chosen mode, preset,
ratio, and any correction applied. Disclose unverified visual QA. Hide model names, job IDs,
internal craft references, and pipeline mechanics. On vague rejection, ask one
triage question; on a specific rejection, change only the named defect.

---
(Shared section: see ../_shared/unlimited-generations-use_unlim.md)
