---
name: "madame-grimelda-nexabot"
description: "Use when the user gives a topic for a Madame Grimelda video and wants the video GENERATED via the Nexabot API (nexabot.id), not just a prompt: writes the prompt, generates, extends, delivers MP4."
---

# Madame Grimelda: Witch Selfie Vlog → generated via Nexabot API

The user gives only a TOPIC (e.g. "tukar tayar", "traffic jam", "harga minyak naik"). Claude turns it into a Madame Grimelda selfie-vlog prompt, then GENERATES the video through the Nexabot reseller API and sends the user the finished 9:16 MP4.

Madame Grimelda is an old-world forest witch who films her chaotic life on a front-facing phone camera as if it were normal modern content, speaking gleeful, unhinged, theatrical ENGLISH. Sister series to Lady Seraphine (gossipy) and Queen Marigold (deadpan). Her energy is CHAOS: delighted by disasters, sudden cackles, sweet whisper to manic glee, solving every problem with a slightly wrong spell. Mischievous and silly, never cruel or frightening.

Do not ask creative questions. Pick the funniest angle yourself and go. The only thing you may need to ask for is the API key (section 6).

## 0. Hard rules

- ALL of Grimelda's dialogue is in English. No Malay words in her lines.
- She is an ORIGINAL character. Never link her to any existing book, film, game or franchise witch or wizard, no franchise terms, no "in the style of", no resemblance to any actor or existing character.
- No real person's name. Invent names ("Bartholomew the toad", "the baker from the next village").
- No brand, product, car-maker, app, shop, show, film or character names.
- No gore, harm to people or animals, or real horror; spells backfire comically.
- The whole prompt is in English. CHARACTER, PERSONA and PHONE STYLE blocks are copied VERBATIM into every prompt.
- Never print, save to memory, or put the API key in any file sent to the user.

## 1. Locked blocks (copy verbatim)

```
CHARACTER (Madame Grimelda): woman in her late 50s with a round rosy face, deep laugh lines, bright pale-green eyes, a small mole on the left cheek, crooked friendly grin with one gold tooth. Long silver-white hair in two thick messy braids threaded with dried flowers, small twigs and tiny brass bells. Wide-brimmed, slightly bent moss-green felt hat with a patched crown and a single pheasant feather. Layered earthy outfit: a mustard-yellow knitted shawl over a rust-orange patchwork dress with many pockets, a leather belt hung with small glass vials, a wooden spoon and a bundle of herbs. Mismatched rings on every finger, fingerless striped gloves, faint soot smudge on her nose. Maintain identical face, braids, hat, shawl, dress, belt and rings throughout.

PERSONA & DELIVERY: gleefully unhinged forest witch who vlogs her chaotic day as if it were completely normal modern content. She speaks English with a warm, raspy, sing-song rural English accent, fast and bouncy, dropping into a sweet hushed whisper and then exploding into a cackle. She is delighted by disasters and treats every problem as an excuse for a spell that goes slightly wrong. She looks into the lens like an excitable aunt showing off. Signature expressions: wide delighted eyes, sudden head-tilted cackle, sweet innocent smile right after something explodes, one eye squinted in suspicion, too-close lean-in with a conspiratorial whisper. Signature gestures: wiggling her ringed fingers at something to cast a spell, blowing a puff of glitter off her palm, tapping the side of her nose, uncorking a vial with her teeth, patting her broom like a pet.

PHONE STYLE: front-facing selfie, phone held at arm's length slightly below eye level and tilted up, her striped-gloved hand and shawl visible at the bottom-right edge of the frame. Framing chest-up with the hat brim often cropped at the top. Energetic handheld shake, quick whip reframes when something behind her catches fire or pops, frequent too-close lean-ins where her grin fills the frame, phone-camera wide lens, sharp face, mild background distortion.
```

Optional staging swaps (face, braids and hat stay identical): patched dark-green travelling cloak outdoors; riding a broom a hand's width off the ground (selfie still); pet toad Bartholomew on her shoulder or hat brim; a sulking broom in the background.

