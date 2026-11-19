---
name: "natural-text-cleanup"
description: "Clean up AI-drafted text so it reads natural and sounds like the author: fix copy-paste artifacts, cut generic AI phrasing (English and Bahasa Melayu), keep facts locked, and report every change."
---

# Natural Text Cleanup

Turn stiff, generic AI-drafted text into clean, natural writing in the author's own voice. Works for English and Bahasa Melayu (scripts, captions, VO, articles, posts).

Treat this as three separate jobs. Never let one silently become another:
1. FORMAT — invisible characters, broken spacing, pasted styling.
2. QUALITY — wording, rhythm, voice, clarity.
3. PROVENANCE — disclosures, attribution, content credentials. These are preserved, never removed.

## Workflow (reversible, six steps)

1. **Duplicate** — Keep the original untouched. Work on a copy. If the input is a file, never overwrite it; write `<name>_cleaned.<ext>`.
2. **Inventory** — Note language (EN / BM / mixed), format (plain, markdown, docx, srt, caption), intended use (VO script, caption, article), and any required disclosure (e.g. platform AI label, sponsor tag, client attribution).
3. **Normalize (format pass)** — Fix without changing words. Run the script below on text, or do the same by hand.
4. **Rewrite (quality pass)** — Edit for natural voice using the pattern list below. Lock: facts, numbers, prices, specs, names, model names, dates, quotes, citations, links, technical terms.
5. **Compare** — Produce a change report. Restore anything that changed meaning.
6. **Publish** — Return the cleaned text. Keep any disclosure or attribution that was in the original or that the user's platform/client requires.

## Step 3 — Format normalization

```python
import re, unicodedata, collections

def normalize(text):
    counts = collections.Counter()
    invisible = {'\u200b':'zero-width space','\u200c':'ZWNJ','\u200d':'ZWJ','\u2060':'word joiner','\ufeff':'BOM','\u00ad':'soft hyphen'}
    for ch, label in invisible.items():
        n = text.count(ch)
        if n: counts[label] += n; text = text.replace(ch, '')
    spaces = {'\u00a0':'no-break space','\u202f':'narrow no-break space','\u2009':'thin space','\u2002':'en space','\u2003':'em space','\u3000':'ideographic space'}
    for ch, label in spaces.items():
        n = text.count(ch)
        if n: counts[label] += n; text = text.replace(ch, ' ')
    quotes = {'\u201c':'"','\u201d':'"','\u2018':"'",'\u2019':"'"}
    for ch, rep in quotes.items():
        n = text.count(ch)
        if n: counts['curly quote'] += n; text = text.replace(ch, rep)
    n = text.count('\r'); text = text.replace('\r\n','\n').replace('\r','\n')
    if n: counts['CR line ending'] += n
    text, n = re.subn(r'[ \t]{2,}', ' ', text); counts['duplicate spaces'] += n
    text, n = re.subn(r'[ \t]+\n', '\n', text); counts['trailing spaces'] += n
    text, n = re.subn(r'\n{3,}', '\n\n', text); counts['extra blank lines'] += n
    text = unicodedata.normalize('NFC', text)
    return text.strip(), {k:v for k,v in counts.items() if v}
```

Only convert curly quotes if the user wants plain ASCII; otherwise keep them consistent. Report the counts.

## Step 4 — Patterns that make text sound generic

Fix these where they appear. Don't strip all of them mechanically; edit until it sounds like a person talking.

**English**
- Filler openers: "In today's fast-paced world", "When it comes to", "Let's dive in", "In this article we will".
- Stock words: delve, tapestry, testament, realm, landscape, navigate, elevate, unleash, seamless, robust, game-changer, boasts, nestled.
- Hedges and signposts: "It's worth noting that", "It's important to remember", "Ultimately", "In conclusion", "Overall".
- Structures: "not just X, but Y"; every list in threes; every paragraph the same length; a summary sentence closing each paragraph; heavy em-dash use; rhetorical question then answer.
- Over-politeness and hype: "truly remarkable", "absolutely", stacked adjectives.

**Bahasa Melayu**
- Pembuka klise: "Dalam era digital ini", "Dalam dunia yang serba moden ini", "Tidak dapat dinafikan bahawa", "Seperti yang kita sedia maklum".
- Penutup klise: "Secara keseluruhannya", "Kesimpulannya", "Oleh itu, jelaslah bahawa".
- Terjemahan literal dari English: "memainkan peranan penting", "di hujung hari", "mengambil tempat", "membuat keputusan yang bijak" berulang-ulang.
- Terlalu formal untuk kandungan santai: "anda" bertubi-tubi dalam skrip video; tukar ikut gaya penulis (kau / korang / kita / tuan-puan) hanya jika itu memang gaya mereka.
- Ayat panjang bertingkat dengan "yang" berulang; pecahkan.
- Rojak: kekalkan jika itu gaya asal penulis; jangan paksa jadi BM baku.

**What to do instead**
- Lead with the point. Cut the warm-up sentence.
- Vary sentence length. Mix short punchy lines with longer ones.
- Use concrete detail (the actual spec, the actual feeling, the actual example) over abstract praise.
- Match the author's register. If samples of their past writing exist, copy their habits: slang, sentence length, how they open and close.
- For VO scripts: write for the ear. Short lines, natural pauses, words people actually say.

## Locked elements (never change)

Numbers, prices, specs (hp, Nm, cc, km/j, RM), model and brand names, dates, quotes, citations, links, legal or sponsor wording, technical identifiers. If a sentence's meaning is unclear, flag it rather than guess.

## Step 5 — Output format

Return, in this order:
1. **Cleaned text** — ready to use.
2. **Format fixes** — counts from the normalization pass.
3. **Change report** — substantive edits, grouped (cut filler / reworded / restructured). List anything that could alter meaning and needs the author's confirmation.
4. **Kept as-is** — any disclosure, attribution or credential that was preserved.

For files (docx, srt, md): output a cleaned copy, then check it opens, pages/timings are intact, links and images survive.

## Boundary

This skill improves readability and voice. It does not:
- remove required AI disclosures, platform labels, sponsor tags or client attribution;
- strip watermarks, signed content credentials (C2PA) or provenance metadata;
- target AI detectors or help submit work where a school, publisher or client requires disclosure of AI assistance.

If the user asks for any of those, say so in one line and continue with the normal cleanup.