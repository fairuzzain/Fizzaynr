# Models, settings and costs

The settings this skill uses for each model, what they cost, and what was measured about them. How to call a tool is in the tool's
own description: build every call from it. The models' defaults are not these settings, so every call carries every value given
here, one take a request (`SKILL.md`, Sending).

## Before the first paid call

Read `seedance_2_5` with `models_explore` (`action: "get"`). Stop and tell the user the film cannot be made right now if either is true:

- its `mode` options lack `omni_reference` or `video_extension`;
- it lacks the film's resolution.

Its `resolution` options confirm the one the user picked at intake (`SKILL.md`, step 0, the one intake question); a pick it
no longer lists is offered again from those it lists.

## Costs

For 3D and 2D, use `generate_image` with `params.get_cost: true` for each distinct
Flare configuration, including its quality, resolution, aspect and reference inputs.
Use the returned credit amounts for the master and remaining references in the plan and approval.
When an input is still pending, identify the unpriced stage in the plan and get its quote before spending. Add the stages for the total:

| Item                                                                                 | Credits                                      |
| ------------------------------------------------------------------------------------ | -------------------------------------------- |
| Live action: each sheet and location sheet (`seedream_v5_pro`)                       | 2.5                                          |
| 3D and 2D: the style master (`gpt_image_2_6_flare`, high)                            | Current one-image quote                      |
| 3D and 2D: every other image (`gpt_image_2_6_flare`, medium)                         | Current one-image quote                      |
| A clip at 480p / 720p / 1080p, per second; an extension's source is not billed again | 3 / 7 / 16                                   |
| A narration track or a song                                                          | 0.4-3, by length                             |
| The score or a song (`elevenlabs_music_v2`), per second of every take                | about 0.07 (32 seconds: 2.14; 45 seconds: 3) |

## Reference images

An earlier image is attached as its job id, an upload or an imported picture as its media id, each in `medias[]` as
`{ value, role }` with the role the model's listing gives (`image_references` for every image model here). A link is never
attached: import it with `media_import_url` first and attach the media id it returns.

**3D and 2D: `gpt_image_2_6_flare`**, `resolution: "2k"`, `quality` as below.

| Image                             | Quality | Shape                                                                                  | Attached                                       |
| --------------------------------- | ------- | -------------------------------------------------------------------------------------- | ---------------------------------------------- |
| The master                        | high    | 16:9                                                                                   | nothing                                        |
| Every other image                 | medium  | sheets, prop sheets and two-panel location sheets 16:9; plates the film's aspect ratio | the master, then any uploaded photo            |
| An edit of a frame or a composite | medium  | as the image it replaces                                                               | the frame or composite, in place of the master |

Check the generated sheets against the approved master for identity and style.

**Live action: `seedream_v5_pro`.** `aspect_ratio: "16:9"`, `resolution: "2k"`.

| Image                               | Attached                        | Extra setting      |
| ----------------------------------- | ------------------------------- | ------------------ |
| A sheet with an uploaded face photo | the photo                       | none               |
| A double's sheet                    | the sheet it shares a face with | none               |
| An edit of a frame or a composite   | the frame or composite          | `is_inpaint: true` |

## Clips: `seedance_2_5`

**A fresh clip:**

- `mode: "omni_reference"`, `generate_audio: true`;
- the film's `resolution` and `aspect_ratio`;
- the clip's exact length as `duration` (whole seconds, 4-30).

Its references go in `medias[]` in this order: its `images` (role `image_references`), its `videos` (`video_references`), then
its audio (`audio_references`) (`clips.md`, References and their limits).

A voice sample bound in the prompt is used as the character's voice for the new line, and the sample's own words are not replayed
(tested: a 4.4-second sample, a new line spoken in the same register).

The receipt does not show the settings a job took, and a value a call leaves out takes the model's own: twelve clips of one
film came back landscape, seven of them billed at 720p. So every value goes into every call, and every take is measured against
them (`SKILL.md`, Checking a result).

**An extension:**

- `mode: "video_extension"`, `extension_mode` `forward` or `backward` as the clip's `direction` says;
- the source first, then the sheets (accepted, tested), then the voice samples;
- the aspect ratio follows the source.

