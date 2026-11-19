---
name: spa-kertas-to-slides
description: Turn an SPA Kertas Cadangan (Word .docx proposal paper, Bahasa Melayu) into a PowerPoint deck in the BDPK/SPA slide format, with coloured section tags (TUJUAN, LATAR BELAKANG, ULASAN URUS SETIA, CADANGAN, SYOR), the Jata cover, the DP logo, page numbers and blue tables. Use when the user asks to "buat slide", "jadikan slaid" or "ikut format BDPK" from a kertas cadangan, or to make a presentation from an SPA paper.
---

# Kertas Cadangan SPA → Slaid PowerPoint (format BDPK)

You turn an SPA proposal paper into a .pptx that looks exactly like the BDPK house deck.
You do **not** design anything. All visual elements are cloned from `assets/template.pptx`
by `scripts/build_deck.py`. Your job is to read the paper, write a **JSON content plan**,
run the script, and check the result.

## Requirements (check once)
- Python 3 with `python-pptx` and `lxml`. If the import fails, ask permission to run
  `pip install python-pptx lxml`.
- Optional, only for previewing: LibreOffice (`soffice`) and `pdftoppm`.

## Step 1 — Read the paper
- Extract the paragraphs and **every table** with python-docx:
  ```python
  from docx import Document
  d = Document("paper.docx")
  for p in d.paragraphs: print(p.text)
  for i, t in enumerate(d.tables):
      print("TABLE", i)
      for r in t.rows: print(" | ".join(c.text.strip() for c in r.cells))
  ```
- Identify the paper's sections: TUJUAN, LATAR BELAKANG, ULASAN URUS SETIA, (CADANGAN), SYOR,
  Disediakan oleh / Disemak oleh, and the "Fail SPA" reference.
- Check the table totals by adding up the yearly columns. **Never invent numbers.** Quote
  percentages only where the paper states them. If you compute something, say so on the slide.

## Step 2 — Write the plan (`plan.json`)
Follow `references/plan_schema.md`. A full worked example is in `references/example_plan.json`;
copy its structure.

Rules for the content:
- Bahasa Melayu, formal register, wording faithful to the paper. Shorten long paragraphs but
  keep the meaning, the dates, the meeting numbers (e.g. "Mesyuarat Suruhanjaya Bil. 18/2026 (3134)") and the figures exact.
- One idea per slide. Typical order: TUJUAN (statement) → LATAR BELAKANG (1–3 slides) →
  ULASAN URUS SETIA (one slide per point or table) → CADANGAN → SYOR → closing.
- Mark **key phrases** with `**bold**` and English terms with `__italic__`
  (e.g. `__One Step Lower__`). Use `"num": true` for (a), (b), (c) lists.
- Tables: reproduce the paper's tables in full. Split long ones across two slides ("(1/2)", "(2/2)").
  Use `band_rows` for JUMLAH rows, `hl_rows` and `red_cells` to highlight the point being made.
- Text limits per slide: about 120 words at 18pt for `text` slides, 15–20 rows for tables
  (size 10–12 for wide tables).
- Cover: title1 (gold line) and title2 (navy line), each at most ~35 characters in CAPITALS,
  plus a subtitle. The presenter defaults to the paper's "Disemak oleh" officer; tell the user so they can change it.

## Step 3 — Build
```bash
python scripts/build_deck.py plan.json "OUTPUT_NAME.pptx"
```
The script prints `Saved … (N slides)`. If it raises `KeyError: Shape … not found`, the user
has swapped in a different template, so ask for the original BDPK deck.

## Step 4 — Check
If LibreOffice is available:
```bash
soffice --headless --convert-to pdf OUTPUT_NAME.pptx && pdftoppm -png -r 50 OUTPUT_NAME.pdf prev
```
Look at every page. Fix the plan and rebuild if:
- text runs past the bottom (above y ≈ 6.4" is safe; the DP logo and page number sit below it). Shorten the text or split the slide;
- a note overlaps a table. Lower the table's `rowh`, reduce `size`, or move the sentence to the next slide;
- `**` or `__` shows literally (a marker is unbalanced).
If no preview is possible, re-read the plan against these limits instead.

## Step 5 — Hand over
Tell the user, in Bahasa Melayu, briefly:
- the file name and number of slides;
- the presenter name used on the cover;
- any figure you calculated yourself;
- that the section tags use the "Boeing" font, which displays correctly only on computers that have it installed.

## Icons available (`icon` field)
bullseye (Tujuan), landmark (Latar belakang), users, briefcase, chart, history (kronologi),
balance (dasar / kebaikan-kelemahan), grad (graduan), idea (Cadangan), gavel (Syor).
