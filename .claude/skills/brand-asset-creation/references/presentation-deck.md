# Presentation deck

Create once logo, palette, and typography are separately approved. Do not ask for another combined approval.

Read `get_essential_kit` through the Brandkit state script. Build the deck in the sandbox via `sandbox_exec`.

## Intake

Require:

- deck purpose
- audience
- source content
- desired slide count
- exact claims/data
- requested aspect ratio
- existing PPTX template, if any

Do not invent mission, values, market statistics, pricing, claims, contacts, or product variants to fill slides.

## Build

- Existing PPTX → edit its masters/layouts (unpack/repack the OOXML in the sandbox).
- No template → create a small coherent layout family with a sandbox PPTX library (e.g. `npm install pptxgenjs` or `pip install python-pptx` inside the batch that uses it — the sandbox is ephemeral).
- Use approved logo, palette, and fonts.
- Keep all text/shapes editable.
- Keep imagery replaceable.
- Use generated imagery only as optional supporting assets.
- Do not flatten whole slides into images.

Create only slide types required by the content, such as cover, divider, image/copy, comparison, process, data, quote, and closing.

## QA and approval

Render slides for inspection with headless LibreOffice in the sandbox (`soffice --headless --convert-to pdf`, then `pdftoppm`), fix, and re-render. Check overflow, collisions, alignment, font substitution, contrast, and placeholder residue.

Deliver editable PPTX plus previews/PDF when requested (upload via `media_upload` → `curl` PUT → `media_confirm`, `type: "file"`). Save only the approved deck through `approve_brandbook_element` using key `presentation-deck` and `required_slots: ["logo","palette","typography"]`.
