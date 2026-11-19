# Generating the film: clips, extensions, references

The film is a chain of clips joined with hard cuts. Every clip is one `seedance_2_5` generation of 4-30 seconds: either made fresh
from references (`omni_reference`) or made by extending another clip (`video_extension`). The model settings are in `models.md`; this file
is the logic. Its one goal besides the story: keep the picture from degrading. Every generation made from generated material copies
that material's errors and adds its own, so errors pile up the further a clip is from clean sources. The rules below cap that.

## Cutting the film into clips

- Pack complete beats into clips of 10-15 seconds: about four beats and six shots, a 30-second film in two clips. Open a new clip
  also when the location changes, time jumps, or the story wants a hard cut; a brief scene in another place may be shorter (from 4
  seconds). Every clip is a new roll of the dice for faces and
  clothes and every seam a place to break, so never shorter, except the after-state clip of a change of state, which runs as long
  as its shots need, from 4 seconds (a 6-second one was right from its first frame); but one 30-second clip of 12-16 shots (tested in nine films) squeezed
  the spike and the ending into shots under a second and dropped planned moments, and a broken beat in it cost a remake of the
  whole 90 credits.
- Each shot lasts at least 1.5 seconds, a shot with a physical action at least 2. The ending's action is its own shots (the move,
  then its irreversible result), at least 4 seconds in all, and the film cuts to black on the result: no held shot after it.
- The model cuts near the prompt's seconds, not on them: in the clips of ten films (220 written cuts in 64 takes of 5-16 seconds)
  half landed within 0.33 seconds and one in three 0.5-2.8 seconds off, late where a line was still being spoken at the written
  second (23 of 27), early in clips without speech; 95% of shots came out at most 0.8 seconds shorter than written, but a clip's last shot after a spoken line up to 1.8 seconds shorter, and in one later dialogue film 2.4 and 2.6 seconds shorter (2 of its 5 clips, both clips whose lines landed late). So a shot with a minimum length, or one that must still be on screen at
  a given second (the hook's two-shot through second 3, an action's 2 seconds), is written 0.8 seconds longer than that, and a
  clip's last shot after a line 1.8 seconds longer, or what it must show goes before the line; a moment that must land on an exact
  second (a flash on a sung word, a hit on a beat) opens its clip, whose first frame is exact. `checks.py clip` holds it: a timed
  beat under 2.3 seconds, an insert under 2.8 (inserts written shorter came out under 2 seconds 13 of 25 times, at 2.8 or more 1 of
  12), a plan item's beat under its held seconds plus 0.8, and in a dialogue film the last clip's beats from the screenplay's ENDING
  heading on, after the film's last line, under 5.8 seconds (4.8 when that line is in an earlier clip; a reaction the screenplay puts
  before ENDING does not count) are refused (written without the margin, four
  of six films of one round had shots under their minimum, two endings under 4 seconds).
- Two beats in a row on the same subject from the same view come back as one shot (4 of 9 such pairs lost their cut): change the side or the size, or write them as one shot. A beat's subject is whoever its framing is on ("<size> on <the character>, … looks at <the other>" is on <the character>): a shot and its reverse are two subjects. Changing the size keeps the cut most of the time (none of 32 lost it in four films),
  not always: in one body-diary clip, two runs, it came back as one camera move 4 of 4 times.
- A clip with one broken beat: keep its good parts (trim it, and write the kept seconds in its entry's `kept`, one range or, when the
  broken shot sits in the middle, the range before it in the clip's entry and the range after it in a `part` entry after the
  remake (The clip entry), each measured on the take
  with the whisper word times and the cuts, never from the prompt's timing: a remake started its line at frame 0, not at the 0.5
  seconds written, and the planned range would have cut its first word) and remake only the
  broken beats as a short clip of their own, made fresh or by extending the good part, within the generation limits: at least the
  seconds of its lines plus 4, and 4 seconds in all. It carries the voice samples of everyone who speaks in it and is not heard in its
  source part. Choose between two takes shot by shot this way too. A kept range starts after the last word of any line it leaves out,
  not at the cut: a range started at the cut carried the dropped take's last word over the next shot. When a remake's 4-second minimum changes the film's length, take the seconds back from the tails of the clips around it, after their last line. A `kept` trim that leaves the film a fraction of a second off a whole second keeps that length, written to a tenth in `durationSeconds` (the score is asked at that length plus 5): no second trim to round it.
- A trim point (a `kept` range, a cut to the planned length, the seconds taken back from a tail) lands on a cut of the clip or
  leaves at least 1.5 seconds of the shot it falls in: a shot cut shorter reads as a jump.
- At a hard cut the two clips differ in shot size, subject or angle. A cut inside one continuous moment opens the next clip on a close
  insert; a cut to a new place or time opens wide, so the viewer sees the room again (`checks.py clip` refuses a clip whose stateIn names a time jump, forward ("<n> <hours | days …> later", "the next <morning | day …>") or back ("<n> <hours | days …> earlier | before", "the <night | day …> before", a flashback), or in the body diary a new "day <n>" or "night <n>", and whose first beat is not wide or medium-wide; an after-state clip that opens on a close insert of the changed thing follows its own rule; a past event named in stateIn with those words is read as a jump too, so name it otherwise). `checks.py clip` reads the clip before's
  prompt and refuses a first beat on the same view and subject a size step or less from its last one (two of four films opened a
  clip so, a jump at the seam).
- The next clip opens on the aftermath of the previous clip's last beat. It never replays its last line, gesture or entrance.
- A clip that will be extended ends on a held shot, a few seconds of one steady framing (a clip extended backward starts on one): the
  extension continues that framing, and a cut there would make the seam visible.

## Generations: shallow, wide as needed

Each clip has a generation number:

- **0, an original:** made fresh from text and the reference images only (an audio reference does not count).
- **An extension:** its source's generation + 1.
- **Made fresh with a reference video:** 1. A reference video is always an original (generation 0).
- **Made fresh with a frame taken from a clip:** that clip's generation + 1.
- When a clip uses several of these, the highest wins.

How deep a clip may go depends on the film's `resolution`:

- **1080p:** at most generation 2.
- **720p and 480p:** at most generation 1. Below 1080p the picture degrades faster, so already at 720p a second extension is one too
  many. An extension of an extension, or a frame plate taken from an extension, is out.

In width there is no limit: one original can be the source or the reference of any number of clips. Trimming or cutting a clip does
not change its generation; only generating does.

