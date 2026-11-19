# Color Grade source bundle

Adapted from the user-supplied `color-grade-skill.zip` (archive README credits
`@ai.volve.news`). Contains the NumPy/OpenCV grading engine, image/video runners,
comparison helpers, reusable-look builder and all 20 supplied movie-look recipes
and statistics. No movie stills are bundled.

The slash command and lazy references live under
`src/tools/preset-instructions/resources/commands/color-grade/`. Both OpenAI/Claude
and Full use the sandbox engine. Full has separate attachment-intake wording.
This does not install a native host skill or reproduce the screenshot's host UI.

Look JSON lives under `scripts/looks/` so the existing sandbox bundle sync includes
it. Script look paths were adjusted accordingly. Runtime dependencies already
exist in `scripts/e2b-template-assets/python/requirements.txt`; no new installation
or dependency versions are introduced. The archive's unpinned requirements and
TMDB HTML scraper are intentionally not shipped: unsupported movie names require
user reference stills. Image writes and video subprocess failures must propagate.

Run the deterministic offline smoke test with the sandbox Python dependencies:

```bash
python3 src/tools/workflows/resources/color-grade/scripts/smoke.py
```

It tests synthetic images, reference matching, LUT export, comparison output and
both video modes with audio. No model/backend calls or external media are needed.
