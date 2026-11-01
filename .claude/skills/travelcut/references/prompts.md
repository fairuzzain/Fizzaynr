# TravelCut prompts

## Clip prompt (one per shot, Nexabot `sfv`, the crop is the start frame)

```text
A cinematic travel shot built from the provided start image.

START IMAGE
The first frame and the whole place: [what is visible — subject, setting, light, colours].

ACTION
[What moves and when, in plain physical terms; the key action happens within the first 4 seconds.]
The camera starts exactly on the start image and [one motivated camera move: slow push in / gentle
rise / lateral track / slow pull back / slight orbit].

LOOK
A premium travel film made from a real photo: the same colours, light and white balance as the start
image, real textures, natural motion blur that matches real speed. Every camera move is physical and
motivated.

LOCKS
The first frame is exactly the start image. One continuous shot. [Keep every person, outfit and the
whole scene exactly as in the start frame.] [Correct anatomy: two hands, five fingers; animals with
real anatomy.] [Buildings, signs and landscape stay in place.] No text, no captions, no logos.

AUDIO
[Natural sounds of this place.] Every camera movement is completely silent. No music.
```

Rules
- Write positively (what should happen), each element once, one camera move per clip, vary moves
  across the film (push, rise, track, pull back, orbit, static with subject motion).
- Only motion the photo supports: water, wind in hair/fabric/leaves, steam, flags, clouds, light
  shifting, a crowd walking, a natural step or head turn, a balloon drifting.
- No names of real people or brands; describe what is visible.
- Safety filter (learned on recap-reel, Oct 2026): the words "face" and "hijab" on a photo of real
  people tripped it; "Keep every person, outfit and the whole scene exactly as in the start frame"
  passed. Rejections are refunded; reword neutrally and retry once.
- Text in the photo (signs, menus) can melt: lock it ("signs stay in place") and check the sheet;
  if it garbles, use the frames before it or choose a crop without the sign.

### Camera move by job
| job | move |
|---|---|
| hook | fast-reading event: a push in toward the subject, or subject motion starting at frame 1 |
| orientation | slow rise or pull back revealing the place |
| human moment | gentle push in, subject's own small motion (a turn, a step, hair in wind) |
| detail | static or tiny push, tactile motion (steam, pouring, fingers) |
| spectacle | slow orbit or lateral track with parallax |
| breath | near-static, only nature moves (water, clouds) |
| ending | pull back, or a look to camera |

## Music prompt (Nexabot `music`)

```text
Original instrumental for a [feel] travel film about [place type / mood, no names of artists or works].
[Genre], about [tempo] BPM, [2-4 instruments]. Starts quiet and spacious for about [N] seconds, then
a clear lift into a full, driving groove with a strong downbeat, steady energy to the end. No vocals.
```
Feels: energetic beat-cut → 118–128 BPM, punchy drums, plucked synth, bass;
cinematic calm → 80–95 BPM, piano, strings, soft pulse; warm nostalgic → 90–100 BPM, warm guitar,
light percussion, analog pads.
