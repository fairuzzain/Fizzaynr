---
name: brand-asset-creation
version: 1.1
description: >-
  Creates branded visual assets from scratch or supplied brand materials: logos, visual identities, brand kits, mockups, merchandise, packaging, signage, brandbooks, decks, social graphics, posters, and banners. Use whenever a user asks to create branding or apply/extend a logo or identity onto physical or digital assets, whether they have ready assets or need missing elements created. Includes deterministic recoloring and SVG/PNG export of existing official logos, even for a small one-color edit. Preserves supplied official assets exactly, remembers approved logo/palette/typography independently, and asks only for gaps not answered in the first message. Not for creating, updating, or listing a Marketing Studio brand-kit record: use the Marketing Studio tools for that account-management request. Also not for unbranded product photography, generic image generation, or website implementation.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Brand Asset Creation

Create a consistent system of graphic materials. Treat the user's brand facts and supplied assets as constraints, not raw material to reinterpret.

## Scope

Default to **graphic production**, not brand strategy.

- Use supplied positioning, audience, tone, copy, logo, colors, fonts, and graphic references as authoritative inputs.
- Do not invent or rewrite mission, values, positioning, audience, tone of voice, naming, or messaging unless the user explicitly asks for brand creation or strategy.
- Create a new logo or broader identity only when explicitly requested.
- Use simple visual concept boards for direction selection. Do not create broad illustration systems, photography-direction documents, motion, audio, or 3D extensions.

## User-facing progress

- Keep the internal workflow private. Never narrate Design Brain reasoning, Creative DNA, mechanisms, prompt enhancement, model discovery, tool selection, state writes, validation passes, or stage-by-stage routing.
- At most once per visible generation batch, send one short status sentence describing only the output being made, for example: “I’m generating three logo options now.”
- After that one status sentence, emit no more user-visible process text until the finished review or deliverable.
- Do not announce or explain each internal step before calling its tool. Tool activity is already visible in the interface.
- After a user chooses an option, acknowledge it briefly and move directly to the next visible output. Good: “Berry Kiss selected. I’m generating three logo options now.” Bad: “The Design Brain produced three mechanisms; now I’ll enhance each into a production prompt.”
- Design rationale shown with finished options is allowed. Process narration while producing them is not.

## Sandbox scripts and state

All Brandkit shell work runs in the remote E2B sandbox through `sandbox_exec` — never a local or client shell. This bundle's scripts are ALREADY INSTALLED there under `${HF_WORKFLOWS}/brand-asset-creation/scripts/` (`brandkit.py`, `build_brandbook.py`, `render_brandbook_pdf.py`) — nothing has to materialize them, and they are still there after `restart: true`. Run them in place:

```bash
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py state --action get_status
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py state --action <write-action> --input brandkit/input.json
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py preview --input brandkit/reviews.json
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py logo-export --input brandkit/logo-export.json
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py brandbook-build --input brandkit/brandbook.json
```

Write structured inputs with a quoted heredoc (`cat > brandkit/input.json <<'JSON' … JSON`); never interpolate user text into shell command arguments.

**The sandbox is ephemeral and shared by this user's calls, not a durable per-chat filesystem.** Follow [handoff routing](references/handoff.md): restore this conversation's latest confirmed state snapshot before use, or initialize a fresh empty ledger when this conversation has none. Never adopt leftover sandbox state. Publish every mutation as a JSON file in the same producing call; do not rely on a printed snapshot, which can exceed tool output/command limits.

**Reserve uploads before producing files.** Read [publishing](references/inline-widgets.md), call `media_upload` for the planned outputs, then run restore → render/export → `curl -f` PUT in ONE `sandbox_exec` command. Confirm only successful uploads with `media_confirm`. Never create files, return to chat to request upload URLs, and hope the sandbox is still alive. SVG/HTML/JSON/PDF/PPTX confirm as `type: "file"` (exact bytes); PNG/JPG confirm as `type: "image"`. Rasterize SVG references before image generation; never import them as images or manually rewrite their geometry.

**Command size is bounded.** `sandbox_exec.command` accepts at most 128,000 characters, including signed upload URLs. Keep payloads compact and split large output sets into self-contained batches (one HTML/PNG preview pair per call when needed). Each batch restores the confirmed snapshot and produces plus uploads its own outputs; never split a batch by leaving unpublished files for a later call.

