---
name: talking-head-prompt-generator
description: Membuat prompt video talking head yang realistis, natural, detail, dan siap produksi untuk berbagai AI video generator, lengkap dengan panduan pelafalan (pronunciation notes) Bahasa Melayu Malaysia, slanga Malaysia, istilah Inggeris/AI, dan CTA. Gunakan saat pengguna ingin membuat prompt talking head, prompt video UGC, prompt avatar berbicara, mengubah naskah/dialog atau gambar referensi menjadi prompt video talking head, atau membutuhkan panduan pelafalan agar lip sync dan suara AI terdengar natural.
---

# Talking Head Prompt Generator

> **Bahasa utama: Bahasa Melayu Malaysia.** Semua output skill ini (skrip, VO/TTS, dialog, caption,
> teks atas skrin, CTA, tajuk, kapsyen media sosial) dan semua soalan serta laporan kepada pengguna
> ditulis dalam Bahasa Melayu Malaysia: ejaan, kosa kata dan loghat Malaysia, bukan Bahasa Indonesia.
> Bahasa lain hanya jika pengguna memintanya. Prompt untuk model imej/video boleh kekal dalam Bahasa
> Inggeris, tetapi teks yang diucapkan atau dipaparkan di dalamnya tetap Bahasa Melayu. Peraturan ini
> mengatasi mana-mana default bahasa lain dalam fail ini. Lihat `CLAUDE.md` → Bahasa.

Create simple, realistic, direct, production-ready talking-head video prompts for any AI video generator. Convert optional reference images, exact dialogue or voiceover text, and optional style instructions into a concise prompt with accurate pronunciation guidance and natural creator-style delivery.

## When to Use

- User wants to generate a talking-head or UGC-style AI video prompt from dialogue or voiceover text.
- User uploads a reference image and wants a talking-head video prompt that preserves identity and environment.
- User asks for realistic lip sync, natural Malaysian Malay creator delivery, or phonetic pronunciation notes for AI video generation.

## Inputs

The user may provide any combination of the following inputs:

### 1. Reference Image (Optional)

If a reference image is provided, analyze and preserve all key visual traits unless the user explicitly asks to change them:

- Face identity and facial structure
- Eyes, nose, lips, and skin tone
- Hairstyle, outfit, and accessories

### 2. Dialogue / Voiceover (Primary Input)

Treat the dialogue as the most important input and copy it verbatim:

- Do not rewrite, shorten, paraphrase, or improve wording.
- Do not translate the dialogue.
- Do not change slang or informal Malay words, and do not make the dialogue more formal.
- Do not correct grammar or remove repeated words or filler words.
- Only adjust punctuation when strictly needed for natural spoken pacing.

### 3. Additional Instructions (Optional)

Always follow explicit user preferences such as:

- Framing: handheld, selfie, vlog, static camera, tripod, fixed camera
- Setting: bedroom, office, outdoor, luxury, casual
- Delivery and mood: serious, fast delivery, whispering, emotional, calm, energetic
- Special audio or action: ASMR, finger snap, pointing gesture, holding or showing a product

## Core Rules

### Camera Rule

- If the user requests handheld, selfie, or vlog, use: `"realistic smartphone front-camera handheld framing"`.
- If the user requests tripod, static camera, or fixed camera, use: `"static camera feel"` and always add `"no tripod appear"`.
- If the user does not specify camera style, infer from the reference image:
  - Use **STATIC CAMERA** when the subject is sitting on a bed or chair, standing indoors, posed, or framed stably.
  - Use **HANDHELD** when a selfie angle is obvious, arm extension is visible, or creator/vlog style fits better.
- Default preference when unspecified: **STATIC CAMERA** (include `"no tripod appear"`).

### Environment Rule

- If a reference image exists, preserve the room, furniture, lighting, background, mood, atmosphere, color tone, camera distance, and framing style. Do not invent a different environment unless explicitly requested.
- If no reference image exists, generate a simple, realistic environment that matches the dialogue and feels natural for Malaysian social media creator content. Avoid overly cinematic or unrealistic sets unless requested.

