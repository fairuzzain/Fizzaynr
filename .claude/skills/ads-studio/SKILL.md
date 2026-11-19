---
name: ads-studio
version: 1.2
description: >-
  Ads Studio (Nexabot): static ad creatives with copy and pictures for a product or a brand,
  through the ads_studio_* tools. Use whenever the user wants ads or ad creatives, including Meta
  ads (Facebook, Instagram) and other static social ads, with or without a brand: from a brand's
  website (researched into a brand kit and products), from an existing Ads
  Studio brand or product, from a product page link, from a product photo with a description, or
  from a prompt alone; and for anything about an existing Ads Studio brand, product or run. Not
  for a picture without ad copy (generate_image), a Marketing Studio brand-kit record (marketing_*
  tools), logo or identity design (brand-asset-creation), ad copy alone, or UGC and other video
  (ugc-* workflows).
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Ads Studio

Ads Studio makes static ad creatives, the kind that run as Meta ads on Facebook and Instagram:
it writes the copy and renders the pictures. It can start from a brand, researched from its own website into a brand profile with products, or from a single
product with no brand at all: a page link, a photo with a description, or just what the user says.
Your job is to run the flow in the right order, give Ads Studio the product before it writes ads
for it, spend nothing before the user agrees, and never pretend to know more than the tools
returned.

Ads from a product photo are this workflow, not a batch of pictures. `generate_image` and
`generate_image_batch` make pictures without copy, and are the wrong tools as soon as the user
says ad, creative or campaign.

## Is Ads Studio here?

If `ads_studio_list_brands` is not among the available tools, Ads Studio is not enabled on this
connector. Say so, point the user to https://higgsfield.ai/ads-studio, and stop. Do not substitute
Marketing Studio, brand-asset-creation or a plain image generation.

## Where Ads Studio ends

| The user wants | Route |
| --- | --- |
| Ads or ad creatives, including Meta, Facebook or Instagram ads, for a product or a brand: from a website, an existing Ads Studio brand or product, a product page, a product photo with a description, or a prompt; anything about an existing Ads Studio brand, product or run | this workflow |
| A Marketing Studio brand-kit record: save colours, fonts, logo values they already have | the Marketing Studio tools (`show_marketing_studio_v2` and the `marketing_*` tools), not Ads Studio |
| A new logo, visual identity, mockups, brandbook, posters | `brand-asset-creation` workflow |
| A creator or UGC video, a product video | the `ugc-*` workflows |
| A picture, or several, with no ad copy: a product shot, a catalog photo, a scene | `generate_image` and the image batch tools |
| Ad copy alone, no pictures | write it in chat; nothing in Ads Studio is spent |

"Brand kit" is ambiguous. Ads Studio's brand kit is what its research reads off the website
(logo, palette, fonts, tagline, audience) and shows on the research card. If the user is
handing you finished brand values to store, that is Marketing Studio.

## The flow

### 1. Start from a brand or from a product

Two ways in. A brand, when the user names one or gives its website. A product, when they give a
product page, a photo with a description, or a description alone. A product needs no brand, and
no brand is invented to hold one.

