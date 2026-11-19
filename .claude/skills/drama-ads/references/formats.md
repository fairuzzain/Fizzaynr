# Formats: how the film is told and heard

A format says who speaks, to whom, how the words are delivered and how the sound is made. It is chosen apart from the look: any
format runs on any template (`styles.md`). `format` in script.json is its id: the one the request names or describes ("a narrated
story", "a sung story", "a talking <object>", "inside the body") or a reference video shows (`SKILL.md`, A reference video),
`dialogue` when neither does.

A format changes only the rules it names below, and wins over them; every other rule of the skill holds as written, and NO SENSITIVE
CONTENT (`story-rules.md`), the no-children rule (`characters.md`) and the originality rule (`styles.md`) hold in every format. Where a
style file (`scripts/styles/`) and the format disagree, the format decides who speaks, to whom and how; the style file keeps the rest.

## Dialogue (`dialogue`, the default)

The skill as written: the cast speak to each other on screen, lip-synced, in short exchanges; the protagonist's inner voice (V.O.)
only where VOICE OVER INTELLIGENCE allows it. Each character's voice is carried from clip to clip by its voice sample (`clips.md`,
Voices).

## Talking object (`talking-object`)

- **Default look:** `feature-3d`.
- **Script:**
  - Two characters: an everyday object with a face and arms (`kind: other`) and the human it belongs to or stands beside. An animal
    that speaks to its owner plays the same way.
  - The object is the only one who speaks; the human answers with face and body. "A's line causes B's response" is met by the human's
    action or reaction.
  - It talks to the human in the second person, looking at them (`lines[].to` the human's id), and into the lens only on a line that
    addresses the viewer: a command first, then the reason, in short lines.
  - The protagonist is the human by default: their talking back and their deliberate move are actions.
  - Hook: the object pops into frame in the middle of the human's action and stops it, between the human's face and what they were
    about to do.
  - It acts with its whole body by the style's physics: it hops, waves its arms, leans in. In a cartoon look a talking object is what
    the style makes normal; in live action it is the film's one world rule (WORLD RULES).
- **Video words:** "<object> talks with its own mouth, lip-synced, its eyes and brows acting every line, looking at <human>, and into
  the lens only when it speaks to the viewer. <human> does not speak; <she/he> reacts." (tested: every line word-perfect in one
  steady voice)
- **Pitfalls:** an object with a face is drawn as a product with a printed label: write its face side as "its smooth front".

## Narration: what `storytime`, `song` and the body diary share

In these formats one voice tells the film over the picture. Its lines are `"kind": "narration"` (spoken) or `"kind": "sung"` in
`lines`, and its screenplay cue is `<NAME> (NARRATION)` or `<NAME> (SUNG)`. They change these rules, and only for those lines:

- **VOICE OVER INTELLIGENCE** governs the inner voice (`thought`); narration is its own channel and may run through every beat. In
  the HOOK it may state the conflict over the conflict image, which still has to pass the freeze-frame test alone.
- **What is on screen:** whatever the conflict turns on is shown (OBVIOUS FIRST); the narration may name the background, the time
  jumps, what the protagonist knew or feared, and others' words quoted inside it. In place of DIALOGUE RULES' "Nobody explains their
  feelings": it never names a feeling the face is playing in that shot.
- **Words** (`script-format.md` and `checks.py`): a narration line up to 20 words, a sung line up to 11; narration and sung words follow
  the format's rate below, outside the per-beat cap and the 30-word monologue limit (WORD BUDGET PER BEAT). They are timed on the
  film's timeline from the track's word times, not inside one clip, and their `to` is `null`.
