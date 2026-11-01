# Window pass-through prompts

From the source guide (written for Kling 2.5 Turbo in Higgsfield with Image 1 + Image 2). For Nexabot
`sfv` there is no Image 2, so every "Image 2" becomes **the destination, described in words**
(`<DESTINATION>`). Keep the guide's wording; add the camera path, destination, AUDIO and AVOID.

## Master prompt (the guide's exact prompt, adapted)

```
Create a fluid, cinematic transition that seamlessly connects this opening image to <DESTINATION_SHORT>.

Begin with the camera fully immersed within the opening image, then move it along a believable,
continuous motion path that naturally guides the viewer toward the transition. Preserve consistent
lighting, scale, depth, and perspective throughout so the movement feels like a real physical camera
traveling through space.

Allow colors, shadows, textures, and environmental details to blend smoothly, with objects and
surfaces transforming subtly and realistically over time. The transition should feel like a single
uninterrupted shot rather than a visual effect.

Maintain a high-end cinematic look that is grounded and realistic, emphasizing physically plausible
camera motion, steady depth and spatial continuity, natural scene-driven lighting, and sharp
high-resolution surface detail.

The objective is to make the transition imperceptible, as if both places exist within the same
evolving environment and the camera is simply moving forward through it.

CAMERA PATH: <CAMERA_PATH>
DESTINATION: <DESTINATION>

AUDIO: soft ambient sound of the first place, a rising airy whoosh as the camera passes through the
glass, then the ambient sound of the destination. No music, no voices.
AVOID: cuts, fades, dissolves, split screen, morphing faces, warped architecture, text, captions,
letters, numbers, logos, watermarks, the camera stopping at the glass, reverse motion.
```

- `<CAMERA_PATH>` - the guide's own example: "Zoom into the ferris wheel into one of the pods through
  the glass and into the destination." Name the opening and where it is in frame, e.g. "Push steadily
  forward toward the lit window on the third floor at the centre of the frame, pass through the glass
  without stopping, and emerge inside the destination."
- `<DESTINATION>` - 2–4 sentences: place, time of day, light direction and colour, palette, 3–4 key
  objects, camera height on arrival, what moves there (steam, people walking, curtains, rain). From
  the user's Image 2 if they gave one. No brand names or on-screen text.
- `<DESTINATION_SHORT>` - 3–6 words ("a warm candlelit café interior").

## Variations (swap the CAMERA PATH line; the rest stays)

| Variation | Camera path line |
|---|---|
| Generic window pass-through | Start inside the opening image and move the camera forward through a window, opening, or transparent surface into the destination. Maintain consistent lighting, scale, depth, and perspective so the transition feels physically real. |
| Architectural pass-through | Begin inside the opening image and guide the camera forward through an architectural element such as a window, doorway, or glass structure. Blend textures, lighting, and shadows naturally so the first place evolves smoothly into the destination. |
| Object-based pass-through | Start within the opening image and move the camera toward a foreground object. Transition through the surface or opening of that object and emerge naturally into the destination while preserving realistic camera motion. |
| Environmental flow | A single-shot cinematic movement that carries the camera from the opening image into the destination through the environment itself, allowing surfaces, colors, and depth to shift gradually. |
| Forward motion reveal | Begin fully inside the opening image and move the camera steadily forward. Let the first place transform naturally into the destination as if both exist in the same physical space. |
| Glass or reflection pass | Guide the camera from the opening image through glass, reflection, or transparent material, blending highlights and textures until the camera emerges into the destination. |
| Cinematic push-in | A slow controlled push-in from the opening image, allowing the environment to reshape and resolve into the destination while maintaining depth and realism. |
| Seamless spatial merge | The first place and the destination merge spatially through continuous camera motion with no visible cut. |
| Scene continuation | Treat the first place and the destination as consecutive moments in the same world, moving the camera forward into the destination with consistent lighting and perspective. |
| Universal pass-through | Begin inside the opening image and move the camera through any natural opening or focal point into the destination. The transition should feel invisible and physically plausible. |

Pick by Image 1: a clear window/glass → Generic, Architectural or Glass; a hero object (bottle,
phone, eye, lens) → Object-based; no opening → Forward motion reveal or Cinematic push-in.

## Start-frame image prompt (when the user has no Image 1)

```
<scene>, photorealistic cinematic still, <time of day and light>, a clearly visible <opening> as the
focal point near the centre of the frame, glass reflecting soft light with a hint of a warm interior
behind it, deep perspective, 35mm lens, shallow haze, rich detail, no text, no signs, no logos, no people facing camera
```
Put the unique scene words first (Nexabot de-duplicates prompts that start the same).
