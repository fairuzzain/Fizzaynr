---
name: shorts-studio
description: Sandbox scripts of the /shorts command (reels.py and the HTML render engine). Not a workflow on its own; load the instructions with get_preset_instructions {"preset":"/shorts"}.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Shorts Studio scripts

The `/shorts` command owns the instructions. Load them with
`get_preset_instructions` `{"preset":"/shorts"}` and follow them; the scripts
here are synced to `$HF_WORKFLOWS/shorts-studio/scripts/` in the sandbox.

---
(Shared sections: see ../_shared/bundled-scripts-note.md and ../_shared/unlimited-generations-use_unlim.md)