## 2. Her voice: gleeful chaos English

Short excited bursts, "Oh!", "Ooh!", "Lovely!", contractions welcome. Every video needs one sweet-whisper secret, one cackle, and exactly ONE modern slang phrase delivered with total sincerity as the punchline.

Running bits (pick 1–2, rotate): opener "Hello, my little toadstools!"; "Don't worry. I have a spell for that." right before it goes wrong; Bartholomew the toad as silent judgmental co-host ("Bartholomew disagrees."); the broom is sulking; everything ends up slightly green; "Totally intended." after any disaster; sign-off "Subscribe, or I'll know. Ehehehe."

Slang slip (pick one): "slay", "it's giving cursed", "no thoughts, just vibes", "this is my villain era", "understood the assignment", "core memory unlocked", "we stan", "chaotic good".

Dialogue rules: one line per beat, at most ~10 words. Write the delivery cue each time, e.g. `She says gleefully in a raspy sing-song rural English accent:`, secret `She leans close to the lens and whispers sweetly:`, cackle `She throws her head back and cackles, then says:`, slip `She adds, totally sincere, in modern slang:`.

## 3. Creative engine

1. Translate the modern topic into her world: car → broom or pumpkin cart pulled by a goat; fuel price → price of moon-dew at the village market; traffic jam → queue of sheep on a forest path; mechanic → grumpy gnome blacksmith; GPS → a lying crow; speeding ticket → scroll from the village elders; car wash → dunking the broom in the cauldron. Invent fresh ones.
2. Vlog format said with glee: day in my life, tutorial, ranking, review, storytime, potion haul, what's in my cauldron.
3. One escalation: the spell backfires comically (green smoke, cart shrinks, goat glows, broom flies off). Sweet innocent smile, then cackle.
4. End with verdict + slang slip + sign-off + cackle; she lowers the phone and the recording cuts off.

Locations (pick 1–2): thatched cottage kitchen with hanging herbs and bubbling cauldron; misty mossy forest path with giant mushrooms; muddy village market; overgrown pumpkin garden; foggy lily-pad pond at dusk; candle-lit attic of dusty spell books; broom ride low over a heather field.

## 4. What the Nexabot API can and cannot do (read before writing the prompt)

Verified from https://nexabot.id/api-docs (Oct 2026):

- Base `https://nexabot.id`. Auth header `x-api-key: nxb_...` (or `Authorization: Bearer nxb_...`).
- `POST /api/v1/api` body: `mode`, `prompt`, `ratio` (1 = 16:9, **2 = 9:16**), `resolution` (720 or 1080, default 720), `media` (array of base64 data URIs). Returns HTTP 202 with `job_id`, `status`, `credit_cost`, `credit_balance`, `est_seconds`.
- Modes: `t2v` text→video (~60s), `sfv` start frame→video, 1 image (~90s), `i2v` ingredients→video, 1–3 reference images (~150s), `r2v` reference video (~380s), `extend` continue a video, 1 mp4 in `media[0]`, prompt optional, always 1080p (~300s). Also `img`, `music`, `tts`.
- `GET /api/v1/jobs/{id}` → `job.status` queued | processing | done | failed, `job.error`. `GET /api/v1/jobs/{id}/download` → mp4. `GET /api/v1/api/credit` → balance (free).
- Cost 0.4 credit per video request, 0.15 credit untuk request lain (refunded on failure); free on an active API Unlimited plan. No rate limit on the API.
- Errors: 401 bad key, 400 bad body, 402 not enough credit, 403 not your job, 404 no job.
- **There is NO duration parameter and the model is not named.** The mode names (ingredients, start frame, extend) suggest an ~8-second clip engine, not Seedance's 15s. So the video is built as a base clip + one extend, and timestamps in the prompt are ~8s per clip. After the first real run, check the true length with ffprobe and adjust the beats if it differs.
- No separate negative-prompt field: put an `Avoid:` line at the end of the prompt text.

## 5. Prompt structure: base clip + extend (≈15s total, 9:16)

Write TWO prompts.

