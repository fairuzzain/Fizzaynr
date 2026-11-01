# Colored Paper Diorama Prompt System (vox-colored)

**/vox in color.** Same composition, density and materials as the /vox black-and-white
diorama (see the frames in `runs/2026-11-01_spa-malaysia-ep1/images/` — the user's reference
for what /vox should look like): aged ledger paper, newsprint, archival maps, torn paper edges,
several layered photo cutouts with rough white keylines and offset red strokes, giant numbers and
headlines on torn labels, deep diorama depth. The only change: the photos and paper are in
**vintage hand-tinted color** (like colorized 1950s photographs and old Kodachrome prints)
instead of black-and-white halftone.

History of this look (do not go back):
- v1 dense modern magazine collage (ransom notes, stickers) — cluttered. Archived in
  `assets/_archive/colored_v1/`.
- v2 minimal flat color-paper fields, 1-3 elements — too empty, "not interesting". Archived in
  `assets/_archive/colored_v2/`.
- v3 (this) = the /vox frames, tinted.

---

## 1. Structure

```
SHOT:          — variable, rewritten per clip (put it FIRST: Nexabot merges prompts that start the same)
STYLE: [STYLE BLOCK] — fixed, pasted identically every time
```

---

## 2. The Style Block (copy verbatim)

> Vintage documentary collage in hand-tinted color, built as a deep 3D paper diorama. Materials: photo cutouts of people, buildings and objects printed as colorized 1950s photographs (soft hand-tinted color, warm skin tones, faded teal, olive, ochre and brick tones, visible halftone dots and print grain), each with a rough white keyline and an offset hot-red marker stroke behind it; aged cream ledger paper, yellowed newsprint, color-tinted archival maps, torn paper edges, a few strips of masking tape. Giant stat numbers and condensed bold headline caps in ink black on torn cream labels, or white on hot-red torn labels, with hand-drawn red underlines and arrows. Palette: aged cream #EFE4CC, archival tan #C9BB9C, ink black #1A1A1A, hot red #C0392B, mustard #D9A441, faded teal #4F8A8B, cobalt accent #2F5DA8. Layered and rich like a documentary collage, several cutouts at different depths, but one clear subject and one hero number or headline. Not a flat layout: cutouts are physical layers separated in real space, strong shallow depth of field, one foreground element close to the lens. Matte print finish, never glossy. Single 16:9 frame, not a style sheet, no captions.

### Why each clause exists (do not delete these)

| Clause | Job |
|---|---|
| "vintage documentary collage in hand-tinted color" | The color: colorized period photos, not modern saturated magazine color |
| "colorized 1950s photographs… halftone dots" | Keeps the archival /vox texture while adding color |
| "rough white keyline + offset hot-red stroke" | The /vox cutout signature |
| "aged ledger paper, newsprint, archival maps, torn edges, tape" | The /vox surfaces the user liked |
| "giant numbers on torn labels, red underlines and arrows" | The /vox type and annotation language |
| "layered and rich… one clear subject and one hero number" | Rich but readable — between v1 (clutter) and v2 (empty) |
| explicit hex palette | Nexabot `img` gets no reference image |
| "deep 3D diorama, shallow DOF" | Depth, as in /vox |

---

## 3. The SHOT Formula

Same as /vox (`guidelines/image-prompts.md`), describing the **opening frame**:

```
SHOT: Background: [surface + how far + focus state].
MG: [subject cutouts at named depths].
FG: [giant number / headline on a torn label] near the lens.
Focus [what is sharp]. No other readable text, letters or numbers anywhere.
```

Use the /vox slot menus (faded world map · torn ledger page · newspaper column wall · stock
chart engraving · passport stamp field · index-card wall …), now tinted. Name at least two
depths, change the background every clip, keep text to one number or one short headline,
spelled exactly.

**Public figures:** small cutout far in the background, solid black bar over the eyes,
identified by context. Never close to the lens, no facial detail.

---

**Stray labels (learned 2026-11-01, SPA Bab 1):** the style block's "numbers and headlines on
torn labels" makes Nexabot `img` invent extra labels ("35%", "91,682", "HEADLINE",
"CONDENSED BOLD CAPS"). End every SHOT with: *"This frame has exactly ONE text element, the one
named above, spelled exactly; every other label, tag, card and scrap is blank, with no numbers,
no percentages, no words; newsprint and ledgers show only tiny blurred illegible print."* For a
frame whose only "text" is a symbol (a question mark) or a calendar, also say *"there are no
paper labels, tags, numbers or words anywhere else in this frame"*.

---

## 4. Reference Example

**SHOT:** Background: a long colonial government office of ceiling fans and tall teal shutters,
tilted, out of focus. MG: rows of wooden desks receding in deep perspective, at most desks a small
colorized cutout of a European officer in a white suit, at three different depths. FG: the giant
number "643" in white condensed caps on a hot-red torn label, close to the lens. Focus on the
nearest desks. No other readable text, letters or numbers anywhere.

---

## 5. Quick Checklist

- [ ] SHOT first, then `STYLE:` + style block verbatim
- [ ] Looks like a /vox frame, just tinted (aged paper, maps, newsprint, keylined cutouts)
- [ ] Several layers but one subject and one hero number/headline
- [ ] At least two depths explicitly stated
- [ ] Background differs from the previous clip
- [ ] Public-figure rules respected
