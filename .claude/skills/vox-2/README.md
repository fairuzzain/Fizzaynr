# Vox-style collage explainer (a Claude skill)

Give Claude a topic, and it makes a short animated explainer in a hand-made mixed-media collage style: black-and-white halftone cut-outs, yellow paint, ink notes drawn with p5.brush, grid paper, newspaper clippings and ransom-note type. Claude researches the topic, writes a fact-checked script, generates the narration and pictures, and renders an MP4.

> "Make a Vox-style video about why the sky is blue"
> "Explainer animation: how do noise-cancelling headphones work? 20 seconds"
> "Short collage video on why onions make you cry"

## Install

- **Claude Code / Claude desktop (Code tab):** unzip `vox-collage-explainer.skill` into `~/.claude/skills/` (you should end up with `~/.claude/skills/vox-collage-explainer/SKILL.md`), or ask Claude to install the `.skill` file for you.
- **Claude apps with skill upload:** upload the `.skill` file in Settings → Capabilities → Skills.

Claude does the rest on first use: it runs `scripts/vox.py setup`, which installs the render engine into `~/.vox-collage-explainer` (about 1 minute).

## What the computer needs

- A Claude environment that can run shell commands (Claude Code, the desktop app's Code tab, or Cowork).
- Node.js 18+, ffmpeg and Python 3. On a Mac: `brew install node ffmpeg`. Claude will tell you if they're missing.
- Nexabot (images, English TTS, music) and gemini_tts.py (Malay VO). No ElevenLabs.
- macOS gives the cleanest cut-outs (Apple Vision); other systems use a colour-key fallback that works well with the plain backdrops the prompts ask for.

## Cost

A 10-second video on Nexabot is about 0.6–0.9 credit: 0.15 per img (3–4 images), 0.10 per gpt-image reference edit, 0.15 for English TTS (Malay VO free), 0.15 for an optional music bed.

## What's inside

```
SKILL.md                    the workflow Claude follows
references/storyboard.md    the storyboard format (beat types: subject, diagram, chart, stat, closer)
references/image-prompts.md prompts that produce clean cut-outs
scripts/vox.py              setup, cut-outs, timing, layout, brush rendering, final render
scripts/layout.py           beat layouts
scripts/render_brush.mjs    p5.brush renderer (headless Chrome)
engine/                     Remotion project that draws the scenes
assets/sfx/                 bundled sound effects
examples/tickle/            a complete worked example
```

## Credits and licences

- [p5.brush](https://github.com/acamposuribe/p5.brush) by Alejandro Campos (MIT) draws every mark.
- [Remotion](https://www.remotion.dev) renders the video. It is free for individuals and small teams; larger companies need a Remotion company licence (see remotion.dev/license).
- Fonts (Libre Caslon Text, Permanent Marker, Special Elite, Anton) are from Google Fonts (SIL Open Font License).
- The paper textures are generated in code. The bundled sound effects were made with ElevenLabs by the skill's author.
