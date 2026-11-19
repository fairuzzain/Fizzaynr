---
name: manga-engine
version: 1.0
description: |
  The sandbox engine behind /manga for black-and-white manga, colour manga and comics: series state,
  checks of the written steps, layout choice and every sheet, poster and page prompt. Load only from the
  /manga command; it does not draw anything by itself.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Manga engine

`manga.py` keeps a manga or comic series in one sandbox folder and builds every picture prompt from the
app's own page, sheet and layout rules (vendored in `scripts/data/`). The chat writes the creative steps
as JSON; the engine checks them, picks each page's layout from its panel count and prints the exact
generation parameters. It never calls a generation tool and never spends credits.

Run it in `sandbox_exec` as `python3 "$HF_WORKFLOWS/manga-engine/scripts/manga.py" <command> --dir <series folder>`.
Every command prints one JSON object (`show script` prints Markdown). `next` always says the one thing to
do now.

| Command | What it does |
| --- | --- |
| `new --style manga-bw\|manga-color\|comics --language L [--reading rtl\|ltr] [--aspect 2:3\|3:4\|9:16] [--chapters N] [--pages P] [--title T] [--story-file F] [--folder-id ID] [--no-poster]` | Start a series |
| `next` | The next action |
| `step concept\|designs\|plan\|script [--chapter K]` | The brief for a writing step, with its answer format and the series so far |
| `submit <step> [--chapter K] [--file F]` | Check an answer; `issues` lists what to fix, `accepted` stores it |
| `show script --chapter K` | The chapter script in plain words, for the user |
| `approve script\|price\|sheets [--chapter K] --words "<the user's reply>"` | Record the user's OK |
| `cost --chapter K` | The parameter sets to price, with counts and the redraw ceiling |
| `jobs sheets\|pages [--chapter K]` | The exact generation items, in index order |
| `record --file F \| --key K --job J [--chapter K]` | Record job ids (`[{"key", "job"}]`) |
| `review --chapter K [--page N]` | What each drawn page must show |
| `verdict --chapter K --page N --ok \| --fault "<what is wrong>"` | Record a check; a fault returns one redraw job while the ceiling allows |
| `order --chapter K` | Job ids in reading order (poster first) |
| `exported --chapter K` | Mark the chapter delivered |
| `status` | A summary |

Gates: the script must be approved before the price, the price before any sheet, and the sheets before
any page. Approvals carry the user's own words.

---
(Shared sections: see ../_shared/bundled-scripts-note.md and ../_shared/unlimited-generations-use_unlim.md)