## Extend or make fresh

- **Extend** when the clip continues the same place and the same characters without a cut, or to carry the exact layout of a place and the
  positions of things in it into another moment: cut the part of a clip that shows that layout (`source.from`-`source.to`) and extend
  that part. An extension continues from the end of its source part (`forward`) or leads into its start (`backward`); it can sit
  anywhere in the film's order.
- **Make fresh** when extending would pass the generation limit, after a hard cut, at a new location or after a time jump. Re-send the
  location sheet and the character sheets; write in the prompt where each character stands relative to the location's anchor and who
  is on which side of whom; in a place an earlier clip filmed, send its frame plate too (Planning the rounds).
  Two originals of one place made in parallel drift apart in layout (where the fixtures stand, which side things are on):
  when the second must match the first, make it after the first, with a frame of it.
- Frames are always sent as references, never as a start or end frame: a pinned first frame makes the seam shimmer instead of
  cutting cleanly, and a reference can drift into frame 0 if it is pinned.
- The sheets go with every clip, an extension included: they are the clean original of every face and outfit.

## References from the film's own frames

The reference images set the design before any clip; after that, a clip's place, its changed states and the props a clip drew first
are taken from the film's own frames. A fresh clip made from such references matched its source clip as closely as an extension did
(four tests in four looks), while separately drawn references drift (two plates of one place came out as two places).

- **Frame plates.** When a clip returns to a place already filmed, or must carry where things stand or what state they are in, take
  the frame of the earliest clip there that shows it, one per direction the new clip's shots face (a direction no earlier clip faced
  keeps the location sheet's panel), remove from it every character and the props that move or are carried in the new clip (in 3D
  a prop the new clip's first frame shows in its place stays even when it moves later in the clip: removed, a prop that stood in its place
  at the first frame and fell later was missing or did not fall in 2 of 3 takes; kept, it stood and fell as written in 3 of 3 and was never
  drawn twice, judged blind; a prop that only sits still there stays: it held its size best in its place; so does a crowd still there in the new clip: kept in the
  plate, a crowd stayed the same people, while a plate cleared of it gave one clip other people, a row of look-alikes,
  and one film's next two clips nobody where the crowd had been), and send it first in `images`, with the location sheet in
  3D and in place of the background plate in 2D (`images`: `frame:k1@8.0`; generation + 1; in 2D the plate it replaces is left out
  and the other is named by position, `["frame:k1@0.0", "l1#2", …]`, `script-format.md`). A 2D clip's first frame reproduces its
  plate almost exactly, so its second 0 is the cleanest source. A frame from inside a clip comes from the shot itself, not from the
  prompt's timing: the model's cuts land up to a second off the written seconds (a frame taken by the timing showed the shot
  before). Find the cuts as Order of work, Stubs, says, take the
  frame about 0.3 seconds after one, and look at it before the edit. When the edit fails, the clip keeps the location
  sheet alone, with the positions written against its anchor. When the new clip comes earlier in the story, the edit also restores
  the earlier state of what changed. Check it with `python3 "${HF_WORKFLOWS}/drama-ads/scripts/checks.py" plate plate-<id>.txt` (a tagged
  frame's edit: `plate-k1@0.5-morning.txt` for `frame:k1@0.5/morning`). A plate a lead will stand in has nobody in it who shares
  that lead's age, hair or clothes colour, and nobody where the lead will stand: a figure in the plate the edit aged into the lead's look took the lead's place and clothes (2 of 2);
  edited into someone unlike the lead in sex and clothes, the lead came back in their own clothes (2 of 2, judged blind). The
  edit: "Edit the attached reference image, one frame of a <template name> film: remove <each character by its look and its place in
  the frame> and <each such prop>, and fill what they covered with the place itself, continuing exactly what surrounds it:
  <surfaces>. Keep everything else exactly as it is: the same framing, <the objects whose place or state matters>, the light and the
  look. No people, figures, silhouettes or animals anywhere, in windows and reflections too; the place stands empty. No text, labels,
  logos or watermarks." A plate that keeps its crowd writes "<the crowd> stays exactly as it is; no other people, figures,
  silhouettes or animals anywhere, in windows and reflections too." in place of the empty-place sentence, and it is edited from a
  frame where the characters it removes cover none of the crowd: removing two leads who stood in front of it, the edit drew 5-8 new
  people where they stood, a child among them (2 of 2); from a frame where they covered none, it added nobody (2 of 2). Look at it: a second edit naming whatever was left removes it. A change of time of day goes in the same edit
  ("show this same place at <the time of day>; relight it in <the light and its side>").
- **Sheets from frames.** A prop a clip drew first, and a character or prop after it changes on screen, gets its sheet from that clip's frames: crop the frames that show it best, the face close first and then full-figure
  crops, tile them at one height into one composite (`ffmpeg -i a.png -i b.png -i c.png -filter_complex hstack composite.png`; in
  pixel art scale with `-sws_flags neighbor`), and edit it with the sheet wording of `sheet-realism.md`, `sheet-stylized.md` or
  `style-master.md` (prop sheets), adding "The attached reference image is <n> film frames of this one <character>, side by side: keep
  the face as in the close frame" and the finish sentence of a prop sheet or the sheet words of the style file (without it clay
  props came back as product photographs).
  Frames from two clips: name which frames give the face and which the body. Frames lit at night: "draw it in its true daytime
  colours: the night light belongs to the frames". Name the size of what changed against a part of the character, and how much of it shows: the edit shrinks what the frames
  half hide. Check it: `checks.py sheet … --stylized` for a
  character in 3D or 2D or a non-human in live action, `checks.py sheet … --photo` for a live-action human (the composite is its
  attached reference image), `checks.py prop …` for a prop; a sheet from frames may run to 2,600 characters. A sheet made from a clip's frames counts as a
  frame of that clip: write the clip in the prop's `sheetFrom`, or in the character's form in `forms` (`script-format.md`).
- **The first clip in a place** holds one wide shot per direction later clips will face, showing every prop they will need there:
  frame plates carry only what it framed (an object it never showed drifted to another spot in one clip and was drawn twice in
  another). In 2D `checks.py clip` refuses a place's first clip without a wide or medium-wide beat on each plate it sends, and a
  wide beat that also names a body crop ("from the chest up") does not count: written so, one first clip framed only the figure and the furniture in front of it.