**Prompt A — base clip (mode `t2v`, or `i2v` if a reference image of Grimelda exists):**

```
8-second realistic selfie-vlog comedy video, vertical 9:16, set in [location], where [premise in one sentence: Madame Grimelda does X like a modern vlogger, narrated in gleeful, chaotic English].

STYLE: photorealistic, shot on a front phone camera, [lighting], authentic rustic old-world cottage details, whimsical practical-looking magic effects (soft smoke puffs, sparkles, gentle glow), never horror. Handheld shake, natural reframing, slight wide-lens distortion, focus stays on her face. Natural weight in head turns, swinging braids and tiny bells, flapping shawl[, plus physics for any spell, broom, animal or object]. No cinematic glamour, no stabilization, no text overlay.

[CHARACTER block verbatim]

[PERSONA & DELIVERY block verbatim]

[PHONE STYLE block verbatim]

0–3s — HOOK
[Selfie action + signature expression]. She says gleefully in a raspy sing-song rural English accent: "[hook line]"
Sound: [concrete SFX].

3–6s — [BEAT TITLE]
[One action]. She says gleefully: "[line]"
Sound: [...].

6–8s — [SHE CASTS THE SPELL]
[Spell gesture, first sparkle, cut just before the result]. She leans close to the lens and whispers sweetly: "[secret line]"
Sound: [...].

Avoid: blurry, distorted face, deformed hands or fingers, extra limbs, duplicated characters, changing hair, hat or outfit, gore, horror, phone visible in frame, background warping, text, subtitles, logos, brand names, watermark, cartoon acting.
```

**Prompt B — extend (mode `extend`, media = clip A):**

```
Continue the same selfie vlog seamlessly from the last frame: same woman, same face, braids, moss-green hat, mustard shawl, rust dress, rings, same location and lighting, same handheld front-camera framing. She keeps speaking English in the same raspy sing-song rural English accent.

0–4s — [SPELL GOES WRONG]
[Comic backfire + sweet innocent smile]. She says: "[reaction line]"
Sound: [...].

4–7s — [VERDICT]
[Head-tilted cackle, lean-in, she lowers the phone and the recording cuts off]. She says: "[verdict]" then adds, totally sincere, in modern slang: "[slang slip]"
Sound: [SFX + short plucky fiddle or tin-whistle sting].

Avoid: [same Avoid line].
```

Rules: one action and one expression per beat; camera always her selfie; every beat has a concrete `Sound:` line; at least one spell gesture and one cackle across A+B; one slang slip total. For a longer reel, chain more `extend` calls (each on the latest output), sign-off only in the last.

## 6. Generate (run it, don't just describe it)

1. **API key.** If the user hasn't given one in this session, ask for it in one line (he makes it at nexabot.id/api-keys). Save it to `~/.nexabot_key` with `chmod 600`. Never echo it back.
2. **Write the helper** `nexabot.py` in the working directory (scripts dir, not a download dir):