### Dialogue Formatting Rule

Always present the user's exact dialogue cleanly:

```text
Dialogue (Malaysian Malay, natural casual delivery):
"Dialog line 1"
"Dialog line 2"
```

Adapt the parenthetical language and delivery label if the user requests another language or delivery style.

### Pronunciation Notes Rule

AI video generators frequently mispronounce informal Malaysian Malay words, slang, shortened words, English words inside Malay sentences, brand names, AI terms, uncommon words, all-caps words, and comment CTA words. Whenever dialogue is present, always include a mandatory `Pronunciation notes:` section.

- Only include words or phrases that actually appear in the dialogue.
- Prioritize these categories:
  1. English words inside Malay dialogue
  2. AI-related terms
  3. Brand and product names
  4. Words written in uppercase
  5. CTA words
  6. Malaysian slang and shortened or non-standard words
  7. Words with multiple possible pronunciations or awkward phrasing in AI speech
- Use practical phonetic guides (IPA phonetic spelling, Malay-friendly syllable breakdown, English/Malay pronunciation note, natural spoken version, or stress/emphasis note).
- Do not overdo simple, safe everyday words, but when in doubt, include slightly more pronunciation notes rather than too few.
- If a sentence mixes Malay and English (very common in Malaysia), add a mixed-language note: natural Malaysian creator-style delivery where Malay words use natural Malaysian Malay pronunciation (Malaysian accent, not Indonesian) and English terms are pronounced clearly in Malaysian-English style depending on common social media usage.

#### Reference Pronunciation Examples

English, AI, and creator-economy terms (Malaysian creator usage):

- `"AI"` = pronounce in English as `eɪˈaɪ` (Malaysian creators also say `"ei-ai"`)
- `"UPGRADE"` = pronounce in English as `ʌpˈɡreɪd`
- `"tools"` = pronounce in English as `tuːlz`
- `"prompt"` = pronounce as commonly spoken in Malaysian tech talk: `"promt"`
- `"custom GPT"` = Malaysian-English creator style: `"kas-tem ji-pi-ti"`
- `"generate"` = `"je-ne-reit"`, `"generator"` = `"je-ne-rei-ter"`
- `"workflow"` = pronounce in English as `ˈwɜːrkfloʊ`
- `"content"` / `"kandungan"` = `"kon-ten"` when used as Malaysian creator slang, otherwise `"kan-du-ngan"`
- `"video"` = natural Malay `"vi-di-o"`
- `"realistic"` = `"ri-a-lis-tik"`, `"hyper realistic"` = `"hai-per ri-a-lis-tik"`
- `"digital"` = natural Malay `"di-ji-tal"`
- `"komen"` = `"ko-men"` in Malay CTA context
- `"DM"` = letter by letter `"di-em"`
- `"link"` = `"lingk"`, `"bio"` = `"bai-o"`
- `"reel"` = `"ril"`, `"template"` = `"tem-plet"`

Malaysian informal words and slang:

- `"tak"` = short `"tak"`, never `"tidak"`; `"takde"` = `"tak-de"`
- `"nak"` = short `"nak"`, not `"hendak"`
- `"je"` = `"je"` (short), `"lah"` = `"lah"` (light, unstressed tail), `"kot"` = `"kot"`, `"kan"` = `"kan"`, `"pun"` = `"pun"`
- `"ni"` = `"ni"`, `"tu"` = `"tu"`, `"camni"` = `"cam-ni"`, `"camtu"` = `"cam-tu"`
- `"aku"` = `"a-ku"`, `"korang"` = `"ko-rang"`, `"kitorang"` = `"ki-to-rang"`, `"awak"` = `"a-wak"`
- `"dah"` = `"dah"`, `"belum"` = `"be-lum"`, `"tengok"` = `"te-ngok"`, `"cuba"` = `"cu-ba"`
- `"best"` = English-style `"best"`, `"gila"` = `"gi-la"` (as intensifier), `"weh"` = `"weh"`, `"wei"` = `"wei"`
- `"memang"` = `"me-mang"`, `"macam"` = `"ma-cam"`, `"sikit"` = `"si-kit"`, `"banyak"` = `"ba-nyak"`
- `"ya"` = `"ya"`, `"yer"` = slightly extended `"yer"`

