---
name: color-grade
description: Sandbox source bundle for the explicitly selected /color-grade command.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Color Grade

Load `get_preset_instructions` with `{"preset":"/color-grade"}` and follow the
command and its references. The command owns intake, preview and delivery rules.
The scripts and look data are installed at `$HF_WORKFLOWS/color-grade/scripts`.

---
(Shared sections: see ../_shared/bundled-scripts-note.md and ../_shared/unlimited-generations-use_unlim.md)