```python
#!/usr/bin/env python3
"""Nexabot helper. Key from env NEXABOT_API_KEY or ~/.nexabot_key.
  nexabot.py credit
  nexabot.py run --mode t2v --prompt-file a.txt --out a.mp4 [--ratio 2] [--resolution 1080] [--media f ...]
"""
import argparse, base64, json, mimetypes, os, sys, time, urllib.request, urllib.error
BASE = "https://nexabot.id"

def key():
    k = os.environ.get("NEXABOT_API_KEY", "").strip()
    p = os.path.expanduser("~/.nexabot_key")
    if not k and os.path.exists(p): k = open(p).read().strip()
    if not k: sys.exit("ERROR: no API key")
    return k

def req(method, path, body=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"x-api-key": key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=600) as resp:
            b = resp.read()
            return b if raw else json.loads(b)
    except urllib.error.HTTPError as e:
        msg = {401:"API key tidak sah",400:"mode/body tidak sah",402:"kredit tak cukup",
               403:"bukan pemilik job",404:"job tak jumpa"}.get(e.code, "")
        sys.exit(f"HTTP {e.code} {msg}: {e.read()[:500].decode(errors='ignore')}")

def data_uri(p):
    mt = mimetypes.guess_type(p)[0] or ("video/mp4" if p.endswith(".mp4") else "image/jpeg")
    return f"data:{mt};base64," + base64.b64encode(open(p, "rb").read()).decode()

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("credit")
    r = sp.add_parser("run")
    r.add_argument("--mode", required=True, choices=["t2v","sfv","i2v","r2v","extend"])
    r.add_argument("--prompt-file"); r.add_argument("--out", required=True)
    r.add_argument("--ratio", type=int, default=2); r.add_argument("--resolution", type=int, default=1080)
    r.add_argument("--media", nargs="*", default=[]); r.add_argument("--timeout", type=int, default=1500)
    a = ap.parse_args()
    if a.cmd == "credit":
        print(json.dumps(req("GET", "/api/v1/api/credit"), indent=2)); return
    body = {"mode": a.mode, "ratio": a.ratio}
    if a.mode != "extend": body["resolution"] = a.resolution
    if a.prompt_file: body["prompt"] = open(a.prompt_file, encoding="utf-8").read().strip()
    if a.media: body["media"] = [data_uri(p) for p in a.media]
    sub = req("POST", "/api/v1/api", body)
    jid = sub["job_id"]
    print(f"submitted {jid} cost={sub.get('credit_cost')} balance={sub.get('credit_balance')} est={sub.get('est_seconds')}s", flush=True)
    t0 = time.time(); last = None
    while True:
        job = req("GET", f"/api/v1/jobs/{jid}")["job"]
        if job["status"] != last: print(f"[{int(time.time()-t0)}s] {job['status']}", flush=True); last = job["status"]
        if job["status"] == "done": break
        if job["status"] == "failed": sys.exit(f"FAILED: {job.get('error')}")
        if time.time() - t0 > a.timeout: sys.exit(f"TIMEOUT, job {jid} still {job['status']}")
        time.sleep(5)
    open(a.out, "wb").write(req("GET", f"/api/v1/jobs/{jid}/download", raw=True))
    print(f"saved {a.out} ({os.path.getsize(a.out)} bytes)")

if __name__ == "__main__": main()
```

3. `python3 nexabot.py credit` — confirm the key works and there is at least 0.30 credit (or `unlimited`). On 401 ask for a new key; on low credit tell the user and stop.
4. Save Prompt A to `a.txt`, run `python3 nexabot.py run --mode t2v --prompt-file a.txt --out grimelda_A.mp4` (use `--mode i2v --media ref.jpg` if the user supplied a Grimelda reference image; `sfv` if he wants that image as the exact first frame). Run in the foreground with a long timeout (up to 10 min).
5. `ffprobe` clip A for duration and audio. Save Prompt B to `b.txt`, run `python3 nexabot.py run --mode extend --prompt-file b.txt --media grimelda_A.mp4 --out grimelda_B.mp4`.
6. ffprobe clip B. If B is longer than A (it already contains A), B is the final. If B is only the new part, join: `ffmpeg -i grimelda_A.mp4 -i grimelda_B.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1" -c:v libx264 -preset veryfast -crf 18 -c:a aac grimelda_final.mp4` (if a clip has no audio, concat video only). Grab a mid-frame with ffmpeg and look at it to check face, outfit and 9:16.
7. Send the final MP4 with SendUserFile (and clip A as backup). On `failed`, report `job.error`, soften anything that might have tripped a filter, and retry once; never resubmit the same failed prompt more than once.

## 7. Reply format

Informal Bahasa Melayu (rojak), short; prompt and dialogue stay English:
1. One line: angle picked + settings (9:16, 1080p, base + extend).
2. Both prompts in code blocks (A and B), so the user can rerun them on the web if needed.
3. The MP4 file, with one line: duration, credit used, balance left.
4. Optional: one line with an alternative angle.

Before submitting, scan for brand, franchise, existing character or real-person names and remove them, and check none of her lines contain Malay.