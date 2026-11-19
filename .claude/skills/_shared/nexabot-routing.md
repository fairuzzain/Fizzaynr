# Nexabot routing for the Higgsfield skills (mandatory)

These skills were extracted from the Higgsfield MCP connector. On this machine **nothing runs on
Higgsfield**: no Higgsfield MCP tools, no Higgsfield sandbox, no Higgsfield credits or `use_unlim`.
Keep each skill's creative workflow (planning, prompt blocks, shot logic, checks, assembly),
and swap every tool call for the local equivalent below. Where the skill names a Higgsfield model,
read it as "the Nexabot mode in this table". Do not stop to ask which engine to use.

**HARD RULE (Fizz, 2026-11-09): no paid external generation APIs, ever.** Never call, install, log in
to, or wait for Higgsfield Cloud (MCP, CLI or sandbox), Midjourney, Kling, Runway, Flux, Seedance/Dreamina
direct, fal, Replicate, or ElevenLabs visual/creative generation. Never ask the user to generate assets
there either. Images and video come only from Nexabot (fallback: Codex CLI on the ChatGPT login); voice
from Nexabot TTS / Gemini TTS; SFX from the free SFX pipeline. If a step truly needs a capability
Nexabot lacks, say so and offer a Nexabot or local workaround; do not reach for a paid service.

CLI: `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" <mode> ...` (shortened to `nexabot` below).
Before the first generation of the day, run `nexabot check` (see global CLAUDE.md).

## Generation

| Higgsfield call / model | Nexabot replacement | Cost |
| --- | --- | --- |
| `generate_image` with reference images, `soul_2`, `nano_banana_*`, `seedream_*` (i2i edits), `gpt_image_*`, `flux_*`, `ideogram_*`, `recraft_*` | `nexabot gpt-image "<prompt>" --media <ref.png> [--media ...up to 10] --aspect 1\|2\|5 --out <file>.png` | 0.10 |
| `generate_image` with no reference | `nexabot img "<prompt>" --aspect 1\|2\|5 --out <file>.png` (or `gpt-image` without `--media`, cheaper) | 0.15 / 0.10 |
| `generate_image_batch` | `nexabot batch images.json --parallel 1` (`"mode":"gpt-image"` or `"img"`; unique part of each prompt first) | per image |
| `generate_video` with a start frame (`seedance_*`, `kling*`, `veo*`, `minimax_h3`, `wan_*`) | `nexabot sfv "<prompt>" --media <frame.png> --ratio 1\|2 --res 1080 --duration <s>` | 0.15 |
| `generate_video` with 2–3 reference images / elements | `nexabot i2v "<prompt>" --media a.png --media b.png [--media c.png] --ratio 1\|2` | 0.15 |
| `generate_video` text only | `nexabot t2v "<prompt>" --ratio 1\|2 --res 1080` | 0.15 |
| `generate_video` from a reference/motion video | `nexabot r2v "<prompt>" --media clip.mp4 [--media style.png]` (10 s) | 0.15 |
| clip extension / continue a take | `nexabot extend "" --media clip.mp4` (always 1080p) | 0.15 |
| `generate_video_batch` | `nexabot batch clips.json --parallel 4` (`{name, mode, prompt, ratio, resolution, duration, media}`) | per clip |
| `generate_audio` voice-over / TTS (`elevenlabs_v4`, `list_voices`, `voice_id`) | English: `nexabot tts "<text>" --voice Fenrir --out vo.wav`. Malay: `python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/gemini_tts.py" -f script.txt -v <voice> -i "<tone>" -o vo.wav`. Pick and lock the voice with the global Voice Matching matrix; `voice_id` = that voice name. | 0.15 / free |
| `generate_audio` music (`elevenlabs_music_v2`, song/stems prompts) | `nexabot music "<prompt>" --out track.wav` | 0.15 |
| `generate_audio` sound effects / SFX kits | SFX pipeline: openverse-sfx → real-sfx → earshot (global CLAUDE.md) | free |
| `remove_background` / `remove_bg` | `nexabot gpt-image "Cleanup: remove the background and give me a PNG with a transparent background. Keep the subject exactly as it is. [Identity lock]" --media in.png` | 0.10 |

**Aspect / ratio:** images `--aspect` 1 = 1:1, 2 = 16:9, 5 = 9:16; video `--ratio` 1 = 16:9, 2 = 9:16.
Any other ratio (4:5, 3:4, 21:9, 2:3) → generate the nearest supported ratio and crop with ffmpeg.
**Resolution:** Nexabot has no 4K and no upscale. Where a skill says `resolution: '4k'`/`2k`, use the
highest Nexabot output (video `--res 1080`) and say so in the delivery note.
**Duration:** use the skill's planned clip length (`--duration` 1–60, `r2v` 10), then cut the clean
range from a 1 fps contact strip.
**Chained edits** ("feed the job id into the next tweak", i2i off a finished render): pass the
previous output file as `--media` to `gpt-image`. Change ONE thing per edit and repeat the Identity
Lock every time (global Identity Lock rules).
**Watermark:** every Nexabot clip has the Gemini ✦ mark — run `delogo` before any scaling
(9:16 1080×1920: `delogo=x=855:y=1695:w=95:h=95`; 16:9 1280×720: x 1130, y 570, 63×63).
**Text in video:** use `sfv` with a text-free start frame; Veo copies text from style sheets.

## Not available on Nexabot (say so; never fake it)

