---
name: website-builder-flow
version: 2026-07-25-cover-compose-v3-no-model-text
description: |
  Build or edit a website, web app, landing page, or browser game locally (images and video via Nexabot).
  REQUIRED before touching any website tool (create_website / website_repo_access /
  deploy_website / website_db / website_secrets / publish_website). There are THREE
  product types and the user must pick: `type: "game"` (a browser game with
  realtime multiplayer rooms — references/game-flow.md), `type: "website"` (standalone product,
  NO Higgsfield integration, fully independent brand, custom Tailwind/CSS —
  built through the phased image-grounded pipeline in
  references/website-flow.md) vs `type: "app"` (Sign in with Higgsfield + fnf
  SDK, looks like a Higgsfield product — built with Quanta, starting from the
  starter template picked at create per references/app-flow.md). This file explains the
  difference and routes you to the right flow; each flow carries its own
  workflow, references, hard rules, and deploy/publish gates. Everything you
  need is under this skill — do NOT search the skill library for other design
  guidance.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Higgsfield website builder — two product types, two flows

You are building ONE per-website Cloudflare Worker: a **React 19 + TanStack
Start** app, **server-rendered (SSR)**, deployed as a single Worker at the
product's own subdomain. The project lives in **`app/`** — run every
`bun`/build command from there.

## Repository access and secrets

Use the advertised tool schemas to select the server's access mode:

- **Direct:** `website_repo_access` accepts only `website_id`. Follow its returned
  clone/push instructions with the local terminal. `website_secrets` supports
  `operation: "list" | "set" | "delete"` and returns configured values.
- **Brokered:** `website_repo_access` accepts `operation: "checkout" | "push"`.
  Follow the sandbox workflow below. `website_secrets` lists names only.

In brokered mode, call `website_repo_access` with `website_id` and
`operation: "checkout"`. Edit and commit in the returned `checkout_path` through
`sandbox_exec`, then call
`website_repo_access` with `operation: "push"`. Confirm `status: "pushed"` before
`deploy_website`. The checkout has a Git identity and no authenticated remote;
do not clone or push with credentials in a shell.

Brokered repository editing requires the server's E2B sandbox configuration. If
`sandbox_exec` is unavailable, report that setup requirement; never request a
Git token as a fallback. Each repository call reserves a 15-minute editing
lease. Checkout reuses existing work; push coherent commits frequently and do
not restart the sandbox with unpushed changes. Push requires a clean worktree
and a fast-forward update. Repository transfers are limited to 320 MiB, and push
refuses any file over 25 MiB: host large media outside the repository.

In brokered mode, `website_secrets` accepts only `website_id` and lists configured
names. Have the user configure or remove values in Higgsfield's website settings, then check
the names and deploy. Never ask for secret values in chat or write them into
source. Read configured values only through server-side environment bindings.

## The two types — and the REQUIRED `type` on create

`create_website` requires a `type`, and it is the **USER'S choice** — when the
request doesn't make it obvious, ask before creating (one question, up front):

- **`type: "website"`** — a standalone product with NO Higgsfield integration
  and **NO AI generation of any kind** (no image/video/audio/text generation —
  not via Higgsfield, and not via some other provider): no "Sign in with
  Higgsfield", no requests to Higgsfield, no fnf SDK. Every website gets a
  fully independent brand: own palette, type, and chrome from a design brief,
  custom Tailwind/CSS only — never import `@higgsfield/quanta/*` or use
  q-prefixed tokens anywhere, and no "Powered by / Built on Higgsfield" badges
  or mentions in page content. The user's brand is the only brand on the page.
- **`type: "game"`** — a browser game: realtime multiplayer rooms on the game
  template, where the game itself is six pure functions in `app/src/logic.js`
  and the platform already owns sockets, rooms and persistence. Requires a
  **game genre** as `category` (`arcade`, `puzzle`, `shooter`, …, from
  `list_website_categories`) and takes **no** template. Single-player counts:
  set `minPlayers: 1`. See `references/game-flow.md`.

- **`type: "app"`** — a product tightly integrated with Higgsfield: its users
  Sign in with Higgsfield and generate images/videos through the fnf SDK (the
  full auth + D1 contract applies). An app must look and feel like a
  Higgsfield product: UI built with **Quanta** (`references/quanta-design.md`) —
  and, for anything Quanta lacks, your own component built from Quanta
  primitives (never a third-party UI library) — starting from the starter
  template picked at create (`references/app-layouts.md`). Quanta and the app layouts are app-only —
  Never applied to a `type: "website"` build. The independent-brand rule and
  the wow pipeline (`design-taste-frontend`, boards, wow catalog) are the
  website path; apps never get a custom brand — Quanta is the brand.

