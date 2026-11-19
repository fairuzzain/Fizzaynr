# Inline reviews in chat

Show every Brandkit review stage directly inside chat as rendered images with download links. Editable HTML/SVG files remain downloads; the inline image is the immediate review surface.

## Publishing a review board

Reserve uploads BEFORE rendering: `media_upload` accepts `files: [{filename, content_type}]`. Allocate one `image/png` and one `text/html` upload per review. Filenames can be stable labels such as `palette-1.png` / `palette-1.html`; they do not need to match the script's local filename.

In ONE `sandbox_exec` call, restore state/inputs per `handoff.md`, write the preview JSON, then chain these steps with `&&`:

1. Run `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py preview --input brandkit/reviews.json > brandkit/preview-result.json`.
2. Read each actual HTML path from `files[i].file` in that JSON (`jq -r`). Screenshot with the preinstalled Playwright CLI, e.g.:

   ```bash
   npx playwright screenshot --viewport-size=1200,900 --full-page --wait-for-timeout=2000 \
     "file://<actual HTML path>" "brandkit/review-1.png"
   ```

   For typography, ensure the intended webfonts have loaded and inspect the screenshot for substitution; waiting alone is not proof of font fidelity. A failed/blocked font load requires correction before review, not approval of a fallback face.
3. PUT the actual HTML and PNG files to their pre-reserved URLs with `curl -f -X PUT --upload-file '<path>' '<upload_url>'`, using returned headers unchanged. Do not end the command before uploads finish.
4. Only after successful PUTs, call `media_confirm` (PNG → `type: "image"`, HTML → `type: "file"`).

Use the same reserve → produce → PUT → confirm sequence for SVG/PNG exports, state JSON, decks, and other local outputs. For logo-export, redirect its result to JSON and use `variants.color.svg` / `variants.color.png` (and only explicitly needed variants); never guess paths. A failed producing command is not a successful upload. Never pass a sandbox path to a client-attachment upload helper.

## Whole-artboard SVG previews

An SVG with physical dimensions such as `width="600mm"` renders at about 2268 CSS pixels at 96 dpi. A smaller browser viewport crops it; setting viewport dimensions does not resize the artwork. For a complete PNG, rasterize the whole SVG with an explicit output width and preserved aspect ratio (for example `rsvg-convert --width 1800 --output preview.png artwork.svg`), or scale an inline SVG inside a fitted HTML wrapper before taking a full-page screenshot. Load/install the approved fonts before rendering text.

Inspect the resulting PNG, including the right and bottom edges: all copy, arrows, bleed/trim boundaries and design elements must be visible. Pixel dimensions, SVG metadata, or a successful screenshot command alone are not visual QA.

## Rules

- Present each option as a markdown image of its board PNG followed by its “Download editable HTML” link:

  ```markdown
  ### Option 1 — <name>
  ![<name> board](<confirmed PNG url>)
  [Open full board](<confirmed HTML url>) · [Download editable HTML](<confirmed HTML url>)
  ```

- Replace every placeholder with the actual confirmed URL. For 2–3 options, repeat the complete block, stacked vertically in one message.
- The PNG is a faithful screenshot of the deterministic HTML board — never a generated image, collage, or re-drawn approximation.
- Do not create fake buttons or selection controls. In interactive mode, ask for feedback in normal chat after the review and STOP. In explicit auto/no-question mode, show the review without asking, persist the chosen slot, and continue.
- Never print filenames or bare URLs without rendering the associated visual, except final brandbook delivery, which intentionally contains only PPTX and PDF links.
- Do not make the user open each file to understand it.

Before writing a preview input, load [exact preview payloads](preview-payloads.md) and copy the complete shape for that stage.

## Recraft logo review

The HTML preview script does not handle logo creation or comparison. Wait for the three indexed jobs with `jobs_wait`, then display them together with `show_generation_by_ids`. Keep the original SVG download links beside the candidate names. This review remains mandatory in explicit auto/no-question mode; never replace it with a prose list of bare SVG URLs:

```markdown
### Candidate 1 — <short name>
![Logo candidate 1](<recraft result url>)
[Download SVG](<recraft result url>)
```

Repeat for candidates 2 and 3. If your client does not render the SVG result URL inline, rasterize a preview in the sandbox with `rsvg-convert` (2048×2048 PNG), upload it as the review image, and keep the original SVG URL as the download link.

Do not redraw, normalize, recolor, or otherwise modify the returned Recraft SVGs; a rasterized copy is a review preview only, never the asset.

## Logo color-revision/export review

When `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py logo-export` returns the color pair and any explicitly requested monochrome/reverse or single-color SVG/2048 PNG pairs, upload only the files intended for the user (SVGs keep exact bytes as `type: "file"`; PNGs confirm as `type: "image"`):

- With `delivery: "internal"`, show only the selected full-color preview and do not link the internal files.
- With `delivery: "user"`, show each PNG inline and link every returned SVG and PNG variant.
- State that geometry is unchanged and the PNG is a review/export preview.
- Never show only PNG filenames or hide the SVG variants.

## Review messages

After palette review:

> Take your time. Reply with the palette you prefer and any colors you want changed.

After logo review:

> Take your time reviewing the three marks. Reply with the direction you prefer and any shape or balance changes.

After typography review:

> Review how each type pair works with the selected mark and palette. Reply with your preferred direction or changes.

After showing the combined Essential Kit review:

> Here are your selected logo, palette, and typography together. Tell me if you want to revise an element.

In interactive mode, each review message ends the turn. In explicit auto/no-question mode, omit these questions and persist the selected slot before continuing. The combined kit is a presentation of existing approvals, not an additional approval gate.