When the references are refused, send the source alone, take the `@Image` and `@Audio` mentions out of the prompt, and keep the
sheets for the next fresh clip.

## Voices, songs and the score

**A narration track or an a-cappella song: `seed_audio`** (`generate_audio_batch`). This concerns only an off-screen narrator; the characters' own voices are
made in the clips and carried by voice samples (`clips.md`, Voices).

- **The same voice on every call.** Each call sends `voice_type` (`preset` for a catalogue voice, `element` for one the user
  saved) and `voice_id`, the same on every call. Without them the provider picks a voice per request, and every take comes back in a different
  timbre (the narration workflow measured six voices in one video).
- **Choosing the voice.** `list_voices` lists them.
  - The user picks the narrator from that list. This is the one question a narrated film asks.
  - When the user named a voice, take it from that list; when nobody can answer, a preset voice whose gender fits.
  - Tell the user about a name the catalogue lacks, and never replace it silently.
- **Speed.** `speech_rate` 30 speeds a narration up, but one preset at 30 read 140-197 words a minute from film to film
  and one request 146 and 237 in two takes: measure every take (`formats.md`).
- **A song.** Put the singing direction in brackets, where it is not sung, then the lyrics: "(singing a slow folk melody, long held
  notes on every line, slow tempo) <lyrics>".

**A song with a band: `elevenlabs_music_v2`** (`generate_audio_batch`), a sung story without lip-synced lines (`formats.md`, Sung story).

- Each part: the song prompt, word for word in every part; its `lyrics`, one sung line a line; its `duration`, at most 120
  seconds with lyrics.
- All parts go in one batch call; a take comes back in seconds.

**The score: `elevenlabs_music_v2`** (`generate_audio_batch`, `force_instrumental: true`).

- Write the prompt into `score-prompt.txt`; the call sends it word for word.
- Instrumental, its `duration` the film's length plus 5 seconds: a take opens on up to a second of silence and its
  last seconds ring out quietly (tested: 32 seconds asked, music from 0.74 to 29.3 s; a 123-second take ended its music 4.3
  seconds early, where every 125-second take covered a 120-second film).
- The prompt: "Instrumental film score, no lyrics.", then the film's world and mood, the key and tempo, the instruments, and how
  it ends. Describe the sound, never name a composer, artist, film or series: a name fails the job (a drama-editor test).
- Measure the take before it goes under the film: some come back far longer than asked (a drama-editor test), and it
  plays 9-10 LU quieter than a sung track (tested: -23.5 against -14.5 and -13.0 LUFS), so its level is set by measure (`clips.md`,
  Assembly).

## The sandbox

- **Where to work:** `sandbox_exec`, in the film's folder under `/home/user` (`SKILL.md`, RUNTIME CONTRACT and GOLDEN RULES, Files), never under `/tmp`: only
  `/home/user` is kept while the sandbox pauses.
- **What is installed:** `ffmpeg`, `ffprobe`, `python3` and `faster-whisper`. Load it with
  `WhisperModel("small", device="cpu", compute_type="int8")`; a fresh sandbox downloads the model on first use (about 40
  seconds), so the first whisper call runs with `background: true`.
- **Demucs, where the sandbox has it** (`python3 "${HF_WORKFLOWS}/drama-ads/scripts/stems.py" check`): when the check
  says it is missing, music a clip was told to leave out is fixed by remaking that clip. Never pip install it.
  `scripts/stems.py` splits a clip's sound into vocals, drums, bass and other, measures its music against its lines, and takes
  the music out (`clips.md`, Order of work, Music).

## When a sheet is refused

`ip_detected` means moderation thinks something looks like protected IP or a real person, often a sheet that resembles a celebrity.
It is often chance: submit the same call once more unchanged (it is not billed; a refused clip passed 3 of 3 times resent, and four
more refusals in tests passed on the first resend). Refused again: remake that sheet with a more distinctive face, or remove the
brand or character the script names (never the user's own product).

## When a clip is refused

`nsfw` on a clip means moderation refused what it shows. Never send the same scene again in other words to get it past: stage
the beat again without what was refused, so the film still shows what its lines say (`formats.md`, Sung story). One film
covered a refused beat with a product insert, and its song promised a scene nobody saw.
