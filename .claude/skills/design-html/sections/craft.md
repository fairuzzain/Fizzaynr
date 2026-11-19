<!-- AUTO-GENERATED from craft.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->
## Craft: Persuade pages and the craft floor

**Persuade pages** applies when the page exists to get one action from a visitor: a landing, marketing, pricing, waitlist, campaign or comparison page. Write `Surface: Persuade` or `Surface: other` as the spec's first line; on `other`, skip to Craft floor, which applies to every page. An approved mockup wins on structure and visuals; this section fills only what it leaves open.

### Persuade pages

**One offer → one audience → one primary action.**

**Intake.** When the context does not settle them, ask one AskUserQuestion with at most three multiple-choice questions: the primary action, the traffic source, and published or design reference. Assume the rest in one `Assumed:` line the user corrects in the refinement loop:
- the conversion and the offer: exactly what they get
- who it is for, the problem they came with, their top three objections, what they already know
- the proof the user can supply (named customers, attributed quotes, real numbers) and the risk terms the business offers

**Archetype.** When approved.json carries an `archetype`, the user already chose it on the /design-shotgun board: take it and its `sections` outline as given, name both in the spec's layout type, and do not re-pick or re-ask. Otherwise pick one and say why there: **classic hero + sections** (`classic-hero`, default; the product reads from one screenshot), **long-form story** (`long-form-story`, the visitor needs educating or is skeptical), **minimal conversion** (`minimal-conversion`, high-intent traffic or a small offer), **comparison** (`comparison`, search intent is "X vs Y").

**Structure.** Above the fold at 375×667 and on desktop, inside the hero budget: a headline naming outcome and audience, one sentence on how, one primary CTA, one proof signal only when real proof exists (named logos or one attributed quote; a metric row stays banned), one product visual. Below it, choose modules and order from the archetype and the objections. The long-form menu: problem → solution, three to five benefits, how it works in three steps, proof, an FAQ of six to twelve real objections, the risk reversal, a final CTA identical to the top. A minimal page stays minimal; a comparison page leads with the comparison.

**Conversion rules.**
- A page behind an ad repeats the ad's promise and tone in the hero.
- One primary CTA; nothing competes with it above the fold.
- Benefit first and specific: "Cut weekly reporting from 4 hours to 15 minutes", never "save time".
- Show the risk reversal the business offers (free plan, trial, no card, cancel anytime). Never invent one.
- Proof sits beside the claim it supports. A high-friction offer moves the FAQ up.

**The primary action works.** A real destination (supplied URL or form endpoint) and every state: invalid (inline error, input kept), pending (control disabled so it cannot submit twice, announced through `aria-live`), failure (what happened, input kept, retry) and success (what happens next). With no backend, simulate the states and say so in a code comment and your summary.

**Copy.** A CTA is a verb plus what they get ("Start free trial"). Draft two or three headlines in the product's voice and keep the most specific one that names outcome and audience; "{outcome} without {pain}" is a test, not a template.

**Indexing.** Record the publication decision; keep the site's policy when known. A page the user keeps out of search gets `<meta name="robots" content="noindex">`; an indexed page gets a real title and description, and its FAQ ships as FAQPage JSON-LD.

**Build order.** One section at a time, top down; a refinement edits one section.

### Craft floor (every page)

**Claims come from the user, never from you.** Testimonials, customer names and logos, results, uptime, prices and guarantees appear only when supplied. Missing proof: leave the slot out, or mark it `[Needs proof: …]` in the warning color so it cannot ship by accident. A believable invented claim is worse than an obvious placeholder.

**Illustrative content looks real.** Sample data in product shots and UI (table rows, chart values, people in a demo inbox):
- No placeholder people or brands (John Doe, Jane Doe, Acme, Nexus, SmartFlow); distinct avatars; varied dates.
- No round sample numbers (99.99%, 50%, 1,000+ customers, 10x). In a claim, a round number signals it was made up: use the supplied figure or drop it.
- No buzzwords: elevate, seamless, effortless, supercharge, streamline, revolutionize, unlock, empower, unleash, next-gen, game-changer, delve, tapestry, "in the world of".
- Sentence-case headings. Errors say what happened and what to do, never "Oops!". No exclamation marks in success messages.

