---
name: video-qa-auditor
description: Automated Zero-Defect Video Quality Assurance Auditor & Prompt Gatekeeper. Audits prompts, keyframes, 1 fps clip strips, delogo watermark removal, audio synchronization, and final video renders to ensure zero hallucinations, zero anachronisms, zero weird artifacts, and publish-ready perfection before delivery ("jana sampai sempurna").
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Video QA Auditor & Zero-Defect Gatekeeper

This skill enforces rigorous quality control across all video generation workflows (Vox diorama, Nexabot Veo, Seedance, HyperFrames, Remotion, and Commercial Videos).

It acts as an uncompromising quality gatekeeper to guarantee that:
1. No video or image contains weird, hallucinated, unrelated, or bizarre elements.
2. No anachronisms or cultural/religious misrepresentations occur (e.g. Western crosses in Islamic history, wrong racial defaults, modern objects in ancient settings).
3. Quality is guarded upfront in prompts via surgical negative constraints.
4. Only 100% defect-free assets are accepted into the final assembly.
5. If any defect is detected: **JANA SAMPAI SEMPURNA** (re-prompt and regenerate until flawless).

---

## The 4 Quality Inspection Gates

```
+-----------------------------------------------------------------------------------+
| GATE 1: PROMPT HARDENING & CONTEXT LOCK                                           |
| (Strict negative prompts, anti-hallucination, exact spelling, cultural rules)     |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| GATE 2: KEYFRAME STILL IMAGE AUDIT                                                |
| (Inspect composition, typography spelling, zero stray symbols, style lock)        |
| [FAIL] -> Adjust prompt and regenerate image                                      |
+-----------------------------------------------------------------------------------+
                                         │ [PASS]
                                         ▼
+-----------------------------------------------------------------------------------+
| GATE 3: 1-FPS VIDEO CLIP CONTACT STRIP AUDIT                                      |
| (Frame-by-frame 1 fps scan: zero morphing, zero stray labels, isolate peak payoff)|
| [FAIL] -> Re-roll clip or isolate clean window (src & speed)                      |
+-----------------------------------------------------------------------------------+
                                         │ [PASS]
                                         ▼
+-----------------------------------------------------------------------------------+
| GATE 4: FINAL ASSEMBLY, OUTRO & WATERMARK VERIFICATION                            |
| (Verify clean delogo, sentence-pause cuts, outro hold, smooth visual/audio fades) |
| [FAIL] -> Re-assemble with exact timing adjustments                               |
+-----------------------------------------------------------------------------------+
                                         │ [PASS]
                                         ▼
                              PUBLISH-READY MASTER MP4
```

---

## Gate 0: Daily Nexabot API & Engine Verification (Mandatory Check)

Before submitting any prompt or generation to Nexabot (and globally at the start of each day), verify that the API is fully synchronized:
1. **Live Sources**:
   - `https://nexabot.id/developers`
   - `https://nexabot.id/api-docs`
   - `https://nexabot.id/api/v1/modes`
2. **Automated CLI Check**:
   ```powershell
   bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check [--force]
   ```
3. **Model Selection & Reference Matching**:
   - Video: Omni Flash 1.2 (`omni`, 10s, 720p/1080p, 0.4 credit) or NexaDance 3.0 (`nexadance`, 20s, 720p, 0.4 credit).
   - Images with references / character consistency: Use GPT Image 2.5 (`gpt-image`) supporting up to 10 visual references at 0.10 credit.
4. If any endpoint or model change is detected, update `nexabot.ts` immediately before rendering.

---

## 1. Gate 1: Prompt Hardening & Context Audit

Before generating any image or video clip, the prompt must be audited against these rules:

### 0. Mandatory Language Consistency Gate
* **Malay Topic / Title:** 100% Bahasa Melayu across ALL outputs: narration/VO script, on-screen typography, captions (if requested), and storyboard. No rojak/English mixing unless official proper nouns.
* **English Topic / Title:** 100% English across all narration, typography, captions (if requested), and script beats.
* **Auto-Lock:** The language of the topic/title automatically sets and locks the project language.

### 0.1 Mandatory No-Caption Gate (Strictly Unless Requested)
* **Strict Default (NO SUBTITLES / NO CAPTIONS):** JANGAN masukkan sebarang sarikata, speech captions, closed captions, atau karaoke word-by-word subtitles ke dalam video akhir merentasi SEMUA skill melainkan pengguna secara eksplisit memintanya ("masukkan caption", "add subtitles", dll.).
* **Visual Design vs Captions:** Teks tajuk, label rajah/peta/diorama, dan statistik (*graphic callouts*) dibenarkan kerana ia sebahagian daripada reka bentuk visual. Transkripsi percakapan alih suara perkataan demi perkataan adalah DILARANG secara default.
### A. Context & Cultural Guardrails
* **Islamic Historical & Religious Scenes:**
  * Explicitly enforce: *natural desert stones, simple uncarved rock cairns, ancient Arabian shields and spears*.
  * NEVER use generic words like *"memorial markers"*, *"cemetery"*, or *"tombstones"* (these trigger Western AI bias to generate Christian gravestones and crosses).
  * Mandatory AVOID clause: `NO crosses, NO crucifix, NO Christian tombstones, NO church symbols, NO religious icons, NO faces of Prophet/Sahabah`.
