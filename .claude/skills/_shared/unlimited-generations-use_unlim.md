## Generation cost (Nexabot) — replaces Higgsfield `use_unlim`

There are no Higgsfield credits or unlimited generations here. All image, video and music generation
goes through Nexabot (see `nexabot-routing.md`): img 0.15, gpt-image 0.10, t2v/sfv/i2v/r2v/extend 0.15,
music/tts 0.15. Never pass `use_unlim`. Before a batch, run `--dry` and state the count and cost;
for a new style, generate one test and look at it before the rest.