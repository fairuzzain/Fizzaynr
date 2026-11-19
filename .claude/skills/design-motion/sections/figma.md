<!-- AUTO-GENERATED from figma.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->
## Figma source (optional, needs a token)

Use this path only when `FIGMA_TOKEN` (or `FIGMA_ACCESS_TOKEN`) is set and the source is a Figma link with a node id. Fill `<figma-file-key>` and `<figma-node-id>` only with values matching `^[A-Za-z0-9]+$` and `^[0-9]+[:-][0-9]+$`; anything else is not a Figma link. The token is a secret: pass it only as a header from the environment, never print it, echo it, write it to a file, or put it in chat or a commit.

```bash
_FT="${FIGMA_TOKEN:-$FIGMA_ACCESS_TOKEN}"
printf 'X-Figma-Token: %s\n' "$_FT" | curl -fsS -H @- "https://api.figma.com/v1/files/<figma-file-key>/nodes?ids=<figma-node-id>&geometry=paths" -o "<motion-dir>/figma-nodes.json"
printf 'X-Figma-Token: %s\n' "$_FT" | curl -fsS -H @- "https://api.figma.com/v1/images/<figma-file-key>?ids=<figma-node-id>&format=png&scale=2" -o "<motion-dir>/figma-ref.json"
```

The nodes response gives the tree, bounds, fills, effects and radii; the images response gives a URL for the **reference frame**, saved as `reference.png`. Every layer position is its absolute bounds minus the frame's origin. Figma's image CDN sometimes resets connections: retry each download and check each PNG's size before using it.

### Layer export

Export every element that will move as its own PNG at 3x through `/v1/images`, 20 to 25 ids per call. Placement:

| Case | Do |
|---|---|
| PNG size equals `absoluteRenderBounds` (text always does) | Place at the render bounds |
| PNG larger than the bounds, even overhang (a clipped effect) | `x = bbox.x − (pngW − bbox.w) / 2`; `y` from `renderBounds.y` unless the top was clipped, then from the effect radius and offset |
| Uneven overhang (an arrowhead, one square cap) | Bounds of `strokeGeometry` or `fillGeometry` from `geometry=paths` |
| Rotated vectors with large blur, arcs, donuts, partial ellipses | `use_absolute_bounds=true`, placed at the bounding box; blobs can be 1x |
| Zero-width or zero-height stroked vectors | Without `use_absolute_bounds` (it returns null for them) |
| Mask group with blurred content | Anchor on the edge that was not clipped |
| Pattern far larger than its surface | `use_absolute_bounds=true`, then crop to the surface |
| Instance children (`I12:34;56:78`) returning null | Export the parent instance |
| A photo baked into a larger layer | Export the photo node too; cover the baked copy with a skeleton and put the photo above for the `photo` resolve |

- Text stays an exported layer in a showcase; retyping it changes kerning and line metrics.
- Keep Figma's z order, static layers included. Frame strokes usually draw above children: render a card's stroke as an overlay above its clipped content.
- A container whose children move separately is rebuilt in CSS from the node data (fills, per-corner radii, inside strokes including `individualStrokeWeights`, effects), with each child exported alone; exporting the container bakes its children in.
- A Figma drop shadow with blur R is `box-shadow` blur R on one element, or `filter: drop-shadow()` blur about R/2 on a group. A shadow on joined surfaces is the shadow of their union: one static container with `drop-shadow`, never per-element shadows that darken the overlaps.
- The background is the original image fill (`GET /v1/files/:key/images`), with the fill's scale mode and `imageTransform` applied in CSS.
- Skip hidden layers and layers buried under opaque shapes.

**Drawing a line on.** Figma outlines strokes into filled shapes, so write the centreline yourself from `strokeGeometry` (halfway across the stroke; a rounded corner's centreline radius is the outline's inner radius plus half the stroke) and use it as a mask over the exported PNG:

```html
<svg class="ly" viewBox="0 0 1440 990" style="left:0;top:0;width:1440px;height:990px">
  <mask id="draw1"><path d="M193 832 V700 A45 45 0 0 1 238 655 H380" fill="none" stroke="#fff" stroke-width="8"
    pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></mask>
  <image href="data:image/png;base64,..." x="192" y="653" width="190" height="181" mask="url(#draw1)"/>
</svg>
```

Animate `stroke-dashoffset` from 1 to 0 on the JS clock; pulses along the line read positions with `getPointAtLength` on the same path.

Adapted from Elaya's [ai-design-skills](https://github.com/elayadesign/ai-design-skills) design-to-motion (MIT, © 2026 Elaya), rewritten for gstack. See NOTICE.md.
