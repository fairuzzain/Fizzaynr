# Editorial Documentary Animation Playbook
## Deep Mechanics for Gemini Omni Flash & Nano Banana Pro

This playbook provides the underlying cinematography, visual design rules, prompt formulas, and technical execution patterns for generating archival, documentary-style editorial motion sequences.

---

## 1. Visual Philosophy: Anchored Continuity vs. Generative Chaos

Traditional documentary motion graphics (e.g., Vox Explainers, Johnny Harris, Netflix docuseries, archival brand retrospectives) keep viewers engaged by grounding complex historical or technical narratives in **anchored visual spaces**.

When generating AI video without an anchor:
- The background constantly warps and shifts.
- Text characters morph into unreadable hieroglyphs.
- Cuts feel random and disconnected.

### The Anchor-and-Layer Principle
```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: ANCHOR STILL (Nano Banana Pro / Gemini 3 Pro Image) │
│ - Locked physical surfaces (wall, desk, workshop, floor)   │
│ - Baked surface typography (stencils, engraved plates)     │
│ - 40% empty central negative space                          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Upload as First Frame
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: DYNAMIC LAYERING & MOTION (Gemini Omni 1.1 Flash)    │
│ - 2.5D archival cutouts pop in with spring physics          │
│ - Rack-focus f/2.8 bokeh blurs background anchor            │
│ - Glowing 3D isometric wireframes extrude from flat surface │
│ - Physical whip-tilts and match-cuts bridge eras             │
└─────────────────────────────────────────────────────────────┘
```

By separating **layout design** from **motion choreography**, you eliminate 95% of AI video artifacts.

---

## 2. Anchor Still Construction in Nano Banana Pro

Anchor stills must be engineered specifically for subsequent video manipulation.

### A. Central Negative Space Rule
Every documentary anchor still must allocate its visual weight across three horizontal zones:
- **Left Third (25–30%)**: Secondary historical props (test gear, tools, archive folders, books, machinery).
- **Center Third (40–50%)**: **Clean, uncluttered negative space**. Neutral textured surface (concrete wall, oak table, drafting mat, cutting board). This is where foreground cutouts, Polaroids, and 3D wireframe extrusions will manifest.
- **Right Third (25–30%)**: Balancing props (cables, lenses, desk lamps, measurement instruments).

### B. Surface Typography Baking
Video diffusion models struggle to generate razor-sharp letterforms in motion. Nano Banana Pro (Gemini 3 Pro Image), however, renders immaculate static typography if prompted properly:
- **Stencil on concrete/brick**: `"bold distressed red stencil text reads 'OCT' above yellow highlight text '1952'"`
- **Serif on cutting mat**: `"centered blue architectural cutting mat with crisp white serif title 'ORIN' in the middle"`
- **Engraved brass plate**: `"polished brass plaque bolted to dark mahogany, laser-engraved with 'PATENT NO. 488,102'"`
- **Stamped industrial steel**: `"matte cast-iron chassis stamped with raised relief lettering 'SERIAL 09'"`

---

## 3. The 5-Part Omni Motion Formula

When animating an anchor still in Gemini Omni 1.1 Flash, structure every prompt using this 5-part syntax:

```
[1. SHOT FRAMING & MOTION] + [2. STYLE] + [3. LIGHTING] + [4. LOCATION] + [5. ACTION & TIMING]
```