- **One track, made before the clips:** narration made inside the clips changes voice at every cut and cannot carry a sentence across
  one. Make it once with `seed_audio` (`models.md`, Voices, songs and the score):
  1. The voice: one narrator voice, chosen as `models.md` (Voices, songs and the score) says, the same on every call. Record it
     in script.json's `narrator` (`script-format.md`).
  2. The rate depends on the voice: tested presets read 118-150 words a minute at their default speed, with pauses of about a second
     between sentences, so every first take at the default speed overran its film by 4-10 seconds. Make it at speech rate 30,
     and measure the take: its length is never predicted from the rate (one preset at rate 30 read 140, 164 and 197 words a minute
     in three films, one request 146 and 237 in two takes, every word right; the 140 take ran 72 seconds for 60, 31% of it pauses,
     and shortening them fitted it to 57 seconds with no word lost). When it runs past the film's last 2 seconds, shorten every
     pause longer than 0.45 seconds to 0.3-0.4 seconds (no word lost) or cut words; with an asked pace (`asked.wordsPerMinute`), lay
     each sentence at its line's start, the silences where the script puts them; when it runs short, lay it sentence by sentence,
     the take's own gaps inside clips and gaps of up to about 2.5 seconds at cuts (a take 10 seconds short filled a 60-second film so,
     no gap over 2.4 seconds). Record the final length in `narrator.trackSeconds`.
  3. Place it on the film: it may start after a lead of about a second, so the hook's action lands first; a line that names a new
     place or time starts inside that place's clip; a pause may be lengthened at a cut.
  4. Take its word times with faster-whisper (`clips.md`, Order of work), set every narration line's `startSeconds` from them, fit the
     clip plan to the track, and run `checks.py script`, `plan` and `effects` again. A sung track is checked alone, before mixing,
     with the lyrics passed to faster-whisper as its `initial_prompt`; a near-match of a sung word passes.
  5. At assembly the track goes over the joined film, music under both (a score under a narration about 10 LU under the narration
     track: three films so heard every word, 122-123 of 122-123), and the clips' own sound under it at its own level:
     clips come back 17-27 LU under a song (five measured), and at their own level every sung word still read and the mix
     measured the same, while one film that turned them down to a fifth was left silent between its sung phrases. Under a song
     with a band, a clip's own sound is kept only in the spans whose beats ask for a sound (a laugh, a gasp, a click) and muted
     elsewhere (`assemble.py join --mute`): kept whole, three of one film's eight clips carried a score of their own under the
     song, one in another key; kept so, no score was left and no span fell silent (measured).
- **The narrator on screen:** a clip in which the narrator speaks a narration or sung line on camera gets that line's part of the track
  as an audio reference (the clip entry's `track`, `clips.md`), cut to start on its first word, and lip-syncs it in the same voice. It
  re-performs the part with its own timing (up to 1.1 seconds off the track), so at assembly that clip keeps its own sound for its
  length and the track is muted under it. The track is the narrator's voice: when the narrator also has `dialogue` lines, their voice
  sample is cut from the track (`clips.md`, Voices).
- **Silent clips:** a clip with no on-screen line carries "The characters act and react without speaking; no voice-over, no
  narration." and none of the template's sentences about mouths and voices. Check it with the voice-activity detector (`SKILL.md`,
  step 6): a voiced span that came back is muted at assembly, only that span; a gasp or laugh the prompt asked for stays. A clip that
  came back with music (one returned a score in another key) has it muted under the track.
- **Short films** (45 seconds or less): the opening and its promise, then two or three scenes in order; the jump back may be told by
  the narration alone, without a scene of its own, and the pivot line may go. A song of 45 seconds or less is two couplets: the worst
  moment and the promise, then the turn and the win.

## Storytime (`storytime`)

- **Default look:** none of its own: the request's template, `live action` when it names none.
- **Script:**
  - The protagonist tells their own story to the viewer, first person, past tense, while the scenes play: the cast act and react
    without talking. The narrator may also talk straight into the lens (the `phone` selfie line).
  - Opening: the narration's first two to four sentences state the worst moment over the image of it: who did what to the
    protagonist, ages and counts as numbers; they end on a promise that it turned, without saying how.
  - Pivot: one line turns back to the beginning. When the worst moment is the first event of the story, open on it and run forward,
    with no pivot.
  - Then the story runs in order from weeks or months before; each time jump is named by the narration as a time phrase and falls at
    a cut. The retelling reaches the opening moment again and goes on to the ending.
  - Time and places (`script-format.md`, Length and skeleton): one jump back after the opening, forward jumps at cuts, and up to four
    places at any length.
  - Lines are spoken American, 3 to 20 words, numbers written as words, two facts at most per sentence. The film
    carries 160-175 narration words a minute (a 30-second film 80-87): at rate 30, 141 words left 4-9 seconds of a 60-second film
    without a voice, 7 of them at the climax, and 172 filled it after step 2's pause shortening. A sparser voice the user asks for
    is theirs (`asked.wordsPerMinute`): each stretch without a word is a beat of its own in the screenplay, held by the action and
    the score, so the silence is planned rather than left by a short track.
  - An animal variant: the animal tells its owner ("you") what is wrong, first person, its mouth closed.