**From a brand.** Call `ads_studio_list_brands` first when the user talks about a brand they may
already have. Reuse a brand whose `status` is `done`; a `running` one is still researching; a
`failed` one can be researched again from its website. For a new brand call
`ads_studio_create_brand` with the website URL. With only a name, Ads Studio starts nothing and
answers `needs_confirmation: true` with `suggested_website`: ask the user in one line ("Is that
allbirds.com?") and, after their yes, call again with that URL as `input`. Never guess or type a
domain the user or Ads Studio did not name, and never start research on a guess.

**Which one a link is.** A bare domain or homepage, or the words brand, store, site or company,
is a brand: research it. A link to one item (a path like `/products/...`, or the words this
product, this item) is a product. Ads Studio does not check: research started from a product
page researches the whole site, and the product reader handed a homepage files a homepage.

**From a product.** Do not list brands first: the brand list opens its own card, and the user
asked about a product. If the conversation already shows the user's brands and one owns the
link's domain, file the product under it with its `brand_id`, so its kit reaches the ads. If the
user's words settle it, follow them: "my brand" means research, "just this product" means no
brand. Otherwise ask one line before anything starts, with the link's own domain in it: "I can
file just this product, also research acme.com as a brand, about a minute and a half, so the ads
carry its logo, colours and tone, or add it to one of your Ads Studio brands. Which one?" Just
the product: `ads_studio_add_product` with no `brand_id`. Also the brand:
`ads_studio_create_brand` with the domain root, then `ads_studio_add_product` with the new
`brand_id`; both read in parallel and step 2 waits for both. One of their brands: read
`ads_studio_list_brands` once and file the product under the brand they name. A brand that
fails while its product completed leaves the product usable without the kit.

Call `ads_studio_add_product` with the page as `url` when there is one, the user's own
description as `text`, and their photos as `images`. Ads Studio reads the page and writes the
product's copy in the background; that is what makes the ads specific, so the product row comes
first even when the user only asked for ads. A photo attached to the chat has no link yet: call
`media_upload_widget` as the only tool of that turn, then `media_confirm`, and pass the `url` it
returns. A link Ads Studio cannot fetch is refused; then ask for the product page or a public
image link.

The one exception is a prompt with nothing to file: an offer, an idea, a service with no page and
no photo. That goes to quote and generate with `prompt` alone, and comes out as specific as the
prompt and no more.

### 2. Wait until Ads Studio has read it

Brand research takes about a minute and a half and opens the research card, which shows the
five stages (gather, synthesis, enrichment, products, assets) as they complete. A product row
takes about a minute and opens the product card, which shows the page being read and then the
product. Tell the user what has started and that you will quote as
soon as it is ready, then stop your turn. Do not call `ads_studio_get_brand`,
`ads_studio_get_product` or `ads_studio_list_products` on a timer or in a loop: read once when the
user comes back, and if it is still running, say so and stop again.

**Nothing is quoted or generated before it is ready.** Ready means: a product the user added
shows `status: completed` in `ads_studio_get_product` (`queued` and `in_progress` are not ready;
`failed` carries `fail_reason`), and an `images_count` above zero when it came from a page; a
brand's researched products show `texts_ready: true` in `ads_studio_list_products`; and a brand
involved has `status: done`. Ads generated before that come out generic: Ads Studio writes the
copy from what it has read, and it has read nothing yet.
A user who says "make ten ads, go" while the page is still being read gets the wait explained,
not a generate call.

When `ads_studio_get_brand` answers `status: done` and `profile_ready: true`, the brand step is
over: the card shows the brand kit (logo, palette, fonts, tagline) and the products it found. Say
that in a sentence or two, using the card's content rather than listing everything again.

If it answers `status: failed`, tell the user why in the words of `research_error` and offer to
try the website again. A partial failure (`gather_error`, `enrichment_error`, `products_error`)
with `status: done` still leaves a usable profile; mention what is missing.

### 3. Offer ads, with the price

Once it is ready, offer to make ads. Read `ads_studio_list_products` (with the `brand_id` for a
brand's products; without one for every product the user has, of any brand or of none, a page at
a time with `cursor` and `next_cursor`), suggest which products fit the user's goal (or the brand
itself), and call `ads_studio_quote` with exactly the arguments you would pass to generate. Tell
the user the `credits` it returns and how many creatives that buys, then wait.

Generation starts only on an explicit yes to that price. A question about cost ends at the
quote. A request to make ads authorizes quoting, not spending at an undisclosed price.

For spending approval, use `ask_user_input` (or `ask_user_input_v3`) only when that
exact host tool is exposed; otherwise ask one concise chat question. Never invent a host tool.

