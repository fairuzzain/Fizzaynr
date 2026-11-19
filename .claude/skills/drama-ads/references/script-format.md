# Script format: one film of any length, built from clips

This file sets the format: where it differs from the other screenwriting files, it wins. Everything else in them applies. It
describes mechanics only; everything a beat contains comes from the writing rules (`story-rules.md`) and the user's idea.

- Read what `SKILL.md` names for each step.
- `characters.md` governs `cast[]`; `styles.md` the `style` line; `clips.md` the clips.

## Length and skeleton

The length is the user's: any length they name; when they name none, the length the story needs. The shape is vertical 9:16
unless the user asks for another: horizontal 16:9, square 1:1, or 4:3, 3:4, 21:9 (the clip model's shapes). The resolution is the one
the user picks from those the clip model lists, 1080p when they pick none (`SKILL.md`, step 0, the one intake question), for every style alike.

The skeleton is the same at every length; its beats fall at these shares of the running time (the 60-second times in brackets),
unless a reference video sets its own (`SKILL.md`, A reference video):

```
0%    HOOK      visual conflict, readable without context                                   [:00]
~13%  FRICTION  who vs who, where; the micro-vulnerability lands here                      [:08]
~27%  JOLT 1    pressure rises                                                              [:16]
~43%  JOLT 2    point of no return                                                          [:26]
~67%  SPIKE     re-evaluation, triggered by the protagonist's deliberate action             [:40]
~83%  ENDING    the final beat; the last spoken line starts at least 5 s before the end    [:50]
      (DWELL)   only when the story needs it: reaction on faces, in motion, at most 3 seconds, between SPIKE and ENDING
```

- A film longer than about 90 seconds runs in acts of 60-90 seconds. Each act has its own FRICTION, JOLTS and SPIKE; the last act's
  spike is the climax, and the ENDING follows it (with a DWELL before it only when the story needs one). Pressure rises every 10-15
  seconds throughout. How beat headings carry the act: Screenplay layout.
- A film of 45 seconds or less: JOLT 1 and JOLT 2 may be one jolt, and the last spoken line comes before the ENDING beat, which is
  action. At 30 seconds the skeleton's every element in one breath gave a dozen shots of under a second each.
- The ENDING lands the film's central question on a strong last image (the hook paid off, the twist paid off, the opening image
  reversed). An open or cliffhanger ending only when the user's idea asks for one.
- Cast: 2-3 central characters, plus groups of extras; a film longer than 60 seconds may add supporting characters, at most 6 in all
  (a body diary may have its one figure: `formats.md`).
- Locations: a film of up to 60 seconds is one continuous scene in one location, with no time jumps, unless the user's idea needs a
  later time (the next morning, a year on): then it keeps the idea with one forward jump at a clip boundary in the same location,
  the later light a relit frame plate of the earliest clip in that place (`clips.md`, Frame plates). Planners without this line dropped a premise's
  "next morning" (3 of 3); with it they kept it (3 of 3). A longer film may use up to 4
  locations (up to 120 seconds) or 5 (longer); a new location or a forward time jump happens only at a clip boundary. Never a flashback.
  Storytime and song (`formats.md`) change this: one jump back after the opening, named jumps forward, up to four places at any
  length; the body diary passes days inside clips.
- Dialogue: at least 70 words a minute of talk time (each clip less its 4-second line tail, the film less the hook's 1.5 seconds:
  50 in a 60-second film of four clips) and at most 110 a minute of the film; counted on the whole film, 0 of 15 scripts could hold
  every other rule and pushed lines off their speaker's shot. At most about 2.5 words per second inside any beat. Narration (160-175 words a
  minute) and sung lines (60-100, or 85-110 for an `elevenlabs_music_v2` song) follow their own rates instead (`formats.md`). A pace
  the user asks for (`asked.wordsPerMinute`) replaces the dialogue and narration rates.
- The hook's action lands before the first line: no `dialogue` or `thought` line starts before 1.5 seconds.
- Every spoken line (`dialogue` or `thought`) is at most 10 words, with no exceptions. A longer
  speech is split into two lines with a visible action between them. Narration and sung lines: `formats.md`.
- A `dialogue` or `thought` line belongs to one clip and ends at least 4 seconds before that clip ends (the model delivers lines up to
  1.5 seconds late).
- Clips: the film is a chain of clips of 4-30 seconds each, one generation each, joined with hard cuts. `clips.md` says how they are
  cut and made; the plan goes in `clips`.

## script.json

Write `script.json` as exactly one JSON object:

