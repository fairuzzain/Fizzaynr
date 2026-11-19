# Logo system

Load this module only when the user asks to create, extend, document, or apply a logo. A request for other branded graphics does not authorize a redesign.

## Route

### Existing official logo

Use the supplied file as authoritative.

1. Analyze source geometry, variants, colors, clear space, and minimum-size guidance from source files/brandbook.
2. Upload once and record the ID in the Brand Lock.
3. Reuse or deterministically place the exact asset.
4. Generate only requested variants/applications.

Never ask an image model to redraw a logo merely to change its background, size, placement, or colorway. Use SVG/PPTX/image compositing when the source supports it.

### Partial logo system

Examples: only a primary logo exists; no monochrome/reverse version, symbol, clear-space rule, or lockup.

- Preserve the primary mark.
- Propose only missing variants.
- Derive variants from source geometry rather than inventing a second style.
- Ask before separating a symbol from a wordmark if the source does not demonstrate that they may be used independently.

### New logo

Run only when explicitly requested.

1. In an interactive new-identity flow, complete the palette review in `concept-boards.md` first. Require a user-selected and persisted palette before generating logo candidates. Color/style preferences from intake are not palette selection. Only explicit auto/no-question mode may select the palette internally; it must call `approve_palette` and receive a successful state response before generating logo candidates.
2. Load `brandkit-design-brain.md` and run `PROPOSE_LOGO_MECHANISMS` with the brief, references, visual axes, and selected palette.
3. Require exactly three distinct symbol-only candidate specifications.
4. Apply `logo-prompt-enhancer.md` exactly once per candidate, building one complete structured candidate input per application.
5. Call `models_explore(action: "get", model_id: "recraft_v4_1")`, then submit `generate_image_batch` with three `{index, params}` requests (one enhanced prompt each, `count: 1`) with `model_type: "vector"`, the selected exact hex colors in `colors`, and the selected background in `background_color`.
6. Wait with `jobs_wait` on the indexed jobs, then show all three together with `show_generation_by_ids`. Use the three Recraft SVG result URLs directly. Do not pass them through the HTML preview script or any SVG normalizer/editor.
7. Show all three SVGs per the logo review in `inline-widgets.md` in every mode, including explicit auto/no-question mode; never return them only as bare URLs. Then send a normal message inviting the user to review and comment when interaction is allowed.
8. When the user selects one SVG, immediately save that exact asset and fingerprint with the Brandkit state script's `approve_logo` action. Continue to typography only when the original request requires text/type; a logo-only request does not.

## Enhancer contract

For each of the three Design Brain mechanisms, assemble the complete structured candidate input defined in `logo-prompt-enhancer.md`:

```text
{
  brand_context: {
    name,
    offering,
    industry,
    positioning,
    audience,
    values
  },
  visual_axes: {
    restrained_expressive,
    geometric_organic,
    familiar_experimental
  },
  candidate: {
    mark_type,
    central_idea,
    visual_mechanism,
    distinctive_element,
    shape_logic,
    treatment,
    style_register,
    user_style_directive,
    composition
  },
  palette: {
    count,
    user_requested_more_than_three,
    roles
  },
  reference_signals,
  forbidden_elements
}
```

Apply that reference's full contract to produce one enhanced prompt per candidate. Use only that enhanced prompt as the candidate's Recraft prompt. Never merge the three enhanced prompts into one request.

Exact hex colors never enter the enhanced prompt prose. Pass them directly in each Recraft request's `colors` and `background_color` params.

Set `user_requested_more_than_three: true` only when the user explicitly asks for a logo with more than three colors. Otherwise pass exactly the one, two, or three logo colors the concept requires, even if the broader brand palette contains more. Never add colors merely to reach three.

In explicit auto/no-question mode, score the three candidates for brief fit, distinctiveness, and legibility; select the strongest without opening a question.

## Exactly three comparable SVG candidates

All three must:

- Be true SVG outputs returned directly by Recraft V4.1 vector mode
- Use the same aspect ratio, palette parameters, background, and generation quality
- Belong to the selected draft palette and user-defined direction
- Differ in mark construction, not presentation quality
- Stay simple enough to reproduce faithfully with vector geometry
- Express one visual concept only; never fuse two metaphors unless the user's own request explicitly described that exact fusion
- Include one concrete distinctive silhouette, negative-space device, motif treatment, or unexpected locked color-role pairing
- Preserve any explicit user-requested style in the candidate and enhanced prompt
- Use one, two, or three logo colors as the concept requires; three is a maximum, not a default, unless the user explicitly requested more
- Avoid generic swooshes, arbitrary initials, stock startup symbols, tiny details, gradients/effects unless concept-critical, and mockup scenes