**When the Ads Studio app submits an `allocation`**, Continue is NOT spending approval.
Pass the whole allocation unchanged to `ads_studio_generate` in one call with its `brand_id`,
`aspect_ratio` and `idempotency_key`. The server quotes every batch and requests one native MCP
form confirmation when the host supports it. Otherwise it returns `approval_required` and the
aggregate `credits`. Show the exact counts and cost, ask one concise chat question for spending
approval and stop. Only after an explicit yes, repeat the unchanged request with
`expected_credits` equal to the approved cost. The server rechecks the price before spending.
Do not bypass a supported native form, split the allocation, omit `allocation` or change the
idempotency key. Do not list or research products again. On `QUOTE_CHANGED`, request a fresh
allocation quote and approval, without `expected_credits`. Cancel, decline or missing approval
starts nothing.

**When a card sends the chat a message that starts "Use this product for Ads Studio ads"**, the
user has picked that product on the card. The message carries its `product_id` and, when the
product belongs to a brand, its `brand_id`. Do not list brands or products again and do not
research anything. Read `ads_studio_get_product` once: if it is `completed`, quote with those ids
and the user's count, say the price, and wait for the yes the message asks for; if it is still
being read, say so and stop.

### 4. Generate

Call `ads_studio_generate` once, with:

- What to advertise: `product_ids` (of any brand or none; each gets its own run), and/or
  `include_brand: true` for the brand itself, and/or a `prompt` in the user's own words. A
  generation advertises exactly what these say. `picked_for_ads` on a product only decides what
  the brand page shows in the web app; it does not select products for generation.
- `brand_id`, optional: the brand whose kit (logo, palette, tone) shapes the ads. Leave it out
  for ads with no brand kit, or send `brand_kit: false` to advertise a brand's product without
  its look. The kit only reaches its own brand's products: a product of another brand, or of
  none, is advertised without it, so never promise one brand's look on someone else's product.
  `include_brand` needs `brand_id` with the kit on.
- `images`, up to four public links the user supplied: `role: "product"` for a photo of the
  thing being advertised, `role: "style"` (the default) for a look to follow.
- `total`: the number the user named, or 1 for a singular request. Ads Studio splits it
  across the subjects, so it must be at least one per subject. "Two products, three ads each"
  is `total: 6` with two `product_ids`.
- `aspect_ratio`: one of `1:1` (default, square feed), `9:16` (stories, reels), `16:9`
  (landscape), `3:4` (portrait feed). **`4:5` is not available**: offer `3:4` as the nearest
  portrait frame. Always send the frame.
- `objective`, only when the user made the goal clear: `sales`, `leads` (sign-ups, demos,
  quotes), `traffic` (visits, clicks), `awareness` (a launch, being known), `engagement`
  (comments, shares). Otherwise leave it out and the product's own profile decides.
- `idempotency_key`: choose it once for this generation (any unique string) and repeat it
  unchanged if you must retry the same call. A new key on a retry buys the same batch twice.

The answer lists `runs` with a `run_id` each and `selected_products` by name. Report which
products the ads are for and stop; the generation card follows the pictures.

### 5. Follow the run

Read `ads_studio_get_run` when the user asks, never on your own initiative and never in a
loop. Rendering takes about three minutes after writing. A run can read `status: done` while
`still_rendering: true`; do not say the ads are ready until `still_rendering` is `false`.
Each concept carries its copy (`headline`, `primary_text`, `cta`, `destination_url`) and
`has_picture`; the pictures themselves are on the card. Name a creative by its `concept_id`.

These are not ordinary generations. Never pass an Ads Studio `run_id` or `concept_id` to
`show_generation_by_ids`, `jobs_wait`, `job_status` or `job_display`, and do not ask for an
image link; there is none for you to hold.

`ads_studio_list_runs` finds a run whose id was lost or shows what is already in flight before
starting another batch. `ads_studio_cancel_run` stops a queued or running run only when the
user asks; pictures already rendered stay, and a run too far along answers that it cannot be
canceled. A canceled run is not a failure.

