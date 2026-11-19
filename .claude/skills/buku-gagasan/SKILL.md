---
name: buku-gagasan
description: Write a complete book on any title from source material (speeches, slides, analysis tables, notes, a previous edition) in one run, then act as editor and lay it out for print/Canva. Covers front matter, chapters, closing, titles, cover brief, Word manuscript and a designed page layout. Use for "tulis buku", "buku gagasan", "buat buku daripada ucapan/slaid", corporate or organisational books, compilations and books of thoughts. Default language Bahasa Melayu.
---

# Buku Gagasan: source material to a finished, laid-out book

Writes **every section of a book in one run** (not one prompt per section), assembles one manuscript, then — on request — acts as **editor + layout designer** and produces a print-ready layout that can be brought into Canva.

Default book language: **standard Bahasa Melayu (DBP spelling)** unless the user picks another. Talk to the user in the language they use.

Reference files (read when the step says so):
- `references/editorial-rules.md` — rules every book must pass + the editor checklist
- `references/writing-prompts.md` — the writing specs for each section (BM prompts)
- `references/layout-guide.md` — design system, page types, how to fill `assets/layout-template.html`, Canva hand-off
- `references/preset-spa.md` — house rules for Suruhanjaya Perkhidmatan Awam (SPA) books (use only when the user names SPA)
- `assets/layout-template.html` + `assets/example-data.json` — the layout engine and a worked example
- `scripts/build_docx.py` — builds the .docx manuscript (only if you can run Python)

---

## Step 1 — Book profile: ask ONCE, then work

Check what is attached. Ask everything still missing **in one round**, then start. Never ask section by section.

| # | Input | Notes |
|---|---|---|
| 1 | Title / working title | Can be rough; you will offer 3 refined options. |
| 2 | Book type | Corporate/organisational, motivational, guide, memoir, compilation, book of thoughts (gagasan). |
| 3 | Main message & audience | One sentence + who reads it. |
| 4 | Source material | Speeches, slides, analysis tables (xlsx), notes, reports, a previous edition. |
| 5 | Chapter structure | (a) user outline; (b) one chapter per source file; (c) **one chapter per letter of an acronym** (e.g. B.E.R.S.A.M.A.); (d) you propose. |
| 6 | Front matter | Perutusan, Prakata, Penghargaan, Dedikasi + name & position for each. |
| 7 | Owner context | Organisation: vision, mission, values, strategic plan. Personal: author background. |
| 8 | Length | Default: intro 2,500–4,500 words; chapters 1,800–3,000; closing 1,000–1,500. If a **previous edition** is attached, match its length and structure instead. |
| 9 | House style / preset | A named preset or attached guideline **overrides** defaults. |

Rules for this step:
- If an answer is unclear (e.g. the user answers with a file name or a word that is not one of the options), ask one short clarifying question instead of guessing.
- If the user says they will attach more material, **wait** for it before writing.
- If the user is not around, take the most reasonable reading, state it at the top of your summary, and carry on.
- **Never invent** numbers, dates, names, programmes or quotes. Mark every gap `[PERLU DISAHKAN: ...]`.

## Step 2 — Read all sources properly