```json
{
  "title": "string",
  "logline": "one sentence",
  "template": "the id of the film's style template in styles.md",
  "format": "dialogue|storytime|song|talking-object|inside-body (formats.md)",
  "style": "that template's style line",
  "durationSeconds": 60,
  "aspectRatio": "9:16",
  "resolution": "1080p",
  "screenplay": "the film in the Screenplay layout below",
  "locations": [
    {
      "id": "l1",
      "description": "what the place looks like, era and kind of place",
      "light": "the scene's light in one line",
      "anchor": "the one fixed, unmistakable object every clip in this place places the characters against",
      "plates": [
        "2D only: the direction each background plate faces: toward <a landmark of the place>",
        "…"
      ]
    }
  ],
  "cast": [
    {
      "id": "c1",
      "kind": "human",
      "name": "string",
      "age": 25,
      "gender": "woman|man",
      "role": "protagonist|antagonist|ally|...",
      "appearance": "ethnicity and skin tone (always, per characters.md), eyes, hair, build, marks — plain visible words",
      "wardrobe": "the outfit worn through the film, garments, colours, materials, footwear (another outfit is a form)",
      "voice": "how they sound: timbre and register, no pace words",
      "faceImage": null
    },
    {
      "id": "c2",
      "kind": "other",
      "name": "string",
      "form": "what it is, in a few plain words",
      "role": "...",
      "appearance": "shape, size against the others, material and texture, colours, the face it has or has not, how it moves",
      "wardrobe": "only what it wears or carries, if anything",
      "voice": "how it sounds",
      "faceImage": null
    }
  ],
  "groups": [
    {
      "id": "g1",
      "name": "string",
      "kind": "group|crowd",
      "size": 8,
      "description": "what they look like ON SCREEN in plain literal words: their visible form, how many, ages, clothes"
    }
  ],
  "props": [
    {
      "id": "p1",
      "name": "string",
      "description": "what it looks like",
      "holder": "c2 or null",
      "sheetFrom": null
    }
  ],
  "clips": [
    {
      "id": "k1",
      "start": 0,
      "end": 15,
      "location": "l1",
      "make": "fresh",
      "images": ["l1", "c1", "c2"],
      "videos": [],
      "voices": [],
      "positions": "where each character stands at the first frame, relative to the location's anchor",
      "stateIn": "what is true at the first frame",
      "stateOut": "what is true at the last frame"
    },
    {
      "id": "k2",
      "start": 15,
      "end": 30,
      "location": "l1",
      "make": "extend",
      "source": { "clip": "k1", "from": 10, "to": 15 },
      "direction": "forward",
      "images": ["l1", "c1", "c2"],
      "videos": [],
      "voices": [],
      "positions": "...",
      "stateIn": "...",
      "stateOut": "..."
    }
  ],
  "narrator": {
    "voice": "narrated formats only: how the narration sounds",
    "voiceId": "the seed_audio preset",
    "speechRate": 30,
    "trackSeconds": 27.5
  },
  "lines": [
    {
      "clip": "k1",
      "speaker": "c1",
      "to": "c2",
      "startSeconds": 3.5,
      "delivery": "how the line is said",
      "text": "exact spoken words",
      "kind": "dialogue|thought|narration|sung"
    }
  ]
}
```

- `template`, `style`: `styles.md`; `format`: `formats.md`.
- `aspectRatio`: 9:16, 16:9, 1:1, 4:3, 3:4 or 21:9; every clip and every 2D plate takes it. `resolution`: 480p, 720p or 1080p; it
  decides how deep a clip may go (`clips.md`, Generations) and the clips' cost (`models.md`).
- `locations[].plates`: only in a 2D template, one entry per background plate (`style-master.md`), in the order the clips send them.
  A clip's `images` names the location (all its plates) or one plate by its position (`l1#2`, the second plate), which is how a
  frame plate replaces one plate and keeps the other: `["frame:k1@0.0", "l1#2", …]`.
  One place at two times of day is two locations in 2D: a plate keeps its light. When the second is made as a relit frame plate of the
  first (`clips.md`), it has no `plates` entry.
- `narrator`: only in a narrated format (`formats.md`): the narration's voice, the chosen preset, the `speechRate` the track is made
  at and, once it is made and fitted, `trackSeconds`: the film's second at which the fitted track's last word ends.