- **Sound:** one narration track in the protagonist's voice, close and dry, running across the cuts nearly without a pause unless
  the user asked for a sparser voice.

## Sung story (`song`)

- **Default look:** `feature-3d`.
- **Script:**
  - Storytime set to music: the protagonist sings their own story over acted scenes, with the `storytime` structure, time and places.
  - Lyrics: rhymed couplets, each line one sung phrase of 8 to 11 words, the two lines of a couplet of equal length, plain American
    speech with contractions, ages, counts and names in the lines as in speech. Sung slowly with held notes (the only way it really
    sings) `seed_audio` sings about 80-100 words a minute: its film carries 60-100 sung words a minute (a 30-second film 30-50).
    `elevenlabs_music_v2` at 76 BPM sang a line every 6.0-6.5 seconds, 102-111 words a minute (seven takes): its film carries
    85-110, about (<the film's seconds> - 8) / 6.3 lines, rounded down; an odd count ends on one closing line after the last
    couplet (the product's line in an ad): rounded up to 14, a 90-second ad came out 96 seconds, and 13 came out 90.0. Lyrics written at the slower rate left two films' songs 24 and 46
    seconds short.
  - The lyrics are written to the film's length, never fitted after: once the song is made, the film's length is the song's. One
    166-second song's 22 lines did not fit 152 seconds without speeding it up, and sped up its lines slid across the planned cuts;
    the film went back to 166. A shorter film gets fewer lines before the song is made.
  - While a line is sung, the picture shows what it says: `checks.py clip` prints each line's window in the clip's own seconds, to
    write the shots against. A verse about one moment of the story played over a product insert
    after its clip was refused, and the song promised a scene the film never showed: a refused clip's beat is staged again another
    way (`models.md`, When a clip is refused), never covered with something else.
  - The singer does not mouth the narration: the face acts the moment while the song plays. A line sung on screen (the singer, or
    another character whose quoted words are sung) is lip-synced from its part of the song.
- **Video words:** for a lip-synced line, "@Audio1 is <name>'s singing voice. <name> sings exactly the words and melody of @Audio1,
  lip-synced from the first frame, <her/his> mouth shaping every sung word: "<the lyric>". Sound: only the singing of @Audio1, no
  other voice, no instruments."
- **Sound:**
  - One song for the whole film, made first, and the picture cut to it. A film with no lip-synced line makes it with
    `elevenlabs_music_v2`, a band and one singer (below). Its track has no separate voice to lip-sync to, so a film with
    lip-synced lines makes its song with `seed_audio`, a cappella, music going under it at assembly: the direction "(singing a slow
    folk melody, long held notes on every line, slow tempo)" sings; "quick steady tempo, short notes" came back a spoken chant.
    `seed_audio` holds neither a length nor a tune past a short song: asked to sing 166 seconds of lyrics, it read them in 104.6.
  - **The song with ElevenLabs** (`elevenlabs_music_v2` with lyrics, `models.md`):
    - It returns the length asked (every take came back 0.03-0.05 seconds over), but its first sung word does not always come at once, though the prompt asks for it: within 0.6 seconds in 10 of 19 takes, within 2 seconds in 15, after an intro of 3-7 seconds in 4 (first parts: 5 of 8 within 0.6 seconds, the latest 3.7). Whisper puts the first word at 0.00 when the voice comes within 1.4 seconds (27 of 27 takes) and 0.4-1.6 seconds early after a longer intro (10 of 10), so read where the voice starts on a spectrogram of the take before planning the film's length on it: the first part plays from its own first second, and its intro opens the film. Then it plays an outro of 7-12 seconds after the last word. `suno_music`, used before it, opened every
      song on 12-15 seconds of intro whatever its prompt asked, and cut a 90-second song's last line.
    - The song is made in parts of about six lines, about 45 seconds each: its length its lines' singing plus about 8 seconds of
      outro (six lines of 8-11 words sang in 37 of 45 seconds at 76 BPM). Four 45-second takes sang every word, while one 90-second
      and two 108-second takes each lost or changed words (one dropped half of two lines). One take a part, all parts in one call;
      only a part that lost or changed a word is made again (step 1 below).
    - `narrator.voiceId` is "elevenlabs_music_v2", and `narrator.voice` the singer's words in its prompt.
  - **One prompt for every part, word for word; only the lyrics change.** Nothing else ties the takes together (no seed, no voice
    choice, no reference), so the prompt is what keeps the style: four takes of one prompt kept one genre, band and singer and the
    same 76 BPM, while the key it named held in one take of four (a different key at a seam passes as a change of key). Write it:
    "A <genre and mood> in <key> at <tempo> BPM in <metre>: <the instruments>. One <female | male> lead vocal, <register and
    timbre>, <age>, close-miked, no backing vocals. <She | He> sings the lyrics word for word, clearly, starting within the first
    two seconds. Ends on a held final chord."
    - Every measurable thing is written as a value (the tempo in BPM, the metre, one named set of instruments, one lead voice by
      gender, register, timbre and age), never as a mood word alone: a value is what the takes have in common.
    - Describe the sound; never name an artist, song, film or series: a name fails the job.
    - Write the prompt once into `song-prompt.txt`. Every part's call sends it word for word with that part's lyrics, plain text,
      one sung line a line: the sung lines of script.json after the part before it. Sent without its lyrics, four takes of one
      film sang words of their own.
  - **The song sets the timing.** The lyrics are written with the script, but every sung line's times, the clip plan and its cuts
    come from the made song, before any clip:
    1. Run `python3 "${HF_WORKFLOWS}/drama-ads/scripts/song_times.py"` on each part's take, its lines given (`--lines <first>-<last> --dry-run`; its usage gives the
       faster-whisper command, the part's lyrics passed as `initial_prompt`: without them a name the lyrics coin came back as
       other words). It lists every lyric word it did not hear, and every line it could not time (whisper's 30-second window glued its words: time
       that line again as step 3 does, in a window cut in the gaps around it); a clean take lists none. Only a listed line is cut from the take
       and transcribed again alone: whisper glues junk to words at the edges of its segments, and a quiet first word that scored
       0.09-0.25 in the whole take was there. A part that really lost or changed a word is made again.
    2. Join the parts: each part cut one second after its last word; the next one starting at `max(<its first word> - 1.0,
       <its first sound> - 0.75)` seconds (a negative start is that much silence before it), joined with a 0.8-second crossfade on
       `ipar` curves, `ffmpeg -i p1.mp3 -i p2.mp3 -filter_complex "[0]atrim=0:<its last word + 1>,asetpts=PTS-STARTPTS[a];[1]atrim=start=<the start, or 0>,asetpts=PTS-STARTPTS,adelay=<minus the start in milliseconds, or 0>:all=1[b];[a][b]acrossfade=d=0.8:c1=ipar:c2=ipar" song.wav`
       (each further part joined the same way). Its first sound is the first 50-millisecond window from `max(0, <its first word>
       - 1.0)`whose level is at least its median window's minus 20 dB:`ffmpeg -i p2.mp3 -af "pan=mono|c0=0.5*c0+0.5*c1,aresample=8000,asetnsamples=n=400:p=0,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null -`.
         A second part's 10.7-second intro, joined whole, left 11 seconds without a word in the middle of one film; padded to a
         second before a first word at 0, under a 0.8-second crossfade, 8 of 10 joins had 0.25-0.6 seconds of digital silence
         and one film's song restarted 37 dB louder; this way four fresh songs' joins, chosen on six others before they were
         made, never fell under -40 dB and kept the first word within 0.4 dB. The last part's outro is cut on a whole second within 8 seconds of the last word and faded
         out. The joined song's length, measured with `ffprobe`, is the film's `durationSeconds`: nothing is stretched.
    3. Time the lines on the joined song in windows under 30 seconds, each cut in the middle of a gap between two lines: transcribe
       each window as in step 1 (its own lines as `initial_prompt`), add the window's start to its word times, then run
       `python3 "${HF_WORKFLOWS}/drama-ads/scripts/song_times.py"` without `--lines` on all the words, which writes each sung line's `startSeconds` (its first word)
       and `endSeconds` (its last word's end). One pass over the whole song glued words at 29.98 seconds, whisper's window edge, in
       6 of 6 songs and put a line up to 17 seconds off; in windows none glued and the worst line was a second off. A window's first
       line is the least exact: whisper pins its first word to the cut.
    4. Set the clips on the story first, then on the song: clips of 8-15 seconds in the story's rhythm, each starting between two
       sung lines or on a line's first word, never inside a line (six of thirteen cuts in one film fell mid-phrase). A cut need not
       fall on a whole second: a clip's `start` and `end` take the song's seconds (the screenplay marker writes them the same way,
       `(0:18.4–0:31.0)`), and a clip whose window is not a whole number of seconds is made at the next whole second and trimmed to
       it (`generated` and `kept`, `clips.md`). Windows rounded to whole seconds left one film only the song's widest pauses to cut
       at, and a 21-second clip ran into a 7-second one.
    5. Run `checks.py script` again: with `narrator.trackSeconds` set it refuses a sung line without its times, a longer intro
       or tail, a cut inside a line, and a clip over 15 seconds that a gap between two lines could split.
  - Every clip is made with its sound on, its own voices kept out by its prompt and muted where they come back (Silent clips): its
    room tone and effects go under the song (Narration, step 5). Made silent, so that nobody would sing along, one film's clips
    left nothing between its sung phrases.
  - A lip-synced clip gets its part of the song (The narrator on screen). The clip re-performs the part in the same voice and
    melody, 0.1-0.3 seconds ahead of it: keep that clip's own sound in the join and lay the song over the other clips.
- **Pitfalls:** a clip given only the lyric sings it in a voice and tune of its own, so two such clips are two singers and two songs:
  make the song first and pass its parts. A sung line fills its clip: time it from the song's word times.

## Inside the body (`inside-body`)

What happens inside one body, in one of two ways:

- **Body cast** (default look `ink-cartoon`): cells, organs and what blocks them are the characters, with faces, arms and gloves, and
  talk to each other inside the body about the person they live in. It is `dialogue` in a body: the body's owner may stay off screen,
  and the stakes are what happens to them, shown inside the body.
- **Body cast** writing: the format's own premise and world (cells inside a body) do not count against the COPYRIGHT CHECK; vary the
  leads' jobs, their names and the spike.
- **Body diary** (default look `hyperreal-3d`): a narrator who is nobody on screen talks to "you" in the second person and the
  present tense; a stand-in figure (an anatomical figure whose skeleton and organs show) plays "you". It wears everyday clothes, and
  only its head, neck and hands and the part of the body its organ lives in are a clear, glass-like shell, the skeleton and organs
  showing through ("in <everyday clothes>; its head, neck and hands a clear, glass-like shell, <the skeleton> showing faintly
  through"): a clear shell around the whole body, head to feet, was refused `nsfw` on 9 of 23 sheets; dressed so, on 0 of 21, and
  every dressed sheet still read as a see-through body (12 of 12, judged blind). A clear garment over a clear torso gave a
  figure in everyday clothes, clear only at the torso. The organs inside are written as "soft, pale pink and peach organs" of an anatomical model, matte and slightly
  see-through, never wet or bloody: the anatomical-model words held through a whole film, but "soft pink and red" came out
  saturated maroon in close-ups. A sick organ is written by its size and colour, matte ("<its size>, <its colour>, <its shape>, matte"): written
  glossy, it came out full-size and healthy. A change that differs between an organ's front and back (or top and bottom) is shown
  in a three-quarter or profile shot that sees that axis ("three-quarter on <the figure>, its face turned toward the <side> edge"),
  never straight on: straight on, an organ's front came back as one side half, on the sheet and in the clip (two runs, 3 of
  3 takes); in three-quarter, at the front in 3 of 3 (judged blind).
  - Its opponent is the habit: the old habit's pull shown as a thing in frame, against the thing of the new habit. It stands in
    for the second character of the script review's questions 1 and 2, FRICTION's two opponents and `plan.json`'s opposing character.
  - One visible change on an organ per day, each an effect in `effects.json`, in place of ONE VISIBLE EFFECT PER ACT.
  - The narration is the Narration section's, with `"speaker": "narrator"` and the cue `NARRATOR (NARRATION)`; the cast may be that one
    figure.
  - It opens on the figure in the problem (the symptom shown on screen) with the question over it: what happens if it does one thing
    every day for a set number of days. This hook replaces the hook's conflict between two characters. Then the narration counts the
    days aloud ("Day <n>."). Each day is one short scene: one action of the figure and the change inside it, shown on
    the organ that changes (an effect in `effects.json`). Days pass inside clips, named by the narration, in place of time jumps only at clip boundaries. A clip that opens on a new day ("day <n>" or "night <n>" in its stateIn) is a cut to a new time: it opens wide or medium-wide, or on the close insert of the organ's after-state that its form sheet carries (`checks.py clip` refuses it otherwise).
  - 160-175 narration words a minute (or the asked pace, `asked.wordsPerMinute`), lines of 2 to 20 words.