### Element Breakdown
1. **Shot Framing & Motion**: Camera distance, lens focal length, exact camera trajectory (slow push-in, top-down locked, downward whip-tilt, center snap-zoom).
2. **Style**: Documentary motion graphics, archival editorial retrospective, tactile 2.5D paper cutout aesthetic, technical isometric blueprint.
3. **Lighting**: Warm tungsten key light, moody directional archival light, cinematic f/2.8 shallow depth of field, neon edge glow.
4. **Location**: Specific environment anchored from the previous still (1950s electronics workshop, architect's drafting table, modern cleanroom).
5. **Action & Timing**: What pops in, exactly when, with what physics, and how the background reacts:
   - Timestamp markers: `"At 1.5 seconds..."`
   - Spatial coordinates: `"top left, tilted -8 degrees"`, `"bottom right, tilted +6 degrees"`
   - Motion physics: `"snappy spring bounce"`, `"settles with subtle overshoot"`, `"racks focus into soft f/2.8 bokeh"`

---

## 4. Multi-Turn Conversational Refinement

Gemini Omni 1.1 Flash retains **stateful conversational memory**. Never re-paste the entire prompt when refining a scene. Re-pasting triggers re-generation from scratch, causing the layout and faces to drift.

### The Delta Edit Pattern
Start follow-up prompts with:
```
"Edit this keeping everything the same. [Specify exact delta change]."
```

### Common Delta Edits
- **Depth of Field Adjustment**:
  `"Keep everything the same. Increase the background blur when the two Polaroid frames appear so the background turns into a creamier f/2.0 bokeh."`
- **Physics Tuning**:
  `"Keep everything the same. Make the photo pop-in snappier with a tighter spring bounce upon landing."`
- **Audio Synchronization**:
  `"Keep everything the same. Add a crisp paper-slide sound effect synced to the exact frame each photo lands."`
- **Lighting Accentuation**:
  `"Keep everything the same. Increase the glow intensity of the white 3D wireframe lines by 20%."`

---

## 5. First + Last Frame Transition Mechanics

Gemini Omni 1.1 Flash excels at interpolating between two distinct visual anchors to create seamless continuous shots without cuts.

### The Continuity Directive (Oner Lock)
Always append these exact keywords to First + Last Frame prompts:
```
"One continuous shot, oner, no scene cuts, physical camera whip-tilt, seamless camera trajectory."
```
Without this directive, the model may generate a cross-dissolve, fade to black, or abrupt cut.

### Transition Archetypes

#### Archetype 1: The Fast Whip-Tilt (Wall to Desk)
- **First Frame**: Vertical wall with historical artifact / date stencil.
- **Last Frame**: Flat-lay top-down workbench / blueprint mat.
- **Prompt Logic**: Direct a rapid downward tilt of the camera head while pivoting on its axis, landing precisely on the top-down angle of the second frame.

#### Archetype 2: The Logo Match-Cut Punch-In (Blueprint to Modern Store)
- **First Frame**: Top-down technical mat with centered logo/title.
- **Last Frame**: Symmetrical modern storefront / high-tech facility with the same brand logo centered in the same screen coordinates.
- **Prompt Logic**: Direct an aggressive forward camera zoom driving straight through the center letters of the logo, breaking into the bright modern space as the letters pass beyond the lens edges.

#### Archetype 3: The 3D Wireframe Extrusion (2D Mat to 3D Device)
- **Starting State**: Flat 2D vector blueprint on drafting desk.
- **Ending State**: Volumetric 3D product model floating above desk.
- **Prompt Logic**: Direct glowing white vector linework to lift vertically off the paper surface, drawing geometric wireframe silhouettes that fill with solid material.

---

## 6. Audio Design & Foley Architecture

Editorial documentary animation relies heavily on tactile, physical sound design to ground AI visuals in reality.

### Sound Cue Mapping
| Visual Beat | Primary Sound Design Cue | Frequency Range |
|---|---|---|
| **Polaroid / Cutout Pop-in** | Quick crisp paper flick, cardboard slap, dry shutter click | Mid-high (1.5 kHz – 4 kHz) |
| **Rack-Focus Blur** | Low-frequency sub whoosh, gentle atmospheric air shift | Low (80 Hz – 250 Hz) |
| **Camera Whip-Tilt** | Fast directional air tear, rapid whoosh with high-frequency tail | Full spectrum (120 Hz – 8 kHz) |
| **3D Wireframe Extrusion** | Clean synthetic glass chime, subtle electrical hum, laser draw | High (3 kHz – 10 kHz) |
| **Match-Cut Zoom** | Heavy cinematic riser ending in an open room air suck | Sweep (60 Hz → 6 kHz) |
| **Product Hero Turntable** | Precision mechanical ratchet, cassette tape head click, motor whir | Mid (500 Hz – 2.5 kHz) |