- **The first frame takes its state and its camera height from the plate sent first, never from the words.** Make the plate in
  the state the shot opens in and at the camera height its shots need, and write no move the plate has already made: written "at
  standing eye height" over a high plate, the camera stayed high in 6 of 6; the plate remade at eye height (a new photograph of the
  same place from that camera position, not an inpaint edit: the inpaint edit kept the high camera), 3 of 3 at eye height (judged
  blind). A clip after something in the place was opened, sent the half-open plate with the opening move written again, opened on it shut in
  4 of 4; sent a plate with it fully open and the state written as it is
  ("<the changed thing> stands <in its new state>, as in @Image1, from the first frame"), every shot stayed open (3 of 3,
  measured and judged blind). A closing move went the way its first frame allowed in 8 of
  8, and a change of state drawn on an object in the plate stayed on it (2 of 2; 0 of 2 without).
- **Frame-plate edits keep the frame's own look:** they take no style block, and `checks.py` skips `--style` on a prompt that begins
  "Edit the attached reference image".
- **Remaking a part of a clip** (Cutting the film into clips): the remade part is a clip of its own with a new id, placed in film
  order in `clips`; the kept part and the remake each carry `kept`.
- **The edit model:** `gpt_image_2_6_flare` (medium, 2k) in 3D and 2D, `seedream_v5_pro` as an inpaint edit in live action
  (`models.md`).
- **The frames' faults become canon:** check a frame before deriving from it. No extra video to show a back view: a text-only
  turnaround drew another face and another room, and the edit draws a believable back. A location plate comes from the frames of one
  clip: two clips' frames gave two rooms in one sheet.

## References and their limits

- **Images:** at most 9 per clip, in this order, which numbers them `@Image1`, `@Image2`…: frame plates first (References from the
  film's own frames), then the location sheet (in 2D its plates, less any a frame plate replaces), then the sheets of the characters in
  the clip, then the prop sheets (`style-master.md`). The style master never goes to a clip.
- **Every image is in the film's look.** A photo sent straight to a clip in a drawn or built look comes back photographed in some
  shots and drawn in others, though the prompt says to draw the photos in the look. In pixel art, with a photographed place, person,
  animal and prop, the wide shots and the animal came out photographed and the face close-up drawn; with only one person's photo among
  drawn references, the wide shots came out drawn and that face close-up a photograph pasted into the pixel world. Redraw every photo
  first with the edit model and the master (a face: `sheet-stylized.md`; a place: `style-master.md`; a product: a prop sheet): the
  same clip made from the redrawn images held the grid in every shot and kept the photo's face and age.
- **Videos:** at most 10 per clip, each 2-30 seconds. Their total length, the extension's source part included, is at most 30
  seconds and at most the length of the clip being made: trim them (Order of work). The extension's source is the first video,
  `@Video1`.
- A reference video carries its camera and its cuts as strongly as its look: a video passed for its look or camera never has cuts in
  it, and at most two are passed for their camera. An extension's source may have cuts inside; it ends on the held shot it is
  extended from (Cutting the film into clips).
- **Audio:** at most 10 per clip, each 2-30 seconds, at most 30 seconds in all: the clip's part of the narration track or song
  first (`track`, in a narrated format), then the voice samples of its `voices`, in that order, numbered `@Audio1`, `@Audio2`…. An
  audio reference carries no picture and does not change a clip's generation.

## Voices

The model invents a new voice for every character it does not hear, so a voice made in one clip is lost in the next. Every clip in
which a character speaks a `dialogue` or `thought` line either hears them in its reference videos (the extension's source part or a
reference video that contains one of their lines) or gets their voice sample as an audio reference.

- **The voice clip:** of the clips in which a character speaks, the one made first (the lowest generation; among equals, the first in
  film order) makes their voice from their `voice` (script.json). Generate it before every other clip in which they speak. Give each
  speaker at least 3 seconds of speech in it, in a calm line in their normal register: a sample cut from a shout made every calm line
  of that character sound off, and a 1-second line left nothing to join. A first clip of 15 seconds holds about two voices (the hook's action
  first, the 4-second tail last), so a third speaker's voice clip is another clip of the first round. When another checked take made
  the voice (a remake, a take left out of the film), name it in that character's `voiceFrom` (`script-format.md`). A narrator
  of a narrated format has no voice clip: the narration track is their voice, and their sample is cut from it (`formats.md`).
- **The voice sample:** once the voice clip is checked, cut 3-10 seconds of that character speaking alone from it: no other voice,
  no loud effect. One sample per character, used in every later clip; never a sample cut from a clip that itself got the sample (a
  copy of a copy drifts). A single line shorter than 3 seconds is joined with another line of theirs from the same clip; with none,
  repeat it or pad it with room tone to 3 seconds (both held the voice).
- **Finding the moment:** the line's `startSeconds` minus its clip's `start` says roughly where it is; the word times from faster-whisper `medium` (Order of work) say roughly where it starts and ends: against the voice's onset on a spectrogram, a line's first word in its clip's own pass started a median 0.15 s early, 32 of 100 lines more than 0.3 s off; after 2 s or more of silence in the clip 12 of 62 lines started 0.5-2.0 s early (the word stamped where the silence began), and the whole-film pass still put 23 of those 62 more than 0.3 s off. Its last word ended a median 0.06 s off on 40 lines (`small`: first words 0.29 s early, 19 of 40 more than 0.3 s), the worst 0.8 s late, so listen to a sample's last half second for the next line's first word. A frame at its middle shows whose mouth moves.
- **In the prompt:** bind each sample to its character by both tags: "@Audio1 is the voice of @Image2, <the character by its look>:
  every line <he | she | it> speaks is in this voice." Then write each line under its character, never under the audio.

## The clip entry (`clips` in script.json, `script-format.md`)

- `id` (`k1`, `k2`…), `start` and `end` in film seconds (4-30 seconds long), `location` (a location id).
- `make`: `fresh`, `extend` or `part`. For `extend`: `source` (`{"clip", "from", "to"}`, seconds inside the source clip; the whole clip when
  they are its full length) and `direction` (`forward` or `backward`). A `part` is the later range of a clip whose middle shot was
  remade: `of` (that clip's id) and `kept` (its seconds in that clip's take), placed after the remake in film order; it is never
  sent or prompted, and its frames and generation are that clip's.
- `images`: ids in order: frames written `frame:k1@12.5` (the clip and the second inside it, counted from its first frame, never
  the film's second; a second edit of the same frame, such as a relit one, takes a tag: `frame:k1@12.5/morning`), sent as frame plates (References from the film's own frames); location ids (their sheet, or in 2D all their plates) or one 2D plate by position (`l1#2`); cast ids (their sheets); prop
  ids (their sheets, `style-master.md`).
- `videos`: `{"clip", "from", "to"}` for each reference video, from originals only.
- `voices`: the cast ids whose voice sample the clip carries (Voices), in order; empty when every speaker is heard in its videos or the
  clip is their voice clip. Narration and sung lines never need one: they are one track made before the clips (`formats.md`).
- `track` (a narrated format only): `{"from", "to"}`, the seconds of the narration track or song this clip lip-syncs, 2-30 seconds.
- `kept` (a clip trimmed after it was made): `{"from", "to"}`, the seconds of its generation used in the film, or a list of such
  ranges in order; `end - start` equals their total. Its lines are timed as measured, and the 4-second minimum and the line tail do not apply to it; nor does the line tail apply to a line that carries its measured `endSeconds` in any take that was looked at (`shots` written), trimmed or not. Write `generated` with it, the generation's own length in seconds: frames and reference parts taken from the clip
  are measured against it, not against its length in the film.
- `positions`: where each character stands at the first frame, relative to the location's `anchor` (never "frame left" or "frame
  right"); keep who is on which side of whom the same across clips unless the clip shows someone cross.
- `stateIn`, `stateOut`: what is true at the first and the last frame (who holds what, what is broken, open, lit). Nothing changes
  between clips unless a clip shows it change.

## The clip's prompt

Write it into `clip-<id>.txt` and check it with `python3 "${HF_WORKFLOWS}/drama-ads/scripts/checks.py" clip clip-<id>.txt script.json <clip id>`.

- **The order:**
  1. the film's `style` line;
  2. its style file's video words (`scripts/styles/<template>.md`);
  3. the clip's action beat by beat, in literal camera terms, each beat its own paragraph opening with its seconds
     ("<from>-<to> s: <framing> …"): `checks.py clip` reads only those, and a prompt without them is refused;
  4. its dialogue (speaker, words, delivery);
  5. its effects (`effects.json`, `plan-and-effects.md`), each named only on its owner.

  In a clip where nobody speaks on screen, leave out the video words' sentences about mouths and voices.

- **The hold sentence**, where the style file's video words have one, goes to the end of the prompt, not after the style line. It names every element of that clip the look must cover:
  - its characters, in close-up and in motion;
  - its props and effects;
  - its sky and light (stars and lamplight at night, clouds and sunlight by day).

  It says what each element is, never what it must not become: "nothing turns into a 3D render" drew a 3D-render preset suggestion on
  every clip. A clip that cuts between places adds "in both places".

- The language, word for word, in every clip with speech: "Every spoken line is in American English, exactly the words in quotes;
  nobody speaks any other language." Without it a whole clip came back spoken in Mandarin.
- No music, word for word, in every clip's prompt: "No music and no score." The video model sometimes adds a score of its own,
  and music belongs over the joined film (Assembly). A clip that lip-syncs its part of the song has its own sound sentence instead
  (`formats.md`).
- The hook's physical action comes at 1-3 seconds with both characters in frame through second 3, and the first line only after it
  lands: an action written at second 0 was played in half a second, and a line at 0.5 seconds turned a shove into a touch. In the
  hook's shot neither has their back to the camera or stands between the camera and the other, so both faces and the action between
  them read in one frame through second 3: written with one's back to the lens, both faces showed at second 3 in 0 of 3 takes (and
  one brief opened on a back in three runs); written so, in 3 of 3, and the conflict was retold from that one frame (judged blind).