- `asked` (only when the user asked for a setting this skill would otherwise decide: `SKILL.md`, The user's own material):
  - `from`: where it comes from, their words quoted or what their reference measured;
  - `wordsPerMinute`: the pace of the film's voice, its narration, or its dialogue when it has no narration. `checks.py script` holds
    those words within 15% of it, never above their kind's top rate; sung lines keep the song model's rate;
  - `texts`: the text they want to see on screen, each `{"text", "start", "end", "over"}`: its exact words, its film seconds, and
    `picture` (over the shot) or `black` (on black in place of the picture). It is laid over the film at assembly, never drawn by
    a clip (`clips.md`, Text on screen); the screenplay carries no card for it.
- `locations[].description`: every location's description names its era and the kind of place the script sets it in, from its
  headings and notes ("<a period> <kind of place>", with the parts that tell the period), so its image never drifts to another
  period. A style with a world of its own names that world's kind of
  place the same way.
- `locations[].description`, how to lay it out: the anchor at the far end (the location sheet's master view faces it); every fixture
  the action uses facing the room, where one of the two cameras sees it (never its back or its inside); what lies beyond a door the
  action opens; and a place seen from inside it (through a window, from a height) as part of this location, its landmark
  named. Fixtures stay in the location even when the ending turns on them; only movable objects are `props`.
- `cast[].kind`: `human` or `other` (anything else that acts: an animal, a creature, a robot, an object, food). A `human` has `age` (a
  number, 18 or above) and `gender`; an `other` has `form`, and `age` or `gender` only if the story gives them.
- No child or baby is ever on screen: the no-children rule is in `characters.md` (Every character).
- `cast[].role`: `<function> — <what they are to the others>`.
- `faceImage`: when the input lists face images, set it to that image's index for the character it belongs to; otherwise null.
- `voiceFrom` (optional): the clip whose checked take made this character's voice, when it is not the first of their clips (`clips.md`,
  Voices).
- `wordsPerSecond` (optional, once their voice clip is checked): the words of their lines in it over those lines' seconds, first
  word's start to last word's end; `checks.py` times a line's end at 2.5 words a second, or at this when it is slower.
- `clips[].generated` (with `kept`): the generation's own length in seconds (`clips.md`, The clip entry).
- `clips[].shots` (once a take is looked at): its shots as they came out, `[{"from": 9.42, "to": 12.13, "framing": "close-up on <name>,
  the view of @Image2"}, …]`, in the take's own seconds (its cuts found as `clips.md`, Order of work, Stubs, says), each framing written as a beat's is: the shot size, on whom, and the view of `@Image<n>` in this clip's own tags (a frame plate taken from a shot written without its view is read as a view of its own at the seams). `checks.py clip` reads them in
  place of the clip's prompt at its seams: a take that kept one view where its last beat asked for the opposite one passed a seam that
  turned a character 180 degrees, and a take that ended on a close-up was read as ending on its prompt's wide. `checks.py
  script` also reads them through `kept`: a shot the film shows under 1.5 seconds is refused (three films' takes came out so, one
  ending's last shot 1.46 s), and the last clip's ending is counted from its shots after the last line's measured end, a shot that starts up to 0.3 seconds before that end counted from it on (whisper put one last word's end 0.17 seconds past the cut it was voiced before), with each line timed as measured carrying `endSeconds`, its last word's end; such a line has no line tail (`clips.md`, The clip entry). A `part` carries none: its shots are in its `of` clip's entry.
- `groups`: every set of extras or background characters the film shows. Describe them by what the camera sees: anyone in disguise or in
  another form is described as the form on screen.
- `groups[].kind`: `crowd` is a large background that only reacts; `group` a small unit that acts. A group has no sheet and never
  goes in a clip's `images`: the clip prompt writes it (`clips.md`, A crowd), and a member the story singles out is a cast member.
- `props[].sheetFrom`: the clip whose frames the prop's sheet was made from (`clips.md`, References from the film's own frames), or
  `null` for a sheet made before the clips.
- `forms`: a character or prop after it changes on screen, and a character in another outfit (`characters.md`), one entry each, `{ "id": "c1b", "of": "c1", "change": "<what changed, in
  plain visible words>", "sheetFrom": "k2" }`; a clip sends the form's id in `images` in place of the one it changed from.
- `props`: the objects the story turns on (passed, taken, used in the spike or the ending), at most 3 per location. Each gets an
  `[INSERT: …]` close-up at the moment it matters; its `description` ends with its state at the end of the film, and `holder` is who
  has it at the start. The CENTRAL OBJECT (`story-rules.md`), when the story has one, is one of them. An object a character holds or
  wears in more than one clip is a prop too, without the insert: written in words alone, one film's character held three different
  versions of one prop and another prop turned into another of its kind, and a prop sent without its sheet came back another
  shape (tested).
- `clips`: in film order, covering the whole film from 0 to `durationSeconds` with no gap or overlap; every field and rule is in
  `clips.md`.
- `lines` are in time order; `startSeconds` is from the start of the film. A `sung` or `narration` line also carries `endSeconds`, its last word's
  end, once the song or the track is made (`formats.md`, Sung story). `kind`: `dialogue` (spoken on screen), `thought` (the
  inner voice, VOICE OVER INTELLIGENCE), `narration` and `sung` (the narrated formats, `formats.md`; `clip` is the clip the line
  starts in, `to` is `null`).

## Links between fields

- **One id system.** Cast `c1`, `c2`…, groups `g1`…, props `p1`…, locations `l1`…, clips `k1`…. The screenplay uses names; every JSON
  field uses ids: `lines[].speaker` is a cast id, `lines[].to` a cast id, a group id or `null` (a thought, or a line addressed to no
  one), `lines[].clip` a clip id, `props[].holder` a cast id or `null`, `clips[].location` a location id, `clips[].images` location
  ids, cast ids, prop ids (the films that make prop sheets: `style-master.md`) and frames, `clips[].voices` cast ids, and later every `effects.json`
  owner is a cast id.
- **Only cast members speak.** The check refuses a speaker that is not a cast id, so a group never has a line; anyone who speaks is a
  cast member. The one exception is the body diary's narrator, `"speaker": "narrator"` (`formats.md`).
- **The screenplay and `lines` are the same dialogue twice:** same words, same order, and each `startSeconds` agrees with the beat
  timestamps around it and lies inside its clip.
- **The screenplay and `locations` agree.** Every part of a place the action uses is named in that location's `description`, so its
  sheet contains it; its `anchor` is one of those parts.
- **The screenplay and `clips` agree.** Each clip marker in the screenplay is a clip in `clips`, with the same times and location.
- **Downstream files read this one.** `plan.json` takes its proof shots from the screenplay, the sheets are written from `cast[]`, the
  location prompts from `locations`, a 3D or 2D film's style master from the main location, its cast and `props`, the clip prompts
  from `clips` and the screenplay. A detail missing here is missing everywhere after.

## Screenplay layout

The beats and their shares of the running time come from Length and skeleton. The frame:

```
TITLE: <TITLE IN CAPS>
Runtime: ~<length> | Locations: <each place, in a few words> | Cast: <each name> (<role>) + <groups>

— CLIP k1 (0:00–0:15) — <location id> —

HOOK (0:00)
FRICTION (0:08)

— CLIP k2 (0:15–0:30) — <location id> —

JOLT 1 (0:16)
JOLT 2 (0:26)

— CLIP k3 (0:30–0:45) — <location id> —

SPIKE (0:40)

— CLIP k4 (0:45–1:00) — <location id> —

ENDING (0:50)
```

A film in acts puts the act before the beat: `ACT 2 — JOLT 1 (1:44)`. A beat can run across a clip marker.

Under each beat heading go stage directions and dialogue, in these forms:

```
<stage direction: its own paragraph, followed by a blank line>

<NAME>
<spoken line>

<NAME> (V.O.)
<thought line>

<NAME> (NARRATION)
<narration line>

[INSERT: <prop in close-up>.]
```

The check tells stage directions from dialogue by this layout, so keep it exactly:

- a beat heading is the beat name in CAPS (with its act, if any) plus the time it actually starts as `(M:SS)`;
- a clip marker gives its clip's `start` and `end` exactly, tenths included when the clip's are (`— CLIP k2 (0:18.4–0:31) — l1 —`);
- a speaker cue is the name in CAPS on its own line, the spoken line directly under it, then a blank line; a stage direction glued
  under a spoken line is read as dialogue and escapes the simile check;
- a `(V.O.)` cue is used only when VOICE OVER INTELLIGENCE (`story-rules.md`) calls for an inner-voice line, and that line is
  `"kind": "thought"` in `lines`;
- a `(NARRATION)` or `(SUNG)` cue only in a narrated format (`formats.md`), its line `"kind": "narration"` or `"sung"`;
- the last stage direction ends with `CUT TO BLACK.`

## Timing as the check computes it

- A `dialogue` or `thought` line ends at `startSeconds + words / 2.5`; it must end at least 4 seconds before its clip's `end`, except
  in a clip with `kept`, whose lines are timed as measured.
  Narration and sung lines are timed from their track and only have to start inside their clip.
- The film's words, per minute of `durationSeconds`, rounded: `dialogue` and `thought` 70-110 (at most 110 beside narration or
  singing); `narration` 160-175; `sung` 60-100, or 85-110 when `narrator.voiceId` is `elevenlabs_music_v2`. With
  `asked.wordsPerMinute`, the narration (or, without one, the dialogue) is within 15% of it and never above its own top rate.
- Line length: `dialogue` and `thought` at most 10 words, `sung` at most 11, `narration` at most 20.
- The last line starts at least 5 seconds before the end of the film.
- A workable density: a new line every three to five seconds while characters talk, with the screenplay's visible action filling the gaps.