**Ship floor.** Head tags apply to a full HTML document, not a component or fragment. Every full document has `<title>`, a meta description, a favicon (an inline SVG data URI from the brand mark when no file is supplied), and on a page meant for sharing `og:title` and `og:description`; `og:image` only from a supplied URL. A "Skip to content" link is the first focusable element, hidden until focused, targeting the `id` of `<main>`. Landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`); alt text on meaningful images, `alt=""` on decorative ones. A marketing footer links privacy and terms at supplied URLs. Required fields and email format validate inline, wired with `aria-invalid` and `aria-describedby`. Every link goes somewhere real: no `href="#"`, no made-up path; a control with no target renders disabled. Navigation to other pages marks the current one `aria-current="page"`; in-page section links do not.

**Values come from the scale.** Every font size, space and radius is a step of the system's scale (DESIGN.md, else the spec), chosen by role. An off-scale value snaps to the nearest step that keeps its role, usually the one below, with that step's line height; never below 16px body text or a 44px touch target, and an approved mockup's measured values stand. A shape nested in another with a gap under 32px gets inner radius = outer − gap when that exceeds 2px.

**Line breaks.** Browser-wrapped headings get `text-wrap: balance`, body `text-wrap: pretty`. Break display lines where the thought breaks; never one word alone on the last line.

**Motion.** These govern the one authored motion moment and state transitions; they license no more motion.
- Content is visible by default; script adds the hidden start state only after the observer is set up (`.motion-ready` on `<html>`), so a script failure or a crawler sees everything and the CTA never waits on an animation.
- Reveal with `IntersectionObserver` (`threshold: 0`, bottom `rootMargin` about −20%, once). Never an unthrottled `window.addEventListener('scroll')`; scroll-linked effects read scroll inside `requestAnimationFrame`.
- Animate `transform`, `opacity`, `filter`, `clip-path` only; blur 14px or less.
- No object grows from `scale(0)` (start at 0.85 or more); only lines and bars grow from zero. A data bar fills as a left-to-right `clip-path` wipe, 0.7–1.1s.
- Stagger in reading order inside one section (30–80ms), never across the page.
- Curves are named tokens: DESIGN.md's, else `cubic-bezier(0.16, 1, 0.3, 1)` for entrances and `cubic-bezier(0.65, 0, 0.35, 1)` for wipes; `linear` only for constant motion.
- Loops pause off-screen. `prefers-reduced-motion: reduce` shows the final state. Full-height sections use `min-height: 100dvh`, not `100vh`.

### Design lint

At Step 4, after the Slop Gate and before the screenshots, run the free lint on the finalized page (`--scope component` for a component file alone; its copy tier reads HTML only, so judge those tells by eye there):

```bash
~/.claude/skills/gstack/bin/gstack-design-lint <path-to-finalized.html> --render
```

It prints one `LINT: <grade> <rule-id> <file>:<line> <evidence> | fix: <fix>` line per tell (the realism rules above among them), then `LINT_SUMMARY: blocks=N ask=N waived=N polish=N render=…`. Read the exit code: 2, fix every `blocks` line (never waivable); 1, fix each `ask` line or waive it; 0, list the `polish` lines as notes. No `LINT_SUMMARY` line: say the lint was unavailable and continue. A `render` line or `render=skipped`: say the page was not measured; the static lines stand. Same contract as the Slop Gate: one surgical fix pass, one rerun. Rerun once when the refinement loop exits; report only new lines.

**Waivers live in the page.** A tell that is right for this page (a real customer named Nexus, a supplied 50% figure, which `invented-proof` may also flag) gets a comment per rule, `<!-- gstack-lint-disable <rule-id>: <reason about this page, 24+ chars> -->`, and prints as `waived` with its reason on every later run, an evolve included. Waive only what the user supplied or confirmed, never a line you could fix.

**Before this can ship.** Open the Step 4 hand-off, and repeat before Step 5's "Copy to project": every `[Needs proof: …]` marker, the dependencies the page cannot own (legal URLs, form endpoint, og:image, indexing, analytics and cookie consent where required), every waiver, and every claim the lint made you change.

Adapted from Elaya's [ai-design-skills](https://github.com/elayadesign/ai-design-skills) and [redesign-skill](https://github.com/elayadesign/redesign-skill) (MIT, © 2026 Elaya), rewritten for gstack. See NOTICE.md.
