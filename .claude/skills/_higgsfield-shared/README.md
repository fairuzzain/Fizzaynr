# Higgsfield skills — full extract

Extracted from the Higgsfield MCP connector on 2026-11-09.

Each folder holds that workflow's `SKILL.md` exactly as the connector served it (frontmatter + body).
Two boilerplate sections that repeat at the end of nearly every skill are saved once in `_shared/`:

- `_shared/unlimited-generations-use_unlim.md`: the free-trial "unlim" rules (Katana has its own non-interactive version inline)
- `_shared/bundled-scripts-note.md`: how to run the scripts preinstalled at `$HF_WORKFLOWS/<workflow>/scripts/` in the Higgsfield sandbox

Not included: the `references/*.md` files each skill points to (fetched on demand with `get_workflow_bundle_file`) and the
Python/JS helper scripts (they exist only inside Higgsfield's sandbox).

## 1. Workflow skills (18)

| Skill | Version | What it does |
| --- | --- | --- |
| ad-multiplier | 1.5 | Many ad versions from one 4–30 s video: swap people/products/backgrounds (Edit), or re-shoot for a new market/language (Recreate) |
| ads-studio | 1.2 | Static ad creatives (Meta/IG) with copy + pictures from a brand website, product page, photo or prompt |
| brand-asset-creation | 1.1 | Logos, palettes, typography, brand kits, brandbooks, decks, mockups, packaging, signage, social graphics |
| character-sheet | 1.0 | Consistent character/model sheets (split-screen, turnaround, expression) with an anti-AI realism engine |
| color-grade | — | Script bundle behind `/color-grade` (match reference stills or 20 film looks, LUT export) |
| drama-ads | 1.0 | Micro-drama story ad film: script → characters → clips → assembled film, with approval stops |
| faceless-video | 2.4 | Narrated faceless channel videos: Explainer, History, Kids, Picture Story, Fairy Tale & Myth |
| katana | — | Remix a reference edit's visual language onto your subject, or edit supplied footage to a brief |
| manga-engine | 1.0 | Engine behind `/manga`: series state, script checks, page layouts and prompts for manga/comics |
| narration | 1.1 | Narration fitted to fixed video windows, a continuous long read, or your photo as on-screen narrator |
| product-photoshoot | 1.0 | Packshots, lifestyle, pins, hero banners, carousels, ad packs, virtual try-on, conceptual, restyle |
| reel-effects | 4.1 | Fixed effects on talking-head reels: text-behind, tier-list, freeze-frame, glass-graph, captions, grade-wipe |
| shorts-studio | — | Scripts behind `/shorts` (AI presenter reels up to ~2 min) |
| thumbnail-generation | 1.3 | YouTube/IG thumbnails: 16 frameworks, identity lock, 11 emotions, 4K render, text overlay |
| ugc-video | — | UGC videos: review, product voiceover, unboxing, try-on, tutorial, website tour |
| video-editing | 1.0 | Higgsedit (native CLI) edits and motion graphics: cuts, layouts, animated text, shaders |
| video-montage | — | Assemble clips, change soundtrack, transcribe and burn captions |
| website-builder-flow | 2026-07-25 | Build websites, Higgsfield apps or browser games, then deploy and publish |

## 2. Slash commands (via `get_preset_instructions`)

**Production:** /ads-studio · /build-ai-influencer · /content-factory (/what-if) · /drama-ads (/microdrama-ads) · /genjutsu ·
/manga (/webtoon, /comics) · /shorts (/ai-reels) · /3d-jutsu · /playable · /playable-ad · /color-grade

**Faceless styles:** /faceless-fairy-tale-myth · /faceless-hand-drawn · /faceless-mannequin · /faceless-paper-diorama ·
/faceless-pastel-flat-2d · /faceless-whiteboard-doodle · /stickman-explainer · /vox-mixed-media

**Talking-head reel effects:** /captions · /freeze-frame · /glass-graph · /grade-wipe · /over-the-shoulder · /text-behind · /tier-list

**UGC:** /ugc-flow · /physical-ugc-skill · /try-on-ugc-skill · /unboxing-ugc-skill

**Marketing:** /marketing · /marketing-adapt-video · /marketing-campaign-manager · /marketing-feedback-to-ads ·
/marketing-headline-variants · /marketing-hook-variants · /marketing-localize-ads · /marketing-research-to-ads · /marketing-resize-ads

**Adobe After Effects:** /2d-character · /illustration-animation · /kinetic-typography · /localization-motion · /logo-animation ·
/lyrics-animation · /motion-bundle · /paper-collage · /poster-animation · /presentation-animation · /saas-animation ·
/scribble-animation · /shot-cleanup · /shot-composer · /whiteboard-animation

**Blender:** /cartoon-shaders · /destruction-studio · /exploded-view · /scene-builder

**Other desktop apps:** /color-grading (DaVinci) · /image-fixer (Photoshop) · /vectorize (Illustrator) · /project-sorter (Premiere)

**Local integrations setup:** /use-after-effects · /use-blender · /use-davinci · /use-illustrator · /use-photoshop · /use-premiere ·
/use-touchdesigner · /use-video-editor

## 3. Recipe presets

**Product images:** /angles · /before-after · /benefits · /bundle · /care-guide · /color-pop · /fabric-wave · /feature-zoom · /flatlay ·
/gym-bag · /hero-shot · /how-it-works · /ice-capsule · /in-hand · /inside-pack · /kitchen-scene · /luxury · /main-benefit ·
/minimalist-white · /moodboard · /myth-fact · /new-drop · /on-desk · /pedestal-shot · /powder-cloud · /power-angle · /product-match ·
/quick-steps · /reel-cover · /retail-stack · /saveable-tip · /share-card · /shelf-ready · /signature-frame · /specs · /swipe-opener ·
/symmetry · /three-reasons · /travel-pack · /unboxing · /usage-guide · /vertical-hook · /water-splash · /weekend-carry · /whats-inside

**Product videos:** /crane-reveal · /detail-scan · /floating-roll · /half-turn · /impact · /label-trace · /light-sweep · /liquid-wrap ·
/macro-glide · /paint-wave · /product-spin · /pull-back · /push-in · /shadow-motion · /sunrise-pass · /texture-track · /topdown-dive · /whip-pan

**Halloween portrait videos:** /abandoned-carnival 🤡 · /alien-reveal 👽 · /blue-flame-skeleton 💀🔥 · /demon-awakening 😈 ·
/full-moon-werewolf 🐺 · /haunted-house-awakens 🎃🏚 · /haunted-mansion-ghost 👻 · /living-skeleton 💀 · /midnight-spell 🧙 ·
/pumpkin-monarch 🎃 · /rise-from-the-grave 🧟🪦 · /spider-throne 🕷 · /the-wrong-reflection 🕯 · /vampire-bat-swarm 🧛🦇 ·
/vampire-castle 🧛 · /witch-familiar 🧙🐈‍⬛ · /zombie-awakening 🧟

## 4. Katana edit presets (/katana/<slug>)

candy-pop · kinetic-tech-edit · daytona-drift · pop-cutout-fashion-edit · monolith · chrome-noir-style-edit · fw26-style-lookbook ·
aura-fast · neon-laser-motion-graphics-edit · track-day-showcase · pop-art-comic-edit · higgsfield-katana-kinetic-typography-edit ·
kinetic-graphic-photo-edit · swole-cinema-aesthetic · noir-crowned-fashion-montage · surreal-collage-vibe · high-octane-turbo-sprint ·
comic · monochrome-glitch-montage · perfume-commercial-style-edit · camera-shots · black-and-white-boxing-montage ·
silhouette-eyes-lips-beat-edit · neon-monolith · vintage-cinematic-rap-video · cinematic-noir-glitch-edit · scrapbook-fashion-montage ·
mentality · gritty-noir-cinematic-montage · y2k-sticker-scrapbook-edit · surreal-multi-hand-edit · fruiteger-aero ·
creative-collage-runway · outfit-check · newspaper-cover-fashion-edit · epic-rocker-vibes · monochrome · cinematic-glitch-action ·
creative-stylized-montage · clone-squad · face-edit-1 · gentleman-driver-style · dreamy-streetwear · futuristic-3d-motion-scan ·
color-palette-outfit-showcase · paper-cutout-fit-check · kpop-style-dance-montage · nocturne · superhero-beat-montage ·
parisian-luxury-vibe · tiger-eyes · urban-elf-aesthetic-edit · anime-concert-star · xerox-2 · painting-flow · purple-grunge-music-video ·
dramatic-melodrama-vibe · y2k-edit · edgy-streetstyle-montage · katana-preset-3myu4q · monochrome-1-bit-anime ·
nocturne-cinematic-fashion-vibe · parisian-night-vibe · summer-tapes-scrapbook · car-edit · drowned-sun-motion-edit · vhs-dont-forget ·
suit-up-basketball-montage · aesthetic-menu-outfit-swap · xerox-3 · urban-edge-skater-style · cinematic-film-look · blue-eyes · star ·
moody-vintage-film-edit · glow-groove-pop-edit · mountain-edge-noir · main-character-energy-edit · face-edit-2 ·
cinematic-perfume-commercial · greek-island-aesthetic · frame-dance · tokyo-bloom · dark-aura · ufo-specimen-collection ·
pink-protocol-car-edit · gritty-action-anti-hero-edit · dark-and-moody · cartoon-edit · luxury-car-beat-montage ·
dreamy-idol-aesthetic-montage · desert-sunrise-lookbook · xerox-1 · dark-geometric-animation · editing-my-gf · kpop-scrapbook ·
cyberpunk-scan-analysis · cinematic-mystery-noir · retro-aesthetic-lookbook · noir-mystery-thriller
