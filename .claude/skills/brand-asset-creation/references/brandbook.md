# Brandbook

Create the Brandbook when logo, palette, and typography are each approved. Never ask for an additional combined Essential Kit approval.

## Required inputs

Read the approved kit from sandbox state (restore `.brandkit/state.json` from this conversation's latest confirmed snapshot first, per `handoff.md`):

```bash
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py state --action get_essential_kit
```

Require these separately approved slots:

- approved logo SVG
- approved palette
- approved display/body typography
- approved brand concept/summary copy supplied by the user
- optional approved mockups

Do not invent mission, values, claims, product variants, prices, statistics, or brand-story copy.

## Canonical template

Use the supplied PPTX as the exact source template:

```text
https://docs.google.com/presentation/d/1rAfUJ-PbZ4S-h3puYSUHpE5UIcdKyRw1/export/pptx
```

Reference PDF:

```text
https://drive.google.com/uc?export=download&id=146zm9NXkGAxgKgQrGL7JywoqeRxXnWmk
```

The bundled Brandkit build script owns this fixed URL and the versioned template contract. Do not download, inspect, recreate, or edit the template manually.

## Interaction policy

Do the work quietly. At most, tell the user once that the brandbook is being prepared. Do not narrate template download, shape inspection, terminal commands, implementation choices, logo conversion, or slide-by-slide progress. Tool activity may appear in the interface automatically; do not duplicate it in assistant prose.

## Sandbox build

Write one JSON input with this complete shape. Replace values, not keys or nesting:

```json
{
  "brand_name": "Northline",
  "concept_summary": "A precise identity built around directional movement and calm technical confidence.",
  "palette_summary": "Ink and Paper establish clarity while Signal Blue marks moments of action.",
  "secondary_logo_url": "",
  "mockups": [
    {
      "url": "https://replace-with-approved-mockup.png"
    }
  ],
  "revision": 1
}
```

First reserve file upload URLs for `brandbook.pptx` and `brandbook.pdf`. Call the builder exactly once, as a `sandbox_exec` `background: true` command whose script chains the state restore, the input heredoc, the build, and PUT uploads of both returned files (template download, font resolution, and LibreOffice conversion can exceed the foreground time limit). Poll the returned status/log paths at least every 60 seconds within the sandbox's 15-minute background lease. Exit 0 must cover both build and uploads before confirmation:

```bash
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py brandbook-build \
  --input brandkit/brandbook.json > brandkit/build-result.json
```

The script reads separately approved logo, palette, and typography slots directly from `.brandkit/state.json`; do not duplicate them in the input. It downloads only the fixed canonical template, performs the deterministic build and QA, resolves the exact approved fonts, and converts the exact PPTX bytes into the matching verified PDF.

In that same background command, read `files[0]` (PPTX) and `files[1]` (PDF) from `brandkit/build-result.json` with `jq -r`, then PUT each to its reserved upload URL using `curl -f`. After the background status reports exit 0, confirm both IDs with `media_confirm` (`type: "file"`). Never wait until after rendering to reserve uploads.

## Fixed seven-slide structure

Preserve slide size, masters, layout, margins, grids, text-box positions, image zones, alignments, and hierarchy. Also preserve every element's exact x/y position, width, height, crop, rotation, stacking order, font size, paragraph spacing, line spacing, and alignment unless a conditional rule below explicitly requires duplication/removal.

1. **Cover**
   - Brand Guidelines
   - Real brand/product name

2. **Branding concept**
   - Approved concept summary
   - Approved palette rationale

3. **Primary logo**
   - Exact approved SVG

4. **Logo system**
   - Primary logo
   - Show a secondary slot only when the user supplied or explicitly requested an approved alternate/monochrome/reverse version
   - Place an approved secondary as a transparent PNG with no background rectangle
   - If no secondary is approved, remove its label and image slot; do not generate one automatically
   - Never invent a secondary logo

5. **Primary palette**
   - Replace every template swatch with approved colors
   - Replace names, RGB values, and hex values
   - Keep title/rationale boxes in their exact template positions
   - Keep each color name, RGB value, and hex value close together directly beneath its swatch; preserve the template's compact vertical spacing
   - Set each swatch label independently to a readable contrasting color; the darkest swatch must use light text
   - Do not add swatch borders. Add a minimal keyline only when the swatch color matches the slide background and would otherwise disappear.
   - Fit all approved colors into the existing palette component/grid without changing the slide's overall hierarchy

6. **Typography**
   - Approved display font
   - Approved body font
   - Use the real fonts throughout the document
   - Show both font specimens at exactly the same point size and in equal-height text boxes
   - Keep both baselines/positions aligned to the template
   - Never shrink only one specimen. If either overflows, reduce both together or shorten the approved specimen copy
   - Render and inspect the slide to prove that neither name/specimen is clipped, substituted, overlapped, or partially off-canvas

7. **Mockups**
   - Exactly two approved mockups per slide

## Conditional mockup slides

- No approved mockups → remove Slide 7.
- One mockup → use the first image zone and remove the second; do not redesign the template grid.
- Two mockups → use one mockup slide.
- More than two → duplicate the exact mockup slide for every additional pair.
- Never place generated-but-unapproved mockups in the brandbook.

## Brand-specific styling

The canonical template controls geometry. The separately approved foundation slots control styling:

- Replace template colors with approved palette colors.
- Replace template fonts with approved fonts.
- Set every slide title in the approved display font, retain the template's exact font size, use normal letter spacing, expand its box within margins, disable wrapping, and keep it on one line.
- Choose an approved title color with at least 3:1 contrast against the slide background; title and background may never be identical.
- Keep body copy in the approved body font without auto-shrinking.
- Render the exact approved logo into distortion-safe square media slots; never stretch it or regenerate its geometry.
- Crop mockup images to the template's 3:4 slots before placement; never stretch width and height independently.
- Use approved copy only.
- Preserve readable contrast.
- Do not add decorative motifs or sections not present in the template.

## Output

Deliver:

- editable `.pptx`
- matching `.pdf`

Render page previews for internal QA only. Do not send the brandbook page by page and do not embed slide previews in the final response.

The bundled renderer runs LibreOffice in the chat sandbox and verifies embedded fonts with Fontconfig and Poppler. Never generate a separate ReportLab/custom PDF. If conversion is unavailable or times out, stop and report the script error.

A template/contract/style mismatch is deterministic. Do not retry it, present “retry Brandbook” as a next step, or dump the locked Brandkit contents into the response. Report the error in one concise sentence and stop.

The script resolves the exact approved TTF/OTF/WOFF/WOFF2 files from their public or `google:` sources before conversion. Conversion fails if Fontconfig substitutes a family or if `pdffonts` cannot confirm both approved families in the PDF. The user still needs those fonts installed to edit/view the PPTX faithfully.

Use stable names:

```text
<brand>-brand-guidelines-v<revision>.pptx
<brand>-brand-guidelines-v<revision>.pdf
```

## QA and approval

Before delivery:

1. Render every slide.
2. Check clipping, overflow, font substitution, image crop, and alignment.
3. Reject any wrapped/overlapping title or title below 3:1 background contrast.
4. Verify logo geometry and palette values.
5. Confirm the PDF visually matches the PPTX.
6. Remove all template placeholder text.

The final response contains only:

1. one PPTX download link
2. one PDF download link
3. one concise warning naming the display/body fonts the user must install for correct editable-PPTX display (include official download links when known)

Do not show page cards, inline images, contact sheets, or screenshots.

Wait for explicit approval. Only then write an `approve_brandbook_element` payload with `required_slots` set to `["logo", "palette", "typography"]` and call the Brandkit state script.