CTA words (especially uppercase):

- `"Taip UPGRADE kat ruang komen"` -> `"UPGRADE"` (`ʌpˈɡreɪd`), `"kat"` (`"kat"`), `"komen"` (`"ko-men"`)
- `"Komen NAK kalau nak template"` -> `"NAK"` (`"nak"`, short, stressed), `"template"` (`"tem-plet"`)

#### Mandatory Closing Lines for Pronunciation Notes

Always end the `Pronunciation notes:` section with these two lines (adjusting language if the dialogue is not Malay):

```text
All other words remain natural Malaysian Malay pronunciation (Malaysian accent, not Indonesian).
Use natural Malaysian Malay lip sync, natural pacing, and realistic mouth movement.
```

### Special Action Rule

Only include special actions when they are visible in the reference image or explicitly requested by the user (for example: finger snap, pointing gesture, showing or holding a product, raising hand, looking away then back to camera, smiling, whispering, leaning closer, slight head movement). Never invent unnecessary gestures or product interactions.

### Audio Rule

- Default: `"No background music. Natural room ambience only."`
- If the user requests ASMR, describe the exact sound clearly (for example: crisp finger snap sound, page turning sound, keyboard typing sound, product tapping sound, soft fabric movement sound, subtle breathing sound, quiet room tone).
- Do not add sound effects unless explicitly requested.

### Delivery Rule

Match the requested delivery style:

- **Fast delivery**: `"Fast but still clear Malaysian Malay creator-style delivery."`
- **Whispering**: `"Soft whispering voice, close and intimate delivery, but still clearly understandable."`
- **Serious**: `"Calm serious tone, controlled facial expression, natural eye contact."`
- **Energetic**: `"Energetic creator-style delivery, expressive but not exaggerated."`
- **Default (unspecified)**: `"Natural casual Malaysian Malay creator-style delivery, Malaysian accent."`

### Realism Rule

- Prioritize: realistic motion, natural blinking, natural breathing, natural facial and head micro-movements, realistic eye movement, subtle body movement, authentic human skin texture (no over-smoothing), natural mouth shape while speaking, realistic lip sync, and believable creator-style delivery.
- Avoid: plastic skin, CGI look, robotic motion, exaggerated acting, beauty filter appearance, unnatural mouth movement, incorrect lip sync, frozen face, stiff posture, overacting, unnatural smile, and fake influencer expression.

## Output Structure

Keep the final prompt concise, direct, and ready to paste into any AI talking-head video generator. Do not add unnecessary sections, long cinematic descriptions, or filler explanations.

```text
Talking head UGC style.
[Character description]
[Environment description if needed]
[Camera description]

Dialogue (Malaysian Malay, natural casual delivery):
"[Exact user dialogue]"

Pronunciation notes:
- [Word-by-word pronunciation rules for risky/English/slang/CTA words present in the dialogue]
All other words remain natural Malaysian Malay pronunciation (Malaysian accent, not Indonesian).
Use natural Malaysian Malay lip sync, natural pacing, and realistic mouth movement.

[Special action if needed]
[Audio requirements]
[Short realism sentence]
```

## Gotchas

- Never alter, formalize, or translate the user's dialogue.
- Never include pronunciation notes for words that do not appear in the dialogue.
- Never invent hand gestures, props, or environment changes that contradict the reference image or were not requested.
- Prioritize realism, accurate pronunciation guidance, natural delivery, and lip sync over lengthy cinematic prose.
