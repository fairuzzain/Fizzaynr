---
name: uncut
description: "AI-first video editor for macOS (by Błażej Kustra) and agent video editing pipeline. Drive Uncut's timeline over local MCP (http://127.0.0.1:47821/mcp) to open footage folders, execute timeline edits, trim, resequence, inspect transcripts, burn captions, and export (FCPXML, EDL, MP4). Includes 15 production recipes: launch-promo, product-demo, talking-head, social-cutdown, explainer, title-sequence, motion-craft, sound-design, brand-application, make-brand-kit, loudness-rules, echo-cleanup, broll-over-dialogue, cut-takes, and motion-film."
---

# Uncut Video Editor & Production Pipeline

[Uncut](https://github.com/blazejkustra/uncut) is an open-source, AI-first video editor for macOS (MIT licensed). It couples AI coding agents (Claude Code, Antigravity, Codex) directly to a professional multi-track timeline, allowing agents to plan, cut, trim, synchronize audio, add kinetic titles, and export projects while users retain full manual timeline control.

---

## 1. Outside Agent Connection & Architecture

Outside agents connect to Uncut over its local JSON-RPC Model Context Protocol (MCP) server.

### Connection Details
- **Endpoint**: `http://127.0.0.1:47821/mcp`
- **Transport**: HTTP (SSE / JSON-RPC)
- **Authentication**: Bearer token required in the `Authorization` header (`Authorization: Bearer <token>`).
- **Token Location (macOS)**: `~/Library/Application Support/Uncut/external-mcp-token`
- **Enabling in Uncut**: Turn on **Settings › App › Outside agents**, then generate or view the token.
- **Safety**: Binds strictly to loopback (`127.0.0.1`), rejects foreign Host or Origin headers, and prompts user confirmation for destructive/large-scale edits.

### Claude Code CLI Integration
The plugin is installed via Claude Code:
```sh
claude plugin marketplace add blazejkustra/uncut
claude plugin install uncut@uncut
```
This enables the command:
```sh
/uncut:open-footage <path-to-footage>
```

---

## 2. Core Agent Editing Protocol

When driving Uncut via MCP or scripting video edits:

1. **Inspect Before Acting**:
   - Call `project_read` to inspect active tracks, canvas dimensions, frame rate, clip markers, and `baseRevision`.
   - If no project is open, use `project_open` pointing to a footage directory or `.uncut` project bundle.
2. **Atomic Timeline Edits**:
   - Always supply `baseRevision` from the last `project_read` to `timeline_edit`.
   - All positions and durations are **integer frame counts** calculated at the project's native FPS (e.g. 24, 25, 29.97, 30, 60).
   - Group related clip splits, trims, and additions into a single `timeline_edit` batch with a human-readable summary.
3. **Verification via `render_frames`**:
   - After modifying transitions, titles, graphics, or layout, call `render_frames` on key frames to inspect rendered composition and legibility.
4. **Approval Gates**:
   - Substantial modifications (deleting tracks, bulk removals, wiping media, deep transcript cuts) trigger a user **Allow** dialog in Uncut. Wait for confirmation.

---

## 3. Uncut MCP Toolset Reference

| Tool | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `project_open` | Opens a footage folder or `.uncut` project bundle | `path` |
| `project_read` | Returns active project state, tracks, clips, FPS, and `revision` | None |
| `project_peek` | Lightweight track inspection without full project dump | None |
| `timeline_edit` | Executes timeline operations (insert, split, trim, move, remove) | `baseRevision`, `ops`, `summary` |
| `render_frames` | Renders visual stills at designated frame numbers for review | `frames` (array of integers) |
| `media_analyze` | Analyzes clip loudness (LUFS), silences, and audio profile | `mediaId` |
| `media_rank` | Ranks candidate media takes based on quality and criteria | `mediaIds`, `rubric` |
| `transcript_read` | Extracts word-level timestamped transcript from local whisper.cpp | `mediaId` |
| `transcript_edit` | Executes transcript-based text cuts across speech tracks | `cuts` |
| `captions_make` | Generates timed captions / burned-in subtitle tracks | `style`, `safeArea` |
| `subtitles_export` | Exports subtitles to SRT or WebVTT | `format`, `outPath` |
| `timeline_export` | Exports project timeline to FCPXML 1.10 or CMX 3600 EDL | `format` ("fcpxml" or "edl") |
| `export_video` | Renders master MP4 / ProRes video file | `codec`, `preset`, `outPath` |
| `project_check` | Audits timeline for defects, gaps, and missing assets | None |

---

## 4. Timeline Interchange (FCPXML & EDL)

Uncut seamlessly roundtrips with Final Cut Pro and DaVinci Resolve:

- **Main Track**: Maps to the FCPXML spine / EDL primary picture track.
- **Overlays & Text**: Maps to connected clips in lanes above spine.
- **Audio Stems**: Maps to connected audio clips in lanes below spine.
- **Clips & Stills**: Maps to `asset-clip` and `video` elements.
- **Crossfades**: Written as standard `Cross Dissolve`.
- **Gain Adjustments**: Mapped to `adjust-volume`.

*Note: Custom shaders, LUTs, and proprietary graphic components are exported as gaps or basic dissolves with warnings.*

---

## 5. Visual Critic & Quality Rubric

Uncut's automated critic audits rendered frames for visual defects. Avoid these measured failure modes:

1. **Hard Cuts & Quick Swaps**: Avoid accidental 1-frame cuts or swapping dominant canvas elements across 2–3 frames.
2. **Single-Frame Pops & Flashes**: Never leave temporary assets or placeholders visible for 1–2 frames.
3. **Low-Information Frames**: Flagged if canvas is empty/bare for >0.33s or shows tiny text in flat field for >0.5s.
4. **Edge Clipping & Mobile Legibility**: Text must never clip outside platform safe margins. Headline text must be legible at 360px viewport width.
5. **Authentic Assets**: Brand logos and marks must be imported from authentic files (`brand_read`), never synthesized or redrawn.

---

## 6. Uncut Production Recipes (The 15 Bundled Skills)

Uncut includes 15 battle-tested editing recipes. Detailed instructions for each recipe are available in the `references/` directory:

- **[Launch promo](./references/launch-promo.md)** (`/launch-promo`): A 15 to 30 s launch film: hook, problem, reveal, proof, call to action.
- **[Product demo](./references/product-demo.md)** (`/product-demo`): A demo built on real UI recordings: tight crops, cursor and state changes that read.
- **[Talking-head short](./references/talking-head.md)** (`/talking-head`): A 9:16 short cut from a talking head, with burned-in captions and real b-roll.
- **[Social cut-down](./references/social-cutdown.md)** (`/social-cutdown`): One edit delivered as 9:16, 4:5, 1:1 and 16:9 cuts, each safe for its platform.
- **[Explainer](./references/explainer.md)** (`/explainer`): How it works in 30 to 90 s: one idea per beat, diagrams built step by step.
- **[Title sequence and kinetic type](./references/title-sequence.md)** (`/title-sequence`): Type as the picture: a hierarchy, holds you can read, motion that follows the words.
- **[Motion craft](./references/motion-craft.md)** (`/motion-craft`): Springs per object class, holds, readability, and the clichés to avoid.
- **[Sound design](./references/sound-design.md)** (`/sound-design`): Few, quiet, synced sound effects; music matched to the pace; ducking under voice.
- **[Brand application](./references/brand-application.md)** (`/brand-application`): The kit applied with restraint: colours by role, fonts, logo files, tone.
- **[Make a brand kit](./references/make-brand-kit.md)** (`/make-brand-kit`): Builds a brand kit from a link or dropped logos and pictures: asks a few questions, then saves the kit with the brand tools.
- **[Loudness rules](./references/loudness-rules.md)** (`/loudness-rules`): Levels a mix by measurement: a target per platform, voice and music set from the exported numbers, true peak under the limiter.
- **[Echo cleanup across mics](./references/echo-cleanup.md)** (`/echo-cleanup`): Removes bleed and doubled voices from a recording with one mic per speaker, by lowering each open mic while another person talks.
- **[B-roll over dialogue](./references/broll-over-dialogue.md)** (`/broll-over-dialogue`): Lays real cutaways over a talking cut: picks moments from the transcript, keeps the dialogue audio, times each shot to the words.
- **[Cut takes](./references/cut-takes.md)** (`/cut-takes`): Turns a long recording with retakes into a tight talk: reads the transcript, keeps the best take of each line, removes false starts.
- **[Motion film](./references/motion-film.md)** (`/motion-film`): Facts for a motion film on the real UI or footage: honesty about the run, the defects Uncut measures and blocks, the toolkit. The creative direction is yours, or a Template's.

---

## 7. Quick Recipe Lookup

| Recipe | Best For | Typical Length | Format |
| :--- | :--- | :--- | :--- |
| `launch-promo` | Product & feature launch announcements | 15–30s | 9:16 or 16:9 |
| `product-demo` | Software UI walkthroughs and action demonstrations | 30–60s | 16:9 or 9:16 |
| `talking-head` | Creator monologues with punch-ins & captions | 30–60s | 9:16 vertical |
| `social-cutdown` | Multi-format delivery from a master cut | 6–30s | 9:16, 4:5, 1:1, 16:9 |
| `explainer` | Concept breakdowns, architectural diagrams | 30–90s | 16:9 or 9:16 |
| `title-sequence` | Kinetic typography, title stings, typographic hooks | 5–15s | Any |
| `motion-craft` | Spring physics, easing rules, motion refinement | Any | Any |
| `sound-design` | Foley sync, audio ducking, soundtrack pacing | Entire cut | Any |
| `brand-application` | Applying corporate colors, type, and logos | Entire cut | Any |
| `make-brand-kit` | Generating structured `brand.json` from assets | Setup | Data |
| `loudness-rules` | Platform-specific audio mastering (LUFS, True Peak) | Mastering | Audio |
| `echo-cleanup` | Phase cancellation & bleed reduction on multi-mic setups | Ingest | Audio |
| `broll-over-dialogue` | Strategic cutaways timed to speech transcript | Timeline | Any |
| `cut-takes` | Best-take selection & false start elimination | Ingest | Any |
| `motion-film` | Pure UI motion graphic films with strict critic gates | 15–45s | Any |

---

## 8. Workflow Checklist

When executing an Uncut edit:
1. [ ] Confirm project FPS and resolution (`project_read`).
2. [ ] Align audio cuts with speech transcripts or downbeats (`transcript_read`, `media_analyze`).
3. [ ] Assemble spine on Main track before adding connected B-roll or text layers.
4. [ ] Apply ducking: music lowered 12–18 dB beneath active dialogue (`sound-design`, `loudness-rules`).
5. [ ] Render sample frames (`render_frames`) at start, major transitions, and CTA.
6. [ ] Audit against the Critic Rubric (no 1-frame flashes, safe areas respected, text readable on mobile).
7. [ ] Export to desired platform master or interchange format (`export_video`, `timeline_export`).