* **National & Regional Contexts:**
  * Prevent foreign/Western architecture hallucinations in Asian or Malaysian historical topics.

### B. Typography & Text Lock
* AI models frequently hallucinate gibberish or duplicate text.
* Always enforce: `This frame has exactly ONE text element, '<EXACT_TEXT>', spelled exactly. All other textures are paper grain.`
* Explicitly prohibit Veo from generating new text during motion: `no new text appearing, no warped or gibberish text, no invented logos, no watermarks`.

### C. Visual Discipline & Movement Constraints
* Append the universal quality blocker in every video prompt's `AVOID` section:
  ```text
  AVOID: no plastic CG, no flat single-plane composition, no static locked-off camera,
  no anatomical deformities, no morphing or melting objects, no moving mouths or lip-sync
  when unnarrated, no stray numbers, no random prompt labels (no 'ALERT WASH' text),
  no watermarks, no music, no voice-over
  ```

---

## 2. Gate 2: Keyframe Image Audit

* Generate the keyframe image first.
* Inspect using `read_file` or visual inspection:
  1. **Subject Integrity:** Are figures and objects cleanly cut out with proper silhouettes and zero extra limbs?
  2. **Typography Check:** Is the text spelled 100% accurately according to the brief?
  3. **Zero Stray Artifacts:** Are there any floating numbers, random labels, or unrelated objects?
* **Action on Failure:** If any defect is found, edit the prompt and re-roll the image immediately. Do NOT feed a flawed keyframe into video generation.

---

## 3. Gate 3: 1-FPS Video Clip Strip & Collision Audit (The `cinematic-qc-auditor` Standard)

Video models (such as Veo and Seedance) often start clean for the first 3 seconds, but begin hallucinating text, random numbers, morphing objects, or physically clipping through solid geometry between seconds 4 and 10.

* **Mandatory Physical Collision & Phasing Inspection:**
  - **The Vehicle Door / Rigid Geometry Rule:** Characters exiting vehicles MUST exit through physically open doors on hinges. If an actor's body clips/phases through the car's B-pillar, window, or solid metal, the clip is an **IMMEDIATE HARD REJECT**.
  - **Prop & Hand Interaction:** Hands must naturally grasp props (steering wheels, pens, cups); fingers must never penetrate or fuse into solid surfaces.
  - **Low Pixel Delta is NOT a Pass:** Smooth clipping motion produces deceptively low pixel variance. Always inspect the exact region of human-object interaction at full resolution.

* Run the automated strip extractor:
  ```bash
  python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/qc_gatekeeper.py" strip <path_to_clip.mp4>
  python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/qc_gatekeeper.py" contact-sheet <path_to_clip.mp4>
  ```
* Review the 10 extracted frames:
  1. **Morphing Check:** Do solid objects (rocks, cliffs, props) melt, distort, or warp unnaturally?
  2. **Unwanted Lip-Sync:** Do characters move their mouths as if singing or talking when there is no talking-head narration?
  3. **Stray AI Artifacts:** Did the model draw prompt instructions or random numbers in the background?
  4. **Payoff Timing:** Identify the exact start offset (`src`) and `speed` that captures the dynamic movement and ends on a settled, clean frame.
* **Action on Failure:** If a clip morphs or produces foreign artifacts, re-prompt with hardened negative constraints and re-generate.

---

## 4. Gate 4: Final Assembly & Watermark Verification

* **Delogo Check:** Run automated crop audit to verify the Gemini watermark is cleanly erased from the bottom-right corner:
  ```bash
  python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/qc_gatekeeper.py" audit-delogo <path_to_final.mp4>
  ```
* **No-Caption Verification (Strict Default):** Pastikan video akhir bersih daripada sebarang sarikata atau speech captions (burn-in/subtitles), MELAINKAN pengguna secara khusus memintanya. Sekiranya ada caption tanpa permintaan, tolak dan jana semula tanpa caption.
* **Audio Balance:** Narration voiceover (e.g. Google Gemini `Fenrir` for Bahasa Melayu Malaysia) must sit prominently above music (music volume ~0.10–0.14, clip SFX ~0.15).
* **Outro & Transition Finish:**
  * Must feature an **outro hold** of 2.0 to 3.0 seconds after the last spoken word.
  * Must include a smooth **visual fade to black** (1.5s to 2.0s).
  * Must include a gentle **audio decay/fade-out** (2.0s to 3.0s).
  * Never allow abrupt cuts at the start or finish.

---

## The "Jana Sampai Sempurna" Execution Loop

When acting as the Video QA Auditor:
1. **Never accept compromise:** If an artifact is visible to a human viewer, it will be noticed by audience/clients.
2. **Diagnose root cause:** Determine whether the defect was caused by prompt ambiguity, missing negative triggers, or video model drift.
3. **Surgical Re-prompt:** Apply the corrective keyword or negative constraint.
4. **Re-roll & Re-audit:** Re-render the asset and run the inspection again until zero defects remain.