- Lines land from 1 second early to 1.5 seconds late, and later after a long stretch before them in their clip: up to 3.7 seconds late after an opening action of several seconds, 2-4 seconds late after an action of the speaker's own written before the line in its shot or a long insert before it, 2.65 seconds late after a silent reaction shot that ran 1.9 seconds over its writing, and the next line late with a late one, 4.7 seconds (nine lines in three films; an insert written 2.8 seconds ran 5.3). Time
  the beats by the take, never by the plan, and time the clip's last line so it ends at least 4 seconds before the
  clip's end, and put the ending's action after it. Every shot after a clip's last line says so in its own words ("in silence, <the
  action>"): a silent 4-second shot written without it came back with the last line said a second time over it.
- Every shot says each character's posture (`checks.py clip` refuses a beat that names one without it; a name or tag inside the description of a depiction, from "photo", "portrait", "picture", "drawing", "painting" or "poster" to the end of its clause, is not read as the character in the shot, so a character who is in the shot is named before it or in a sentence of their own) and, at a door, a window or any edge the action turns on (a curb, a threshold, a
  counter), which side of it and on which surface they are ("<the character> stands <inside | outside> <the opening>,
  <behind | in front of> <its edge>"; "<the prop> <in the place> <below | above> <the edge>, on <the surface it stands on>,
  <the edge> and <the surface beyond it> behind <her | him | it>": a prop written only by the space it stood in was set on the
  surface beyond the edge 2 of 2 times, written so on its own surface 2 of 2, judged blind), and where a prop out of frame is ("<the prop> on <the surface> to the <side>, below the
  frame"): a background plate that shows seats sat a standing character down, a character came out drawn outside their own door,
  and a prop left unplaced moved in front of two close-ups. In a close-up, write where the table or counter in front of them ends and what lies on it out of frame ("<the furniture>'s
  edge at <the part of the body it reaches>, below the frame; <what lies on it> out of frame"): a close-up over a counter drew what
  lay on it as a mound filling the lower third of the frame, the body sunk into it.
  A face wanted from a character who stands on the camera's side of a table or counter comes with the camera turned around: behind
  the furniture, looking across it at them, toward what is behind them, named by its location-sheet panel ("from behind <the table>,
  looking across it at <the character>, toward <what that panel shows>"). With the camera facing the furniture and the character
  written "in front of it", the face was given by drawing the character behind it or beside its end (3 of 3); written so, the character stayed on their own
  side, face to the camera (3 of 3, judged blind), though the plate sent first still faced the furniture from their side. A shot that shows a piece of
  furniture together with a character standing on the camera's side of it, from a medium shot to a wide, writes that character seen
  from behind or at three-quarters from behind, on <their> side of it, and turns <their> face to the camera only after <their> action
  there ("<the character> stands on the camera's side of <the furniture>, seen from behind at three-quarters, <their> back half to the
  camera; <the action>, then <they turn> <their> face over <their> shoulder to the camera"); a close-up, or a shot that leaves the
  furniture out of frame, keeps the face to the camera as written. Written turned three-quarters toward the camera, the characters
  were drawn behind the furniture in 4 of 6 takes of a test (and 3 of 4 takes over two films); written so, on the camera's side in
  6 of 6, and a close-up written after it kept the face (6 of 6, judged blind).
  A door, gate or window a character opens is two shots: their hand on the key or the handle (an insert), then the opening seen
  from their side, their back to the camera, the features of their side of it named around them in frame and what lies beyond only
  through the opening ("from behind <the character>, on <their> side of <the door>, <their> back to the camera, <the features of this
  side> around <them> in frame; through the opening, <what lies beyond>"): written as one shot facing the door, the opener was drawn
  on its far side in 2 of 2; as the two shots alone, on the camera's side, but with their own side drawn again beyond the door in 3 of 5;
  with this side's features named around them, on their own side in 3 of 3 (judged blind).
- **Every shot has its subject in frame from its first frame,** and a clip opens and ends on a character or a story prop, never on a
  surface: the model likes to open and close a clip on a transition. Written as an entrance through something the character first moves aside, one clip opened
  and closed on a second of it filling the frame, nobody in it. Write an entrance with the character
  already in frame ("<the character> steps through <the opening>, in frame from the shot's first frame").
- **The last frame is written by who and what are in it.** A shot that ends on a flash, a glow or a whiteout names what is seen when
  it clears, every subject in it: written as the white "fading on <one subject>", one film's last shot showed that subject alone on
  black, the others in it gone.
- In the film's last shot, a character who leaves is written by the frame side they leave by: <the one who leaves> at that side of
  the frame and whoever stays at the other, <the one who leaves> walking out of frame <side> in a straight line along <a feature
  that shot's view shows>, past <a landmark on that side>; whoever stays is written still, in full view from the first frame to the
  last. Written as a walk toward a place the view does not show, the one who left crossed in front of the one who stayed and hid
  them (1 of 1 in a film), and stayed in frame to the end in 2 of 3 takes; written so, they left by the named side with the other in
  full view in 3 of 3 (judged blind). Exits in other shots follow their own action.
- A delivery never asks for a pitch against the character's `voice` ("low, slow" for a high voice, "a wail" for a bass): it swapped
  or replaced the voice. A shouted or panicked line of a low voice restates its register in the voice's own words, never "yells", "screams", "shrieks" or
  "loud": an "outraged" delivery flipped a bass to a shriek even with the voice sample, and "loud and rough" with the register named
  still lifted a line an octave. Put the register in the voice binding too ("@Audio<n> is the voice of @Image<n>, <name>: <the voice's
  register words>"): together they brought the line back down.
- Each prop at the moment it acts is named again by its tag with the detail that tells it apart ("@Image<n>, <the prop>, <the
  detail>"), with its size against a part of a character; every shot that shows it names it so. A prop told apart by its container
  is written with the container ("<the prop> in the <container's colour> <container>"), never with the container's colour on the
  thing ("the <container's colour> <prop>"), and a part of it in its own colours ("<a portion> of <its own colour> <its part>"):
  written with the container's colour on it, the prop came out in that colour in 2 of 2 takes (and in 4 of 4 shots of one film),
  written so in 0 of 2 (judged blind); so is a place feature the action uses, with its size against the
  character. A change that must stay is written to the end: "from <second> to the last frame <the changed state> stays". A part of
  a character is never named alone: it is drawn as a separate thing. A mark the story turns on holds only on a prop with its own
  sheet, shown in an insert: among alike things without one it came back as other marks.
- What makes a character recognisable (an accessory, a mark) is named in their reference sentence ("@Image<n> is <name>, always
  <the feature>") and in every shot of them: named once per clip, the feature was gone from every shot of two clips, and named so it
  held in every later clip.
- Two identical objects the story turns on merge into one: show both in one shot, or make them differ visibly.
- Machines, packs and signs get printed words and badges: write them as "a plain unbranded <thing>" in every prompt. The user's own
  product is the exception: it keeps its name and label as its prop sheet shows them (`style-master.md`, Prop sheets); written
  plain, an ad's product came back with its name nowhere on screen.
- **The user's product's label reads only in a close insert** where the product fills the frame, upright and whole: at 480p small
  or tilted lettering is redrawn as look-alike letters, and in a medium shot a two-line label did not read.
- **Every prop in frame sends its sheet** in `images`, in every clip that shows it: sent only the place and the characters, one clip
  drew a prop in its case as another object. `checks.py clip` refuses a prompt that names a prop whose sheet the clip does not
  send.
- **A crowd is written by how it fills the place, never by a number,** with the ages of its `groups` entry written as what shows
  them ("every one an adult of <their ages>: <the hair and the lines of those ages>, adult height and build"), behind the action and
  out of focus: a film that wrote its crowd as a dozen people showed four in one clip and a changing crowd in another, its far faces smeared at
  480p; written without ages, two crowds meant as a <number>-year-old lead's age-mates came out decades younger.
  With the ages alone, a 3D crowd of that age still had members younger than written in 1 of 3 takes (2 of 6 clips of one film), and
  with the group's whole description (its hair colours, its clothes colours) in 3 of 3; with the ages and their marks, none in 3 of 3
  crowd-only shots (judged blind), but in films with the cast in front the same wording gave a crowd decades younger in one take and an
  older one in the next, and a child in another: ages written in words drift from take to take, so the first take that shows a crowd is judged face by face
  before its frame becomes a plate. Nothing else of the description goes with them: written with its mix and its clothes colours added, 3 of 3 takes had
  members younger than written again (one to seven each), and with the marks written for every member and the mix kept, 2 of 3 still had
  one (judged blind); the marks alone keep the ages and can lose the mix. Anyone the story singles out of a
  crowd is a cast member with a sheet. A shot that shows none of the cast is a clip of its own that sends no cast sheet: in a
  clip that sent them, a crowd shot drew a double of a cast member (2 of 2, and 2 of 2 with "<name> is not in this shot");
  sent none, it drew nobody like that cast member (2 of 2).
- **Spell out the shot and the face.** The model frames wider and plays milder than asked: a line marked only "firm" was played with a
  smile. So write:
  - each shot's size and framing, and the size of each gesture;
  - every expression in face words: what the brows, eyes and mouth do;
  - a gesture as its own beat rather than timed to a single word, where it may not show;
  - a hand one character holds out toward another framed over the receiver's shoulder, both in shot ("over <the receiver>'s
    shoulder onto <the giver>: <the receiver>'s shoulder and the back of <their> head soft at the near <side> edge of the frame"):
    in a close-up on the giver alone, the hand came in from the frame's edge on the receiver's arm (1 of 1 in a film, 1 of 3
    in a test); framed so, the giver's own arm in 3 of 3 (judged blind);
  - a look as the face that looks ("<the character> looks down"), never as its target: a look written as its target became a
    camera tilt down to the looker's own body. A glance at something behind the camera is a direction ("glances to <their> left, past
    the camera"), and in a clip whose shots all face away from it, nothing behind the camera is named anywhere in the prompt (its
    @Image sentence says only "<the place> seen toward its far end"; its light and sky are left out): named, even "out of frame
    behind the camera", it was drawn behind the character in 6 of 6; named nowhere, the plate's view in 3 of 3 (judged blind).
- One physical action per shot. A bodily contact is a wind-up, a cut and the aftermath; a change of state is a shot before, a cut and
  a shot after (WHAT THE VIDEO MODEL CAN SHOW, `story-rules.md`), the after shot opening a clip of its own that sends the
  after-state's form sheet: inside one clip, a face between them or not, the after shot opened in the before state and changed on
  screen (4 of 4 for a prop joined to a piece of it that had come off, one fused into one piece); opening its own clip, it was right from the first
  frame (2 of 2, judged blind). That clip opens on a close insert of the changed thing or on the reverse view, never on the view the
  clip before ends on: opened on the same view, the cut read as a jump, someone moved (2 of 2); opened so, it did not (0 of 2,
  judged blind). A move that opens or changes a place's light (a window covering drawn back, a door flung wide) is written as a
  slow pull ("<the action> <the place's light-changing fixture>, the gap widening over <seconds>"): written as a fling it opened in 3-5
  frames in two films; written so it moved over 33 and 69 frames, though one take still cut away a third open. Write every state as it is, never the failure to avoid ("it stays
  joined", "it never comes back"): the model draws what the words name.
- A state of a fixture a character works by hand (open, shut, on, off) that a later shot names is changed on screen in the shot
  before, by a hand, as that shot's last action ("<the hand> pushes <the fixture> shut, and from <second> to the end of the shot
  <the fixture> stays shut"), or the later shot opens its own clip from a plate in that state; it is never written only as the later
  state. This is for fixtures a character works by hand, not for light or weather: written only as the later state, the fixture moved
  with nobody touching it in 3 of 3 takes; changed by a hand in the shot before, in 0 of 3, and the shot's own action still played in
  3 of 3 (judged blind).
- After a prop or a character changes, the clips that show the after-state send that
  state's sheet in place of the before one (`style-master.md`, one entry per form), and every shot names the after-state or keeps it
  out of frame: a shot after a prop changed showed it in its before state again, and a framing that left it out fixed it.
- A character's voice clip carries their `voice` words with their first line ("in <his | her | its> <voice words>").
- **Name the references by their tags:** "@Image1 is <the place>: its left panel faces <its far end>, its right panel faces back
  to <its near end>; @Image2 is <name>, <the character by its look>; @Image3 is <the next one, by name>…". The tags count the
  clip's `images` in order, so adding or dropping one moves every tag after it (dropping one reference renumbered four prompts of
  one film): `checks.py clip` refuses a reference sentence that does not name the character or prop its number sends.
- **The background.** The model may take a shot's background from the wrong panel or plate, whatever the tags say. Name the
  landmarks it must show inside the shot, each with its side, and check each shot's background.
- **An extension:** "@Video1 is the clip being continued: keep <what stays exactly>; this clip adds <what is new>". Never restage
  what the source already shows.
- **Voice samples:** bind each one to its character as Voices says.
- **In 2D:**
  - Name the plates: "@Image1 is <the place> seen toward <a landmark>; @Image2 is the same place seen the other way, toward
    <a landmark>".
  - Write each shot as "the view of @Image1, static camera", with its framing in words, or with the camera move its style file
    allows. A plate sets the place, never the framing.
  - In a flat world, with one backdrop, write "@Image1 seen straight on, static camera".
- Write `positions` and `stateIn` as present facts of the first frame. A fresh clip never says "continuing from the previous shot":
  the model replays the old ending as the clip's first second. Only an extension refers back, and only through `@Video1`.
- Time the beats in the clip's own seconds, 0 being its first frame, an extension's included.
- Leave music out of the clips: music made in separate clips drifts when they are joined; add a score at assembly if the film wants one.
  The one exception is a clip that lip-syncs its part of the song (`formats.md`).
- Only what a camera films goes into a prompt. A fade, a dissolve, slow motion or a title is made at assembly: a fade to black
  written into a clip was ignored.

## Planning the rounds

Clips that need nothing from each other run in one batch, so a film takes as many rounds as its longest chain of waiting. Plan that
chain before the first paid call, while writing `stateIn` and `stateOut`.

**1. List the states.** For every clip, write down:

- its place;
- its time of day and light;
- the state of every prop and character at its first and last frame.

**2. Prepare every state in step 3.** Some states a later clip opens in would otherwise exist only once an earlier clip shows them on
screen: a prop or a character after it changes, a place in another light. Make each such state's reference
with the other images, from the master:

- a form sheet for a prop or a character (`forms`, one entry per form);
- a plate or a location sheet for a place in another light.

The later clip sends that reference and none of the old state's, so it no longer waits for the clip that shows the change and runs in
the same batch. The change itself is still shown on screen, as a shot before, a cut and a shot after (`story-rules.md`).

**3. Know what still waits.** A clip waits only for what no image made ahead can give it:

- a voice: the speaker's voice clip and sample;
- the place as it was filmed: every clip in a place an earlier clip filmed sends that clip's frame plate (References from the
  film's own frames). With the location sheet alone, one place's layout changed between clips.

**4. Plan the rounds.**

- **Round 1:** the first clip in each place and each speaker's voice clip, often the same clips, in one batch.
- **Round 2:** every other clip in one batch, with the frame plates and samples from round 1 and the prepared states.
- **Remakes** join the next round.

Four 2-minute films of nine or ten clips ran this way: one clip, then a batch of eight, then remakes, in 53 to 63 minutes each. A
state prepared ahead and sent to a clip running beside the one that shows the change is untested as a pair: look at both before
building on them.

## Order of work

**Every paid call carries all it needs** (`SKILL.md`, Sending), every id copied from `jobs.json`: an image its checked prompt file's
text, with the model, quality, variant, 2k, shape and attachments `models.md` gives it; a part of the song the prompt of
`song-prompt.txt` and its own sung lines (`formats.md`); the narration the narrator's lines of script.json joined in order, nothing
else, in the narrator's voice and at its `speechRate` (`formats.md`); the score the prompt of `score-prompt.txt` at its length
(`models.md`, Voices, songs and the score); a clip the film's shape and resolution, its length and mode, its references in its
entry's order and the prompt of `clip-<id>.txt`. Written from
memory, the calls of one film left out the shape and the resolution, and twelve clips came back landscape, seven of them billed at
720p; retyped prompts changed words, and typed URLs were refused. When the first result of a call is done, measure it (`SKILL.md`,
Checking a result) before the next call goes out.

1. Make the reference images and look at every one (`SKILL.md`, step 3). In a narrated format, make the narration track
   or the song now too, time the lines and the clip plan to it, and run the checks of steps 1 and 2 of `SKILL.md` again
   (`formats.md`).
2. Generate the originals (generation 0), in parallel.
3. Look at and listen to every clip before anything is built on it (`SKILL.md`, step 6): faces, clothes, the
   room, the positions, every prop against its sheet (the user's product above all: at 480p one came back in two shapes in one
   film, another with its label upside down), the language, words and timing of every line. A defect in a source is paid for
   again in every clip made from it; remake a bad original (or only its broken part) before using it.
   - **Stubs.** Find the clip's cuts with the scene filter in the sandbox (`ffmpeg -i k1.mp4 -vf
     "select='gt(scene,0.1)',metadata=print" -f null - 2>&1 | grep -E 'pts_time|scene_score'`, the cut seconds rounded to
     hundredths), and look at the frames on both sides of every cut it returns: at a 0.3 floor a
     scene filter missed 6 of 92 cuts, a cut to a dark room, a cut-in on the same set, an over-the-shoulder to a closer single; at
     0.1 it missed none and added 16 false candidates in 24 clips; any floor counts a light switched on or off. Then the length of
     each shot between the cuts and the clip's two ends. A shot under 0.5 seconds is a
     stub: the model's cuts land up to a second off the written seconds, and a shot the prompt put first or last in the clip,
     most often a silent reaction, can shrink to a few frames (tested: stubs of 10 and 13 frames read as jumps in the film, shots of
     17-19 frames did not). A stub with no word of the clip's whisper in it goes out with its sound, through `kept`: the range
     starts at the cut after a stub at the clip's start, ends 0.02 seconds before the cut of a stub at its end (a range ended at the
     cut's time rounded to hundredths kept the stub's first frame), and goes around a stub inside the clip as two ranges. A stub
     that carries a word is a broken beat (Cutting the film into clips). An extension's source range leaves the source's stubs out
     too: the extension continues the frames at its edge.
   - **Empty shots.** Look at the middle frame of every shot: a shot with no character and no story prop in it (cloth, a wall or a
     blur filling the frame) goes out like a stub when it carries no word, and its beat is remade when it does. Two such shots of a
     cloth, 1.3 and 1 seconds long, reached one finished film unseen at 480p.
   - **Music.** A clip can come back with a score of its own despite "No music and no score.", and it would play against the
     film's score. Where the sandbox has Demucs (`python3 "${HF_WORKFLOWS}/drama-ads/scripts/stems.py" check`; `models.md`, The
     sandbox), take it out of the clip instead of remaking it. Without Demucs a clip with music is remade, or in a narrated
     format muted under the track (`formats.md`).
     - `python3 "${HF_WORKFLOWS}/drama-ads/scripts/stems.py" split k1.mp4 …`, run from the film's folder with `background: true`, several clips in one call, splits each
       clip with sound once into vocals, drums, bass and other. It prints how loud the clip's music (bass and other) is against
       its lines, under them and between them, and its hits (drums) and room between them; a clip without lines is measured
       against the film's lines. `"music": true` marks music within 20 dB of the lines; music further under has little to take
       out, and the clip keeps its sound (a drama-editor threshold). Never split a lip-synced sung clip, whose sound
       is the song, or a clip whose music the story plays on screen (a radio, someone at an instrument).
     - `python3 "${HF_WORKFLOWS}/drama-ads/scripts/stems.py" clean k1.mp4 <mode>` writes `k1-clean.mp4`: the same picture, byte for byte, and the sound the mode keeps, at
       the original's sample rate and channels, so it still joins with `-c copy`:
       - `voice_room` (the usual one): the lines, the hits (blows, steps, doors) and the room: the music's held notes and
         chords go, the noise-like sound of the place (air, a street, rain) stays, and with it a noisy part of the music (a
         riser, a shaker);
       - `voice_fx`: the lines and the hits, no room, for a clip whose room part still carries the music;
       - `voice`: the lines alone, for a clip whose sound under and between the lines is only music, or whose score has a beat
         (a beat splits into the drums);
       - `voice_rest`: the lines with everything else 12 dB under, for a clip whose music is faint and whose room or effects
         carry the scene.

       On `voice` and `voice_fx` the room goes with the music, and the clip can turn dry. Separation thins a voice a little and
       can leave a faint warble (drama-editor tests): whisper the clean clip, and every line must still read word
       for word.

     - From then on the clip is that file: its trims, frames, voice samples and joins are cut from it, and a later clip that
       would take it by its job id (an extension's source, a reference video) gets it uploaded instead (step 5), so the music
       does not come back in the clip made from it.
4. Then the generation-1 clips (and at 1080p the generation-2 clips), each as soon as its source and references are done and checked. A clip
   whose `voices` lists a character waits for that character's voice clip and sample, whatever its generation.
5. Trims, frames and voice samples: download the clip into the film's folder in the sandbox (`curl -L -o k1.mp4 "<result url>"`),
   make the file with ffmpeg, upload it and pass its id.
   - a part of a clip: `ffmpeg -ss <from> -to <to> -i clip.mp4 part.mp4` (add `-an` only to a part passed for its picture; an
     extension's source that must carry its speakers' voices keeps its sound)
   - a frame: `ffmpeg -ss <second> -i clip.mp4 -frames:v 1 frame.png`; the exact last frame: `ffmpeg -sseof -0.1 -i clip.mp4 -frames:v 1 -update 1 last.png`
   - the word times: `python3 -c "from faster_whisper import WhisperModel as W; s,_=W('medium',device='cpu',compute_type='int8').transcribe('clip.mp4',word_timestamps=True); [print(f'{w.start:.2f} {w.end:.2f}{w.word}') for x in s for w in x.words]"`
   - a voice sample: `ffmpeg -ss <first word's start - 0.1> -to <last word's end + 0.2> -i clip.mp4 -vn -ac 1 voice-<cast id>.mp3`
6. Save every job id and media id in `jobs.json` the moment you get it, each voice sample's media id under its cast id.

## Assembly

- Assembly runs in the sandbox (`sandbox_exec`), in the film's folder. Download every clip there (`curl -fL --retry 3 -o`) from
  its result URL in `jobs.json`. An extension comes back as the new part only, at the length you asked for, and its first frame repeats the
  source's last frame, so the two join without a visible seam (tested: a 15 s forward extension of a 15 s clip returned 15.0 s). If a
  clip ever comes back longer than planned, the extra is the source part: cut it off.
- Join them with `python3 "${HF_WORKFLOWS}/drama-ads/scripts/assemble.py" join script.json --clips <dir> -o joined.mp4`, each clip downloaded as
  `<dir>/<id>.mp4`: it cuts every clip to its `kept` ranges or else to its planned length (trim points: Cutting the film into
  clips), the picture by frames and the sound by samples, and joins them in film order with hard cuts and one encode. Every clip
  comes back one frame longer than asked (40 of 40 six-second clips: 145 frames at 24 fps), so uncut clips drift off a song; and
  each clip cut to its own file and joined with `-c copy` put the sound 23-43 ms later at every seam, the last clip of four films
  118-226 ms behind its lips, where the script kept every clip within a millisecond.
- Add music, if any, now, over the joined film. A score under dialogue: one instrumental (`elevenlabs_music_v2` through
  `generate_audio_batch`, `models.md`, Voices, songs and the score), made with clips round 2 (`SKILL.md`, Stages in ask
  mode) and only laid over the joined film here, started at its first sound (the end of its opening
  silence, `silencedetect=n=-45dB`), cut at the film's end and faded in and out. Its level is set by measure, about 10 LU under the
  clips' sound: `ebur128` on the joined film and on the take, then `volume=<film I - 10 - take I>dB` on the take into
  `amix … normalize=0`. Then whisper the film again: every line must still read word for word (tested on a 2-minute film, the
  score 10.7 LU under). In a narrated format lay the narration track or the song over it at its timeline, the music under the
  voice; keep a lip-synced sung clip's own sound for its length, and mute a silent clip that came back with a voice (`formats.md`).
- The clips' own sound stays under everything: their room tone and effects fill the gaps between lines and sung phrases. Every
  clip is made with its sound on; a film whose clips were made silent, so that nobody would sing along, had nothing between its sung
  phrases. A voice a clip adds is muted only where it is (`formats.md`, Silent clips), with `--mute <clip id>:<from>-<to>` (its
  take's own seconds) on the join, and its music taken out (Order of work, Music); where no track or score plays over a muted
  span, `--fill` lays the clip's own room tone there instead: a mute alone left 2 seconds of digital silence in one dialogue film.
- Every edit beyond the hard cuts (a fade at the end, a dissolve) is made here with ffmpeg, never asked of the video model.
- Last, the film's loudness: `python3 "${HF_WORKFLOWS}/drama-ads/scripts/assemble.py" loudness mixed.mp4 -o film.mp4` (the joined film with its music,
  narration or song laid over). It holds loudnorm linear, raising the sound into a limiter while its peaks leave no room, and
  measures the encoded file: -14 LUFS, true peak -1.5 dBTP or lower, or it refuses. Run as two plain passes, loudnorm silently
  compressed all four films of one test instead, lifting the room tone between lines up to 4 dB more than the lines, and the
  AAC encode left their peaks over -1.5.
- Deliver, after the captions when the film gets them (below), as `SKILL.md` step 8 says: `media_upload`, the PUT in the sandbox,
  `media_confirm`, and the user gets the link `media_confirm` returns, exactly, with the report.

## Text on screen

Text appears on screen only when the user asks for it (`asked.texts` in script.json). The clips never draw it: the video model
redraws letters as look-alikes, so no clip prompt names it, and the shot under a text keeps room for it clear of faces and the
product. After the loudness and before captions, lay each text over the film at its seconds, in its exact words, in the look of the
style file's Captions unless the user shows another: `picture` over the shot, `black` on a black frame in place of the picture for
its seconds, the sound unchanged either way. Then look at a frame inside every text: every word exact and readable, and nothing the
story needs hidden under it. Captions are then placed around the texts as text already on the film.

## Captions

Captions are optional: a film with lines gets burned-in captions in its style's look (its style file, Captions) only when the user
asks for them (`SKILL.md`, step 7); a look the user shows is written as the same flags. They are made by the `video-montage` workflow
(load it with `get_workflow_instructions`; its `references/subtitles.md`), which owns their timing, placement, burning and
checks. This workflow is its caller and hands it, once step 6 of `SKILL.md` has passed:

- **the film:** the finished film, and for the timing the joined film before the score went under it;
- **the lines:** `script_manifest.json`, `{"blocks": [{"vo_line": "<the line's text>"}, …]}`, one block per entry of `lines` in
  film order, every kind (dialogue, thought, narration, sung), so the captions carry the script's words;
- **the language**, `en`, and **the look:** the style file's Captions flags, `--max-words` for `audio_to_captions.py` and the rest
  for `subtitle_paper_burn.py`.

Before the burn, read the caption file it times: in the test films the first word of a line sometimes stood alone 4 to 7 seconds
before the rest of it. Move such a word into the caption that follows it. Keep the film without captions. Captions are burned
last, on the film at the resolution it goes out at: an upscale after the burn softens them (one film's captions were burned 30
pixels high into a 480-pixel-wide frame).