Typography is selected afterward. Every enhancer prompt must include “no text” in its constraint tail. Monograms may contain only their explicitly requested initials.

If prompt enhancement or the Recraft call fails, retry once with the same candidate specification. If it fails again, stop and report the error. Never substitute GPT Image. Select a winner on the user's behalf only in explicit auto/no-question mode.

During typography selection, the mark and wordmark must feel like one lockup:

- Match stroke/weight and corner character
- Balance mark height against cap/x-height
- Use deliberate gap and optical alignment
- Avoid a detailed/heavy mark beside a weak or unrelated wordmark

Never reproduce or cite a reference mark as the target.

## Color revision and optional variant export

Logo approval requires only the selected color Recraft SVG. For downstream image-generation references, export and confirm its PNG; the SVG/file ID and SVG-producing Recraft job ID must never be passed as raster inputs. Monochrome/reverse variants are optional. Do not announce, prepare, generate, or save them unless the user explicitly requested them.

When logo files or a confirmed production method require export:

1. Load [exact logo-export payloads](logo-export-payloads.md), then keep the exact Recraft SVG as the geometry source.
2. Write `brandkit/logo-export.json`, then run `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py logo-export` with `include_monochrome: false` by default. This creates only the approved color SVG and transparent 2048×2048 PNG.
3. Set `include_monochrome: true` only after an explicit request for monochrome/reverse files or when a user-confirmed output requires one-color production. Then set `primary_color` to the dominant approved source color.
4. Pass `replacements` only for a requested full-color revision.
5. Do not call Recraft or GPT Image for a color-only change.

The script fingerprints every generated variant. Any geometry mismatch is a hard stop. Optional black/white variants are deterministic derivatives of the approved color SVG, not separate concepts or image-model recolors.

For a user-requested solid palette-color/one-color variant, pass that target hex once as `single_color`. Do not reinterpret filled shapes as holes, add masks/knockouts, change fill rules, or convert strokes/paths to preserve contrast. If overlapping paints merge in one color, disclose that outcome; topology changes require separate explicit approval. The script recolors every actual SVG paint automatically and adds the SVG/transparent PNG pair. Never inspect source paints or construct per-fill `replacements` for a monochrome variant.

The script accepts Recraft hex, `rgb()`, and `rgba()` paint values and removes a detected full-canvas background. A failed color match reports the available source colors itself. If export still fails, stop and report the exact error. Never inspect or create copies with ad-hoc shell commands, `grep`, `sed`, regex scripts, or manual SVG rewriting.

For user-requested logo files or internal raster references needed by an approved downstream output, reserve the required upload URLs before export and append PUTs in the producing sandbox call via `media_upload` → `curl` PUT → `media_confirm`. SVGs confirm as `type: "file"` and keep their exact editable bytes; PNG outputs confirm as ordinary `type: "image"` uploads.

## System deliverables

Produce only requested items:

- Primary horizontal lockup
- Secondary/stacked lockup
- Symbol/monogram
- Wordmark
- Small-size/favicon treatment
- Clear-space diagram
- Minimum-size guidance
- Approved backgrounds
- Incorrect-use examples

## Clear space and minimum size

For an existing identity, copy official rules. If none exist, propose rules and mark them `inferred`:

- Define a repeatable unit `x` from a stable feature (symbol width, cap height, or dominant stroke), not an arbitrary pixel count.
- Apply `x` consistently around each lockup.
- Test at intended digital and print sizes.
- Create a simplified small-size treatment only with user approval; do not silently remove details from the primary mark.

## Editable output

- Three original Recraft SVG candidates
- Approved Recraft SVG source for the selected mark
- Full-color SVG and 2048×2048 PNG exports
- Black/white SVG and PNG variants only when explicitly requested or production-required
- PPTX brand-guide pages when requested

SVG wordmarks remain editable text and require the approved font to be installed. Do not promise native AI/EPS/Figma/Canva/PSD.

## Logo QA

- Exact spelling and glyph order
- No altered proportions or invented details
- No unintended gradients, shadows, bevels, or effects
- Correct palette and contrast
- Black and white variants have the exact approved geometry and one solid color
- Exactly three candidates generated with identical Recraft parameters
- Selected mark and later wordmark treatment look optically complete together
- Legible silhouette at small size
- Clear-space and minimum-size examples match the actual asset
- Every mockup/template uses the approved anchor, not a regenerated copy