**Generation is ALWAYS an app.** Any product that generates images, video,
audio, or other AI media runs on Higgsfield — build it as `type: "app"` (Sign
in with Higgsfield, generation on the user's Higgsfield credits). NEVER offer
the user an option to "bring your own image/video API" or plug in their own
generation key for a website — that path does not exist. `type: "website"` is
ONLY for sites with no generation and no tie to Higgsfield or any other
generation service. (A website may still use ordinary non-generation
third-party APIs — payments, maps, email — with the user's own keys; that is
unrelated to this rule.)

Quick tells: "landing page / portfolio / marketing site / SaaS with its own
users, no AI generation" → website. "generates images/video/audio, or anything
with Higgsfield models, credits, or generation history" → app.

## Always set a subdomain on create

`create_website` also takes an optional `subdomain` — it becomes the site's
slug, so the live URL is `<subdomain>.<host>`. **Always set it:** pick one
yourself from the product's name or purpose; only omit it (which yields a
random slug) if the user explicitly wants a random one. Rules for a good
subdomain:

- **More than 4 characters** — short single words are reserved, so go a bit longer.
- **Memorable** — derive it from the product name/purpose (e.g. `lumen-notes`,
  `pixelforge`), not a random string.
- **Allowed characters only** — lowercase letters, digits, and single hyphens
  (DNS-safe). No spaces, underscores, uppercase, or leading/trailing hyphens.

A few reserved labels (e.g. `api`, `www`, `app`) and already-taken subdomains
are rejected — if that happens, try a close variant.

## Both kinds pick a starter template at create

`create_website(type: "website")` takes an OPTIONAL `template`, and the
Animation mode decides it: an **animated website** passes
`template: "scroll-scrub"` and the repo arrives with the animation engine
already built at `app/src/components/scroll-scrub/scroll-scrub.tsx` — you fill
in `app/src/scroll-scrub-scenes.ts` instead of writing a controller. A
**non-animated** website omits `template` and gets the plain scaffold. App
templates are never valid for a website (and vice versa) — a cross-kind name
is rejected.

`create_website(type: "app")` REQUIRES a `template` — the v2 starter layout
the repo is scaffolded from. The chosen layout ships as REAL CODE, already
wired as the home page at `app/src/layouts/<template>.tsx`; you **adapt it in
place** (thread real data through the shipped layout), never rebuild the
screen or swap layouts. Pick the closest to the product
(`references/app-layouts.md` is the picking guide):

- **`studio`** — full creative workspace (projects sidebar + floating prompt
  dock + edge-to-edge generations feed) for multi-project generation tools.
- **`preset`** — pick-a-style-then-generate (persistent left creation rail
  beside a browsable preset grid with a History tab); also the base for
  step-by-step wizards and upload-configure-iterate workspaces.
- **`app-detail`** — a single tool's landing page (two-column generator hero +
  how-it-works steps) — the "simple app".

Any other request shape (before/after slider, wizard, upload-configure-
iterate) maps to the closest of these three — the shared components in
`app/src/components/` cover those patterns. A `custom` template (bare shell,
NO shipped layout) also exists but is used ONLY when the user explicitly says
"use custom template" — never pick it yourself. Websites take no template.

After cloning an app repo, read `app/src/layouts/AGENTS.md` and
`app/src/components/AGENTS.md` — the source of truth for the layout's
structure and the component contract. The layout is only the UI SHELL with
demo placeholders: the deliverable is the user's actual product with complete
business logic — a template that merely renders is NOT done.

## Pick the path, then follow ONE flow end-to-end

