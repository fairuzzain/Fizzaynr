---
name: rbdigital-nexabot
description: Generate images, videos (Omni Flash 1.2, NexaDance 3.0, Veo), music and text-to-speech through the NexaBot API (nexabot.id) from the workspace shell. Use when the user asks to generate/buat gambar, video, lagu, muzik, suara or TTS, or invokes /rbdigital-nexabot or /Rbdigital-nexabot.
---

# RBDigital NexaBot Generate (Reseller & Unlimited API)

Generates images, video (Omni Flash 1.2, NexaDance 3.0, Veo), music and TTS through the NexaBot API (https://nexabot.id), using the user's own API key and credit. Run calls from the workspace shell with `bun nexabot.ts` or `scripts/nexabot.py`.

Reply in the user's language (Bahasa Melayu santai if they write in Malay), short and practical.

## Mandatory Daily API & Documentation Check Before Generating
Every time before generating any assets with Nexabot (and globally at the start of each day), verify any changes across:
1. **Developer Docs**: https://nexabot.id/developers
2. **API Docs**: https://nexabot.id/api-docs
3. **Live Modes & Voices**: `https://nexabot.id/api/v1/modes` (auth: `x-api-key`)
4. **Automated CLI Check**:
   ```powershell
   bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check [--force]
   # Or using python runner:
   python <skill>/scripts/nexabot.py check [--force]
   ```
If any new endpoint, model, mode, duration, or parameter changes are detected, update `nexabot.ts` immediately before proceeding.

## Settings (the user fills these in)

API_KEY: PASTE_KEY_KAU_KAT_SINI
TELEGRAM_ID: PASTE_TELEGRAM_ID_KAT_SINI

- Note: The script automatically checks `${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/.env.nexabot`, env vars (`NEXABOT_KEY` / `NEXABOT_API_KEY`), or `API_KEY` above.
- TELEGRAM_ID is optional. The API key automatically authenticates all endpoints including GPT Image 2.5.

## Step 0 — Get the key (every session)

1. Read API_KEY above. If it still says `PASTE_...` or is empty, the script auto-reads from `${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/.env.nexabot` or `NEXABOT_KEY`/`NEXABOT_API_KEY` env. If none exist, look for a key the user gave earlier in this chat (starts with `nxb_`). If there is none, ask once in one short message: "Bagi API key NexaBot kau (bermula nxb_). Ambil kat nexabot.id → bahagian API." Then wait.
2. Never print the key back in replies, never write it into delivered files, never put it in URLs or anything sent anywhere except nexabot.id.
3. First time in a session, verify API status and check the balance:
   ```powershell
   bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check
   bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" credit
   ```
   - 401 → the key is wrong or revoked; ask for the right key.
   - NETWORK error → tell the user in one line that Claude/agent can't reach nexabot.id from here, and that they need to allow network access to `nexabot.id`, then try again.
   - 402 / balance too low → tell them to top up credit at nexabot.id. Mention that the web "Unlimited" plan does NOT cover the API; only API credit or the separate "API Unlimited" plan does.

`<skill>` = the folder that holds this SKILL.md.

## Costs (always report model + cost + remaining balance after generating)

| what | cost (credit) | on API Unlimited plan |
|---|---|---|
| Video models (Omni Flash 1.2, NexaDance 3.0, t2v, sfv, i2v, r2v, extend) | 0.4 / video, refunded on failure | Free (0 credit) |
| General requests (img, music, tts) | 0.15 / request, refunded on failure | 0.15 credit |
| GPT Image 2.5 (`gpt-image`) | 0.1 / image | always charged |

### Plan API Unlimited
- Memberikan penjanaan tanpa potong kredit (0 kredit) untuk **Omni Flash 1.2** dan **NexaDance 3.0** via API.
- Maksimum **14 request paralel serentak per user**. Request ke-15 dan seterusnya automatik masuk antrean dan jalan sendiri apabila slot kosong.
- Hanya terpakai untuk request API dengan header `x-api-key` atau `Authorization: Bearer`. (Plan Unlimited web tidak cover API).
- Pengecualian: GPT Image sentiasa memotong kredit (0.1 kredit).

## Image Generation Models

- **GPT Image 2.5 (`gpt-image`)**: **0.10 credit / image** (cheaper than standard img!). Supports up to **10 visual reference images** via `--media <ref1.png> --media <ref2.png>`! Endpoint: `POST /api/v1/gpt-image`. Use this whenever visual reference / style matching / character consistency / photo edits are needed directly in Nexabot without external paid tools.
- **Google Image (`img`)**: 0.15 credit, 768×1376-class JPG, ~22 s. Text-only (no reference images). `aspect` 1 = 1:1, 2 = 16:9, 5 = 9:16.

## Video Generation Models

- **Omni Flash 1.2 (`omni`)**: 10 s clip (Full HD 1080p default, 720p also supported), ~180s, 0.4 credit (percuma atas plan API Unlimited). Optional start frame image `media[0]`. Ratio 1 = 16:9, 2 = 9:16. Prompt opsional bila ada start frame.
- **NexaDance 3.0 (`nexadance`)**: 20 s clip, SELALU 720p, supports audio, ~360s, 0.4 credit (percuma atas plan API Unlimited). Best for full kinetic action/story. Text-to-video (tiada media input). Ratio 1 = 16:9, 2 = 9:16. Prompt up to 10,000 chars. (Legacy `seedance` commands automatically route here).
- **Veo / Google Vids video modes (`t2v`, `sfv`, `i2v`, `r2v`, `extend`)**: 0.4 credit. Durasi default 15s (1–60; `r2v` 10s). Resolution 720p/1080p (default 720p; `extend` SELALU 1080p). Can also specify `--model omni|nexadance`.

## How to run

Pick aspect/ratio: 9:16 for reels/stories (ratio 2, aspect 5), 1:1 default for images, 16:9 for landscape (ratio 1, aspect 2).

```bash
# Bun CLI runner:
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check [--force]
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" credit
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" gpt-image "<prompt>" [--media ref1.png --media ref2.png] --aspect 5 --out out1.png
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" img "<prompt>" --aspect 1 --out out1.jpg
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" omni "<prompt>" --ratio 2 --res 1080 --media start.png --out omni.mp4
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" nexadance "<prompt>" --ratio 2 --out dance.mp4
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" sfv "<prompt>" --media frame.png --ratio 2 --res 1080 --out clip.mp4
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" batch clips.json --parallel 4 [--dry]

# Or Python runner:
python <skill>/scripts/nexabot.py check
python <skill>/scripts/nexabot.py credit
python <skill>/scripts/nexabot.py gpt-image "<prompt>" [--media ref1.png] --aspect 5 --out out1.png
python <skill>/scripts/nexabot.py omni "<prompt>" --ratio 2 --resolution 1080 --media start.png --out omni.mp4
python <skill>/scripts/nexabot.py nexadance "<prompt>" --ratio 2 --out dance.mp4
python <skill>/scripts/nexabot.py music "<description or lyrics>" --out m.wav
python <skill>/scripts/nexabot.py tts "<text>" --voice Kore --out vo.wav
```

After it finishes:
1. Look at the result before sending (for video, check a few frames or 1 fps strip).
2. Report model, cost, remaining balance.

## API reference

- Base `https://nexabot.id`.
- Autentikasi: header `x-api-key: <key>` atau `Authorization: Bearer <key>`.
- Submit all modes to `POST /api/v1/api` `{mode, model?, prompt?, ratio?, resolution?, duration?, aspect?, voice?, media?}`.
  - Video models: `omni` (10s default, 720|1080p, optional start frame), `nexadance` (20s, 720p, audio support).
  - Video costs 0.4 credit (0 credit on API Unlimited).
  - Other requests cost 0.15 credit (img, music, tts).
  - GPT Image 2.5 costs 0.1 credit (`POST /api/v1/gpt-image`, up to 10 reference images in `references`).
- Status `GET /api/v1/jobs/<id>` → `{ok: true, job: {status: queued|processing|done|failed, model, model_label, progress, error}}`.
- Download `GET /api/v1/jobs/<id>/download`.
- Balance `GET /api/v1/api/credit` → `{ok: true, telegram_id, registered, credit, credit_cost: 0.15, video_credit_cost: 0.4, video_models: ["omni", "nexadance"]}`.
- Modes & Voices `GET /api/v1/modes`.

TTS voices (30 voices): Achernar, Achird, Algenib, Algieba, Alnilam, Aoede, Autonoe, Callirrhoe, Charon, Despina, Enceladus, Erinome, Fenrir, Gacrux, Iapetus, Kore, Laomedeia, Leda, Orus, Puck, Pulcherrima, Rasalgethi, Sadachbia, Sadaltager, Schedar, Sulafat, Umbriel, Vindemiatrix, Zephyr, Zubenelgenubi.