## Core workflow

1. **Classify the request.**
   - `apply-existing`: make new graphics from supplied brand assets.
   - `extend-partial`: fill only missing visual-system decisions.
   - `create-identity`: allowed only when the user explicitly requests a new logo or identity.
   - Persist the deliverables and constraints named in the first message; never discard them or ask the user to choose scope again later.
2. **Read approvals.** Load [handoff routing](references/handoff.md), then run `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py state --action get_status` through `sandbox_exec` (restoring this conversation's state first, per that reference). Load only the needed state module later; never read unrelated state modules or infer approval from the newest generation.
3. **Load [intake](references/intake.md).** Parse the first message and attachments first. Ask one compact question set containing only genuine gaps that block the requested output; never repeat answered questions or force a full identity questionnaire for a partial task.
4. **Inventory, analyze, and lock supplied assets.** Load [asset analysis](references/asset-analysis.md). Inspect every relevant asset/page, separate official assets from inspiration, and immediately lock each user-declared official logo, palette, and typography slot through its independent `lock_authoritative_*` state action. Persist normalized visual axes with `set_visual_axes`.
5. **Determine the minimum approved slots for the requested output.** Never require a complete Essential Kit by default:
   - logo-only → logo
   - palette-only → palette
   - typography-only → typography
   - symbol mockup, merchandise, or copy-free packaging → logo; add palette when color/application decisions need it
   - text-bearing social, packaging, poster, or signage → logo + palette + typography
   - Brandbook or presentation deck → logo + palette + typography
6. **Build only missing required slots.** Load [Brandkit Design Brain](references/brandkit-design-brain.md), [concept boards](references/concept-boards.md), [inline widgets](references/inline-widgets.md), and only the missing [palette](references/palette.md), [logo](references/logo.md), or [typography](references/typography.md) module. When the user selects a generated element, immediately save only that element with `approve_palette`, `approve_logo`, or `approve_typography`; do not wait for a combined approval.
7. **Use combined review only when useful.** For a requested full identity/Brandkit, or when the user asks to see the approved elements together, render one combined HTML board from the separately approved slots. It is a presentation view, not another approval gate.
8. **Continue the original request.** As soon as its required slots are approved, proceed with the deliverables named in the first message. Do not ask the user to choose production scope again unless the original scope was genuinely ambiguous.
9. **Load only the requested output modules:**
   - Logo or logo guide → [logo](references/logo.md)
   - Color palette → [palette](references/palette.md)
   - Font recommendations or type system → [typography](references/typography.md)
   - Brandbook → [brandbook](references/brandbook.md)
   - Deck → [presentation deck](references/presentation-deck.md)
   - Carousel or social graphic → [social media graphics](references/social-templates.md)
   - Poster or banner → [posters and banners](references/posters-banners.md)
   - Packaging artwork → [packaging](references/packaging.md)
   - Signage → [signage](references/signage.md)
   - Merchandise artwork → [merchandise](references/merchandise.md)
   - Packaging, device, signage, merch, or lifestyle visualization → [mockups](references/mockups.md)
10. **Audit and approve downstream elements.** Load [QA and iteration](references/qa-and-iteration.md). Fix only the failing asset. Save a final page/template/mockup through the state script's `approve_brandbook_element` action only after explicit user approval, passing the exact `required_slots` that output actually used.

## Route guards

- **New identity:** create only the elements required by the original request. A palette used to generate a new logo is a required upstream dependency even when logo is the only requested deliverable; typography is not mandatory for a logo-only request.
- **Interactive new-logo order:** follow [concept boards](references/concept-boards.md) in order: show palette options, wait for the user's palette selection, persist it with `approve_palette`, then generate the three logo candidates. Color or style preferences from intake guide the palette options; they are not a selected palette and never authorize skipping the palette review. Only explicit auto/no-question mode may skip the review; it must still select the exact palette, persist it with `approve_palette`, and receive a successful state response before prompt-enhancement or Recraft calls.
- **Existing identity:** lock supplied official elements independently and proceed directly when the requested output's required slots are available. Never run the logo prompt enhancer or Recraft when an official logo exists.
- **Partial identity:** preserve every approved/supplied slot and create only missing slots required by the requested output.
- In interactive mode, after every visual review, STOP and wait for the user's ordinary chat response. In explicit auto/no-question mode, still show the review, persist the chosen slot, and continue without a question.
- Never infer approval from silence or tool success. Select on the user's behalf only in explicit auto/no-question mode and record that authorization in the approval summary.
- A user's explicit selection approves that specific generated element; persist it immediately through its matching `approve_*` action. Never ask for approval of unrelated or already approved slots.
- Never block a partial output on `essential_kit`. Read and require only its actual approved slots.
- Never announce or generate monochrome/reverse variants unless explicitly requested or required by the confirmed production method.

In explicit auto/no-question mode, choose and persist the required slots and their upstream dependencies, then continue the first-message deliverables. This mode does not waive state-script or review requirements. Never say that a slot is locked, selected, approved, or saved until its state-script call succeeds.

## Consistency invariants

- User-supplied official assets are fixed immediately. Each proposed/generated palette, logo, or typography option remains a draft only until the user explicitly selects that element.
- Do not create brandbook pages, social templates, decks, or mockups until required upstream locks exist in `.brandkit/state.json`.
- Treat every requested asset as its own module. Never route a specialized asset through a generic template reference.
- Reuse the same approved logo media/job reference across every output.
- Copy relevant Brand Lock values verbatim into every generation prompt: exact hex colors, font names/weights, shape language, border/radius rules, spacing, composition, and forbidden treatments.
- Never derive each asset independently. Every module consumes the same Brand Lock and changes only content, format, and composition.
- Never redraw an uploaded logo when it can be placed or composited exactly.
- Use the exact approved Recraft SVG everywhere. Never regenerate, redraw, normalize, or redraw its geometry. Color-only revisions must use `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py logo-export`.
- A requested solid palette-color/one-color logo must use the logo export script with `single_color`. Never inspect SVG paint tokens or build per-fill replacements for monochrome output.
- Never identify a font from pixels as certain. Mark it as a visual match until source metadata or a font file proves it.
- Separate generated imagery from editable layout except in the explicitly flattened social-media module. Social graphics use GPT Image 2.6 with approved logo and typography references and are never presented as editable.
- Preserve exact user copy. Do not paraphrase text that must appear in an asset.
- If the approved logo, palette, or typography changes, treat every dependent downstream element as invalidated and ask for approval again.
- Changing one approved slot never erases unrelated approved slots. Recheck dependent outputs and regenerate only what actually depends on the changed slot; never regenerate a user-supplied official logo.

## Failure policy

- For an uploaded PDF/DOCX/XLSX/CSV, follow the sandbox document route in [asset analysis](references/asset-analysis.md). If the document cannot be parsed there, stop and ask for page images or source files.
- If the Brandkit preview script fails, correct the concrete error and retry once. If it fails again, stop and report it; do not replace the HTML review with a generated image.
- If an enhanced logo prompt violates the [logo prompt enhancer](references/logo-prompt-enhancer.md) output contract, rewrite it once against the same candidate specification before submitting. If it still fails, stop.
- If a Recraft request fails, retry once with the same enhanced prompt. If it fails again, stop.
- If the Brandkit logo export script reports a geometry mismatch, stop; never fall back to generative logo editing.
- For every other logo-export failure, stop and report the exact script error; the script reports source colors when relevant. Never use unrelated shell commands, `grep`, `cp`, `sed`, ad-hoc scripts, or manual SVG rewriting as a fallback.
- If the Brandkit Brandbook build script reports a deterministic template/contract/style mismatch, stop immediately. Do not retry it or suggest retrying until the script is fixed.
- If the Brandkit Brandbook build script reports an unavailable, failed, or timed-out PDF converter, stop. Do not attempt a second conversion route.
- For social-media graphics, never use the sandbox, Python, Pillow, font downloads, or runtime installs to compose the graphic. Use the route in `social-templates.md`.
- Never describe generated assets as approved, complete, or “beautiful” without running QA and receiving the required approval.
- Never invent missions, values, flavors, prices, claims, statistics, or strategy content that the user did not provide.
- Never deliver filenames alone. Every HTML/SVG/image output must be surfaced through the appropriate review surface per [inline widgets](references/inline-widgets.md) plus its downloadable editable file.

## Existing capabilities to reuse

- For a supplied brand homepage URL, capture and analyze it in the sandbox (Playwright with headless Chromium is preinstalled) instead of guessing its contents.
- Before image generation, call `models_explore` (`action: "get"` with the target model id) and follow the returned parameter schema. Put generation arguments inside `params`. Submit distinct candidates through `generate_image_batch` with one `{index, params}` item per candidate, `count: 1`; wait with `jobs_wait` and show the completed set once with `show_generation_by_ids`. Never replace the three distinct prompts with `count: 3`.
- Ask for the desired mockup aspect ratio before generation unless already supplied. Seedream is the primary mockup generator — resolve the exact model id per [mockups](references/mockups.md). Use GPT Image 2.6 (`gpt_image_2_6`) only as a second stage when the final mockup contains readable text; preserve the exact Seedream base and apply the approved logo/text with locked placement, scale, alignment, clear space, color, and material behavior.
- Use `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py preview` only for editable HTML palette/type/combined review boards. Publish its files per [inline widgets](references/inline-widgets.md) — screenshot to PNG in the sandbox, upload PNG + HTML, show the PNGs in chat. The script never creates or modifies logos.
- Use `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py logo-export` only for an existing selected/approved Recraft SVG. It exports only the color SVG/PNG pair by default. Set `include_monochrome: true` only for explicitly requested monochrome/reverse files or a confirmed production method that requires them. Upload user-requested files and required internal raster references; SVGs uploaded via `media_upload` keep their exact bytes as editable files.
- Use `${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py brandbook-build` as the only canonical Brandbook PPTX/PDF creation path. It reads separately approved logo, palette, and typography state, preserves the fixed template contract, and emits matching local files to upload. Run it with `background: true` and poll its log — the build downloads the template and fonts and runs LibreOffice, which can exceed the foreground time limit. Never replace it with an agent-written PowerPoint script.
- Apply [logo prompt enhancer](references/logo-prompt-enhancer.md) only during new-logo creation, exactly once for each Design Brain mechanism. There is no server-side enhancer tool; you produce the enhanced prompt yourself under that contract.
- Recraft V4.1 (`recraft_v4_1`, `model_type: "vector"`) is the sole SVG logo generator.
- Use `.brandkit/state.json` only inside this workflow. Do not use user memory or any cross-chat store for Brandkit approval state; this conversation's latest confirmed state JSON URL is the durable backup, per [handoff routing](references/handoff.md).
- Read state lazily: `get_status` first; `get_logo`, `get_palette`, `get_typography`, or `get_essential_kit` only when that module is required; list/get one brandbook element rather than loading all approved extensions.
- For non-Brandbook presentation decks, follow [presentation deck](references/presentation-deck.md). Canonical Brandbooks use only the bundled Brandkit build script.

## Editable output policy

Offer the format that fits the material:

- Decks → editable `.pptx`.
- Social-media posts, stories, carousels, and banners → flattened `.png`/`.jpg`.
- Posters, logos, and individual vector layouts → editable `.svg` when the geometry can be represented faithfully.
- Digital layouts → editable HTML/CSS when requested.
- PDF and PNG/JPG are preview/final formats, not editable source.

Do not promise native Figma, Canva, PSD, AI, or EPS files. PPTX/SVG/PDF may be imported into other editors, but fonts and layout can shift. Custom fonts must be installed on the recipient's machine.

## Delivery

For a brandbook, follow the stricter final-response contract in `references/brandbook.md`: two file links plus the font-install warning only. Do not add the summary/manifest below or page-by-page previews.

For other Brandkit outputs, return only what the user requested, plus:

1. A compact Brand Lock summary.
2. A manifest of only the requested generated/editable deliverables. Keep internally hosted source logos, state snapshots and font specimens out of this list unless the user explicitly requested those files.
3. Any font/install, import, vector, or logo-fidelity limitations.
4. Clear names for each variant so the user can request a targeted revision.

---
(Shared sections: see ../_shared/bundled-scripts-note.md and ../_shared/unlimited-generations-use_unlim.md)
