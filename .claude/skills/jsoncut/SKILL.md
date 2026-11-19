---
name: "jsoncut"
description: "Pull out, delete or inspect fields in a JSON file or stream with the jsoncut CLI. Use when someone says jsoncut or wants specific values from a JSON file."
---

# jsoncut

A small command-line tool for selecting or removing fields in a JSON document. Run it with Bash.

## 1. Make sure it is installed and working

```bash
which jsoncut && echo '{"a":1}' | jsoncut -n -g a
```

If that fails, install it and patch it. Version 0.6 is old and crashes on Python 3.10+ because it imports `Mapping`/`Sequence` from `collections`:

```bash
pip install --break-system-packages jsoncut
D=$(python3 -c "import importlib.util,os;print(os.path.dirname(importlib.util.find_spec('jsoncut').origin))" 2>/dev/null || python3 -c "import site;print(site.getsitepackages()[0]+'/jsoncut')")
sed -i 's/^from collections import Mapping, deque, namedtuple/from collections import deque, namedtuple\nfrom collections.abc import Mapping/' $D/inspector.py $D/treecrawler.py
sed -i 's/^from collections import Sequence/from collections.abc import Sequence/' $D/sequencer.py
echo '{"a":1}' | jsoncut -n -g a   # expect {"a":1}
```

Note: `find_spec` itself imports the package and may fail before the patch; the fallback path covers that.

## 2. Look at the document first

Always pass `-n` (no colour codes) so the output is clean.

- `jsoncut -n -i -f file.json` — every key path with its type, counts and min/max. Best first step on an unfamiliar file. Array elements show as `#`.
- `jsoncut -n -l file.json` — numbered list of top-level keys.
- `jsoncut -n -c file.json` — element count of a top-level array.

## 3. Select and delete

Key paths use dots; array indexes are numbers (`cars.1.brand`).

- Get one or more fields: `jsoncut -n -g cars.0.brand -g cars.0.price file.json`
- Keep the full path in the output: add `-p`
- Delete a key or element: `jsoncut -n -d cars.0 file.json`
- Pretty-print for a file: add `-I 2` and redirect, e.g. `jsoncut -n -g cars -I 2 file.json > out.json`
- Reads stdin when no file is given: `cat file.json | jsoncut -n -g key`

## Known quirks (tested)

- `-r/--root` combined with `-g` gives KeyNotFound errors. Use the full dotted path with `-g` instead.
- `-G/--getdefault` is broken (it writes a bogus key into the output). Don't use it; if a key may be missing, check with `-i` first.
- On a missing key it prints KeyNotFound plus the available keys. Use that list to fix the path.

## When jsoncut isn't enough

For filtering by value, mapping over arrays, or reshaping, use `jq` (check `which jq`) or a short Python script with `json` instead of forcing jsoncut.

## Not this tool

"JsonCut" is also the name of a JSON-to-video rendering cloud API (it has a Make.com app). That is unrelated to this CLI; if the person means the video service, say so and don't use this skill.