## Products

- `ads_studio_add_product` adds a product from its page `url`, the user's `text` and/or their
  `images`, under a brand or under none; pass existing ids in `overwrite` to refresh rather than
  duplicate. It answers as soon as the row is queued; the product is usable once
  `ads_studio_get_product` answers `status: completed`.
- `ads_studio_get_product` reads one product: `status` says whether Ads Studio has finished reading
  its page (`queued`, `in_progress`, `completed`, or `failed` with `fail_reason`). Read it once
  when the user asks about a product they added; its card follows the read by itself.
- `ads_studio_list_products` with a `brand_id` lists that brand's products; without one it lists
  every product the user has, of any brand or of none, a page at a time.
- `ads_studio_update_product` merges the fields you send and leaves the rest alone. Use the
  user's own words for copy fields; do not invent selling points. `picked_for_ads: false`
  hides a product from the brand page, `true` shows it; nothing is deleted.
- `texts_ready: false` on a brand's product means its copy is not written yet. Wait for it
  before quoting (step 2): ads made from an unread product come out generic.

## Outcomes and recovery

| Answer | What to do |
| --- | --- |
| `needs_confirmation: true` from create_brand | Confirm `suggested_website` with the user; call again with the URL. Nothing started. |
| `status: failed` on a brand | Explain `research_error`; offer to research the website again. |
| A brand `failed` while its product `completed` | The product is usable without the kit: say so, offer to research the site again, and quote the product alone if the user wants. |
| `status: failed` from get_product | The page could not be read. Say why in the words of `fail_reason`; offer to try the page again with `overwrite`, or ask for the user's own description and photo. Do not quote it. |
| `queued` or `in_progress` long after a product was added, or `completed` with `images_count: 0` from a page | Still unread, or read without pictures. Offer to refresh it with `overwrite` (a page that blocks readers stays unread), or ask for the user's own description and photo. Do not quote yet. |
| A picture link Ads Studio cannot fetch | Ask for the product page or a public image link; a chat attachment goes through `media_upload_widget` and `media_confirm` first. |
| `partial: true` from generate | Some runs started and are paid for: report those `run_ids`. Nothing was charged for the products in `not_started`; say why from `not_started_reason`, and only if the user still wants them, generate those products alone with a new `idempotency_key` (a different batch). Never repeat the whole request. |
| `error_code: ADS_STUDIO_UNAVAILABLE` after a generate | The request may have been accepted. Read `ads_studio_list_runs` before anything else; never retry with a new `idempotency_key`. |
| Not enough credits, quota or queue refusal | Say the numbers the answer carries and what it suggests; do not lower the count or switch products on your own. |
| `still_rendering: true` on a `done` run | The copy exists, the pictures are landing. Not ready yet. |
| The user wants edits, variations or a different look | Not available through these tools; point to Ads Studio in the web app. |

## Never

- Poll `ads_studio_get_brand`, `ads_studio_get_product`, `ads_studio_get_run` or `ads_studio_list_products` in a loop; the cards poll, and you read once per user turn.
- Quote or generate while a product to advertise is still `queued` or `in_progress`, shows `texts_ready: false`, or a brand involved is still `running`.
- Send a product photo plus a request for ads to `generate_image` or `generate_image_batch`.
- Start research on a domain nobody named, or generate before the user agreed to the quoted price.
- File a product page as a brand, or a homepage as a product; when the link's domain is new and the words do not settle it, ask.
- Send `4:5`, or an objective the user did not imply.
- Reuse the same `idempotency_key` for a different batch, or mint a new one for a retry.
- Hand Ads Studio ids to the generic job tools, or describe `picked_for_ads` as choosing products for ads.
- Call an Ads Studio brand kit a Marketing Studio brand kit, or the other way round.

---
(Shared section: see ../_shared/unlimited-generations-use_unlim.md)
