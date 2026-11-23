# Nexabot API — quick reference

Source: https://nexabot.id/developers, checked against the live API on 2026-11-23.
Python client: `.claude/skills/vox-colored-nexabot/scripts/common.py` (`Nexabot` class).
The `nexabot.ts` CLI lives in `vendor/Motion_as_kit` (not in this repo) — update it there.

- Base URL `https://nexabot.id`. Auth: `x-api-key: nxb_...` (or `Authorization: Bearer nxb_...`). JSON bodies.
- **2026-11-11:** the only video model is `omni_flash` (Omni Flash 1.2). `model=omni`, `veo` etc. → 400.
  `/api/v1/seedance` is gone (404).

## Endpoints

| Method | Path | What | Credits |
|---|---|---|---|
| POST | `/api/v1/api` | async job: `t2v sfv i2v r2v extend img music tts` | video 0.3, others 0.15 |
| GET | `/api/v1/jobs/:id` | job status: `queued processing done failed` | – |
| GET | `/api/v1/jobs/:id/download` | result file (409 not ready, 410 expired) | – |
| POST | `/api/v1/image` | sync premium image, returns `url` | 0.1 |
| GET | `/api/v1/image` | image model list | free |
| POST | `/api/v1/voice` | sync ElevenLabs TTS, returns `url` + `timestamps` | 0.02 |
| GET | `/api/v1/voices` | ElevenLabs voices (`voice_id`, languages, features) | free |
| POST | `/api/v1/voice/clone` | `{audio: data-URI 15-60 s, name, gender}` → `voice.voice_id` | free, 5/min |
| GET | `/api/v1/api/credit` | balance + costs | – |
| GET | `/api/v1/modes` | modes, video models, `tts` voice names | – |

## POST /api/v1/api

| Field | Notes |
|---|---|
| `mode` | required |
| `model` | `omni_flash` (default for video modes) |
| `prompt` | required except `extend` |
| `ratio` | video: 1 = 16:9, 2 = 9:16 |
| `resolution` | 720 \| 1080 (`extend` always 1080) |
| `duration` | seconds, 1-60, default 15 |
| `aspect` | `img` only: 1 = 1:1, 2 = 16:9, 5 = 9:16 |
| `voice` | `tts` only, e.g. `Achernar` (default), `Charon`, `Kore`, `Puck` (30 names, see `/modes`) |
| `media` | base64 data URIs: `sfv` 1 image · `i2v` 1-3 images · `r2v` 1 video + 0-1 image · `extend` 1 video |

Reply: `{ok, job_id, status, download_url, model, credit_cost, credit_balance, est_seconds}`.
Poll every 2-5 s. **Files are deleted 30 min after the job finishes** — download right away.
An identical media-less request while the first is still running returns the same `job_id` at 0 credits.
Omni Flash output has no watermark (so no delogo needed).

## Sync endpoints (use a 3-5 min HTTP timeout)

- `POST /api/v1/image` `{model, prompt, aspect?, resolution?}` for `nano_banana_2` (aspect auto/21:9…1:8,
  resolution 0.5K-4K), `nano_banana_2_lite`, `nano_banana_pro`, `nano_banana`;
  `{model, prompt, image_size?}` for `gpt_image_2`, `gpt_image_2_5_flare`, `gpt_image_2_5_sunburst`,
  `mai_image_26_flash`, `mai_image_26`, `mai_image_25`, `mai_image_25_pro`
  (`landscape_4_3 landscape_16_9 square_hd square portrait_4_3 portrait_16_9 auto`).
- `POST /api/v1/voice` `{text ≤5000, voice_id, language_code="id-ID", speed 0.5-2, stability, similarity_boost, style}`
  (the last three only where the voice's `features` allow).

## Plans and errors

API Unlimited (24 h, 3/7/14 parallel) makes **video** free only; image and voice are always charged.
Errors are `{ok:false, error}`: 400 bad model/mode/media · 401 key · 402 credits · 403 not your job ·
404 job unknown · 409 not ready · 410 expired · 429 rate limit · 502 upstream (refunded) · 503 engine down (not charged).