| Higgsfield capability | What to do |
| --- | --- |
| Lip-sync / talking-avatar mouth sync | Not possible. Tell the user, propose a version without visible speech (VO over B-roll, back/side angles). |
| `sam_3_video`, `sam_3_3d` (segmentation / matting) | Use local tools if installed (rembg, ffmpeg chroma/luma key); otherwise tell the user. |
| `generate_3d`, `higgsfield_3d_animation_actions` | Ask first; Blender MCP `generate_3d` may cost a credit. |
| Upscaling | Not available. Deliver at native resolution. |
| `get_presets`, `get_preset_instructions`, `/katana/<slug>` presets, the ~80 slash-command recipes | Not in this bundle. Tell the user; work from their brief or reference instead. |
| `create_website` (website-builder-flow) | Build the site locally as files (see the skill's own structure); publish only if the user asks. |

## Sandbox, media and job tools → local

| Higgsfield | Local |
| --- | --- |
| `sandbox_exec` / "the Higgsfield sandbox" | Run on this machine: PowerShell, or Git Bash for `.sh` |
| `$HF_WORKFLOWS/<skill>/scripts/<script>` | `$ROOT/.claude/skills/<skill>/scripts/<script>` (`python` not `python3`; `.sh` via `bash`) |
| `get_workflow_bundle_file`, `get_workflow_instructions` | Read `$ROOT/.claude/skills/<skill>/references/<file>` directly |
| `media_upload`, `media_confirm`, `media_upload_widget`, `media_import_url`, `media_id`, `upload_url`, `show_medias` | Local file paths. The user's attachments are already files; a URL → download it into the project folder. |
| `jobs_wait`, `show_generation_by_ids`, `show_generations`, `job_id`, `get_status`, `poll_after_seconds` | `nexabot.ts` waits and downloads at once (files vanish from Nexabot after 30 min); results land next to the batch JSON plus `nexabot-results.json` |
| `get_cost`, `models_explore`, `models_get`, `show_plans_and_credits`, `use_unlim` | Cost table above; `nexabot batch <file>.json --dry` to count and price; `nexabot credit` for balance. State count and cost before spending. |
| ffmpeg encodes | GPU: `-c:v h264_nvenc` |
| Scripts that read `HF_WORKFLOWS` (katana, reel-effects, shorts-studio, brand-asset-creation, video-montage, faceless-video, drama-ads) | In each PowerShell call, first set `$env:HF_WORKFLOWS = "$ROOT/.claude/skills"` (in Git Bash: `export HF_WORKFLOWS="$ROOT/.claude/skills"`). Workspaces the scripts put under `/home/user/...` go in the project folder instead. |
| `katana/scripts/rr.sh` bootstrap, `fetch_ref.py` private pip index (`socket.higgsfield.xyz`) | Do not use. Install missing Python packages from normal PyPI only after telling the user. |
| POSIX-only bits (`fcntl` in `ledger.py`, `.sh` helpers) | Run them in Git Bash; if a script still fails on Windows, do that step by hand with ffmpeg/Python and say so. |

## Rules that still apply on top of each skill

Global CLAUDE.md wins wherever a skill disagrees: language lock, no captions unless asked, VO
routing, SFX pipeline, Identity Lock, storyboard pre-approval before any video clips, the 4 QA gates
("Jana Sampai Sempurna"), project folder `Downloads\Video Ai\<project>` and the Google Drive sync.

## `higgsfield` CLI commands (GitHub skills: higgsfield-generate, -brandkit, -soul-id, -marketplace-cards)

These four skills drive the `higgsfield` CLI instead of MCP tools. The CLI is NOT installed and must
not be installed or logged in. Map every command:

| `higgsfield` CLI | Nexabot / local |
| --- | --- |
| `auth login`, `account status`, `workspace status` | Skip. `nexabot credit` for balance; `nexabot check` once a day. |
| `generate create <image model> --prompt ... [--image ref]` | `nexabot gpt-image` (with refs) or `nexabot img` (no refs), per the Generation table |
| `generate create <video model> ...` | `nexabot sfv` / `i2v` / `t2v` / `r2v` per the Generation table |
| `generate create <audio model>` | VO: Nexabot TTS (English) / Gemini TTS (Malay); music: `nexabot music`; SFX: SFX pipeline |
| `generate create <3d model>` | Not on Nexabot: ask first (Blender MCP `generate_3d`) |
| `generate wait`, `generate get`, `generate list`, `--wait` | Not needed; nexabot.ts waits and downloads |
| `generate cost`, `model list`, `model get` | Cost table above; `nexabot batch <file>.json --dry` |
| `generate workflow`, `workflow list`, `workflow get`, `preset list` | Server-side recipes are not available. Work from the skill's own prompt guidance and the user's brief. |
| `upload create`, `upload list`, media URLs | Local file paths passed as `--media` |
| `marketing-studio *` (avatars, products, hooks, brand-kits, ad-formats, dtc-ads, webproducts) | Not available. Use `ads-studio` / `ugc-video` skills, or build the ad from the brief with gpt-image + sfv. Avatars with lip-sync: not possible. |
| `soul-id create/get/list/wait` (train a face model) | No training on Nexabot. "Soul" = a locked reference set: 3–10 clear photos of the person kept in `<project>\soul\<name>\`, passed as `--media` to `gpt-image` (up to 10) with the global Identity Lock prompt every time; video via `sfv` from an identity-locked start frame. `--soul-id <id>` → that folder. Only with the person's consent. |
| `marketplace-cards create` (backend templates) | Backend templates are not available. Generate each card with `gpt-image --media <product.png>`: main image on pure white, product fills ~85 %, no text/props; secondary and A+ modules as separate gpt-image calls; crop to the marketplace's size with ffmpeg. |
| `higgsfield node npx ...` (brandkit local tooling) | Run the bundled script with local `node`/`npx` directly. |