- Text files/PDFs: extract the text. **Image-only slides** (no extractable text): look at every slide image and transcribe titles, taglines, acronym definitions, pantun/quotes, design cues (patterns, colours).
- Spreadsheets: read every sheet and every row; analysis tables often map *concept → values → programmes* — keep that mapping, it becomes chapter content and chapter-opener panels.
- **Previous edition of the book**: treat it as the format reference — copy its section order, chapter shape (title style, length, sub-headings or not, quote placement, award/icon pages, photo pages with captions) and its continuity facts (last year's theme and achievements). Use its facts only as background/continuity, never as this year's achievements.
- If the user attaches an editorial guideline, read it first; it overrides this skill.

## Step 3 — Brief + content map (required before writing)

Write a short brief: title, type, message, audience, tone, owner context, chapter plan (chapter → working title → sources → core message), **content map** (every programme/story/figure/quote → the chapter it fits, nothing repeated, no empty chapter), and the house-style rules that apply. Every section is written against this brief.

**Acronym styling:** keep the owner's exact styling everywhere, including the cover title. If the owner writes `B.E.R.S.A.M.A.` with dots, every reference to the concept uses the dots (and never produces a double full stop at sentence end). Ordinary uses of the word ("bersama-sama") stay normal. Confirm with the user if unsure.

## Step 4 — Write every section (in this order)

Use the specs in `references/writing-prompts.md`. Order: Bab Pengenalan → every chapter → Penutup → front matter (Perutusan, Prakata, Penghargaan, Dedikasi) → titles (3 options each; book title evergreen, no year unless asked).

For every chapter:
- Turn speech into narrative (remove greetings, protocol, "tuan-tuan dan puan-puan").
- Arc: situation → challenge → change/action → resolution and lesson.
- Explain the *value/meaning* of each programme, not just the fact.
- Where a programme's 2026/current status is unknown, write it as direction/intent and add `[PERLU DISAHKAN: status ...]`.
- Quotes at the **end** of the chapter (rules in `editorial-rules.md`).
- Placeholders: 2–4 `[FOTO: subject — caption | Tarikh & lokasi: PERLU DISAHKAN]` per chapter; `[IKON: ...]` if the previous edition had award pages.
- Sub-headings: follow the previous edition; default **none** for narrative books.

**Length honesty:** if the sources are too thin to reach the target length without filler or invented facts, stop at the honest length, say so in the summary, and point to the `[PERLU DISAHKAN]` gaps as where the chapters will grow when material arrives.

## Step 5 — Design & cover brief (Lampiran A)

Concept and visual symbols; 2–3 cover concepts in words; colours from the owner's corporate palette (no guessed hex codes); list every photo placeholder chapter by chapter so photos can be collected at once.

## Step 6 — Assemble the manuscript

Default output: one **Word (.docx)** manuscript.
- If you can run Python: write each section as a markdown file and run `scripts/build_docx.py` (see its header for usage).
- If you cannot run code: output the full manuscript in clean Markdown, section by section, in the order below, so the user can paste it into Word/Google Docs.

Order: Cover · Copyright/ISBN page · Sidang Editorial (placeholders) · Dedikasi · Perutusan · Prakata · Penghargaan · Kandungan · Bab Pengenalan · Bab 1…N · Penutup · Rujukan · Lampiran A (design brief) · Lampiran B (alternative titles, sensitive terms, full `[PERLU DISAHKAN]` list).

## Step 7 — Editorial check, then deliver

Run the checklist in `references/editorial-rules.md` and report it as a short table. Deliver with a short summary: chapters, total words, number of photo/quote placeholders, the `[PERLU DISAHKAN]` list, decisions for the editorial board, and an **ISBN reminder** (apply to Perpustakaan Negara Malaysia in parallel with editing).

## Step 8 — Editor + fresh layout (when the user asks for layout / design / Canva)

Act as the book's editor and designer. Follow `references/layout-guide.md`:
1. Editor pass: move production notes (Lampiran A/B) out of the print layout; turn inline `[PERLU DISAHKAN]` paragraphs into **"Nota Editor · Perlu Disahkan"** boxes; give Perutusan/Prakata a portrait frame + signature block; add a chapter-opener panel per chapter (e.g. Prinsip / Nilai / Programmes) from the source mapping.
2. Fill `assets/layout-template.html` with `BOOK` and `SECTIONS` data (schema and example in the guide and `assets/example-data.json`). Page size defaults to the previous edition's size (SPA: B5 176 × 250 mm).
3. Deliver the single HTML file. The user opens it in Chrome → Print → Save as PDF (paper size from the file, margins None, Background graphics ON).
4. **Canva:** drag the PDF onto the Canva home page (or Upload) → Canva converts it into an editable multi-page design. Fonts used (Playfair Display, Lora, Montserrat) exist in Canva. If a Canva connector is available and can create a design from an uploaded file, use it; otherwise give the user these steps. Never upload the user's files to a public hosting site to get a URL.
5. After any later text change (e.g. acronym styling), update both the manuscript and the layout so they never drift apart.