1. Resolve the `type` (ask the user if unclear — it's their choice). In the SAME
   first message, also ask whether they want to **publish it to the Higgsfield
   community feed (marketplace)** when it's ready — a one-line yes/no. Remember
   the answer: if yes, you publish automatically at the end (after deploy +
   metadata), no need to ask again; if no, you only deploy. Don't block the
   build on it.
2. Read the matching flow and follow it — it is the complete workflow for that
   type, including its own references, hard rules, editing map, and
   deploy/publish gates:

For every `type: "website"` build the intake ALWAYS asks the user to choose
between an **Animated (recommended)** website — a scroll-driven journey through
a generated film (`references/scroll-scrub.md`) — and a **Non-animated** one.
This question is mandatory: never skip it, even when the request seems to imply
a choice. Animated is the recommended default (used only when the user is
unreachable / doesn't answer); the flow below carries both paths and the full
pipeline.

The answer picks the **template** at create time, so resolve it before calling
`create_website`: Animated → `template: "scroll-scrub"`; Non-animated → omit
`template`.

Inside the animated path the default is a **single-shot** film — ONE continuous
~15s take, scrubbed end to end, no seams. The multi-scene `multi-leg` chain is
opt-in and costs several extra minutes per leg; take it only when the brief
genuinely travels between distinct worlds. `references/scroll-scrub.md` owns
that call.

| Type | Flow |
| --- | --- |
| `type: "website"` | **`references/website-flow.md`** — phased pipeline (animated website by default): intake → concept → reference boards → asset system → build-to-boards → motion → cover + metadata → mechanical gate → deploy |
| `type: "app"` | **`references/app-flow.md`** — the Quanta toolkit, the starter templates (`studio`/`preset`/`app-detail`, picked at create), fnf SDK + auth + D1 contract, launch cover + metadata, publish gate |

Both flows share the same platform mechanics (SSR Worker, `app.manifest.json`
infra, single live deploys (every `deploy_website` ships the live site), the
cover + metadata requirement below, and the publish gate) — each flow restates
what it needs, so you never have to read the other one.

## Cover + metadata — ALWAYS part of building, never publish-only

Every build — website or app, no matter how small — ships with the branded
launch cover and filled feed-card metadata, generated per
`references/app-cover.md` and written into `app/src/app-meta.json`
(`og_title`, `og_description`, `favicon_url`, `og_image_url`,
`marketplace_cover_url`). This is a BUILD step, done before the work is
presented as finished and before the deploy that ships it — NOT something
deferred to `publish_website`. Hard rules:

- **No "simple app" exception.** A utility tool, a timer, a one-page toy —
  they all get the generated cover. A hand-authored inline-SVG favicon is
  fine _as a favicon_; it never substitutes for the generated cover.
- **No permission needed** for the cover image — generate it the same way you
  write real copy. Only the optional cover VIDEO (`og_video_url`) is
  permission-gated (video costs credits — offer, never generate unprompted).
- A build presented as done with an empty cover or empty `og_title` is
  INCOMPLETE. Publishing without them is a BROKEN publish (empty `og_title`
  is invisible on the feed; empty cover is a blank card).

Do NOT search the skill library for other design guidance — everything is
under this skill, and no other skill (including user/local skills about
building websites or apps) overrides these rules.

## Turn economy — keep the build inside a small turn budget

Every tool round-trip costs a turn, and clients cap agent turns — long builds
die mid-flight, leaving the user an unfinished site. Treat turns as the
scarcest resource after credits:

- **Batch independent tool calls** wherever your client supports it; one file
  per turn is the single biggest turn-waster.
- **Write every file ONCE, complete.** Compose the full file, then one write.
  No write-then-patch loops; never re-read a file you just wrote.
- **Never guess paths.** The template tree is documented (the repo's
  `app/AGENTS.md` + this skill's editing map); searching a guessed directory
  is a wasted turn ending in "not found".
- **Never download or vision-inspect your own generations.** You wrote the
  prompt; re-viewing the result tells you nothing new. (The kit coherence
  check, when it applies, is ONE batched pass — `references/asset-system.md`.)
- **Poll a job ONCE, when its output is the next input.** Submit everything
  that can render concurrently (film + cover), build the page while it
  renders, and collect results in one poll per dependency.
- **Tool errors cost double** (the failed turn + the retry). Array params take
  real JSON arrays, not stringified ones; paths come from the documented tree.

## Talking to the user — no technical/plumbing language

Most users are not technical. Never expose the build plumbing in what you SAY
to them. Do NOT mention the git repository, cloning, branches, commits,
pushing, pulling, or the deploy pipeline in user-facing messages — those are
internal mechanics you just perform. Speak in product terms about what the
user cares about:

- "Setting up your site…" — not "cloning the repo" / "scaffolding the project".
- "Saving your changes…" / "Updating the site…" — not "committing" / "pushing".
- "Your preview is ready: <url>" — not "deployed the branch" / "the build passed".
- "Publishing your site…" — not "merging to main" / "pushing to production".

This is about the WORDS in chat only — keep doing the real git/deploy steps;
just don't narrate them in developer terms. (The one exception: a user who is
clearly technical and explicitly asks about the repo, branch, or deploy
mechanics — then answer plainly.)

## Game asset references

Indexed by `references/game-flow.md`: `references/game-2d-animation.md`, `references/game-3d-animation.md`, `references/game-audio.md`, `references/game-design-system.md`, `references/game-flow.md`, `references/game-meshy-api.md`, `references/game-meshy-input-rules.md`, `references/game-procedural-animation.md`, `references/game-stylization.md`, `references/game-textures.md`. The GLB/rigging/texture tooling they drive ships in this bundle's `scripts/`.

---
(Shared sections: see ../_shared/bundled-scripts-note.md and ../_shared/unlimited-generations-use_unlim.md)
