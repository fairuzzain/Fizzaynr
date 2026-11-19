---
name: "otomasi-canva"
description: "Automate Canva through the connected Canva connector: find, create, edit, resize, export and organize designs, upload assets, and autofill brand templates."
---

# Canva Automation (Canva connector)

Use the user's connected Canva connector (tools named `mcp__Canva__*`). Do not use Rube/Composio. If no `mcp__Canva__*` tools are available, tell the user to connect Canva under Settings > Connectors and stop.

Every Canva tool takes a `user_intent` field: always fill it with a short description of what the user wants.

## Before any workflow

- Load the Canva tool schemas you need (ToolSearch `select:` with all of them in one call) and follow each tool's own description when it differs from this skill. The connector's tool descriptions are the source of truth.
- Design IDs start with `D` and are 11 characters. IDs inside preview URLs from generation are NOT design IDs.

## 1. Find designs

Tool: `search-designs`
- `query`: the user's keywords (requires `sort_by: "relevance"`, the default)
- `ownership`: `any` (default), `owned` or `shared`
- `sort_by`: `relevance`, `modified_descending`, `modified_ascending`, `title_ascending`, `title_descending`
- Follow `continuation` until it is absent when the user wants a full list.
- To read what is inside a design (text, pages, thumbnails, speaker notes): `read-design` with the `design_id` (a share URL also works).

## 2. Create a design

- If a `create-design` tool is listed, use it for ordinary new designs.
- For on-brand designs (brand kit, brand colours/fonts/logo, or a brand template), or when `create-design` is absent, use `generate-design`:
  1. Ask whether the user wants an on-brand design. If yes, call `list-brand-kits` and let them pick; pass `brand_kit_id`.
  2. Call `generate-design` with a detailed `query` (include all context from the chat; the tool has no memory) and a `design_type` (poster, flyer, instagram_post, your_story, doc, infographic, logo, youtube_thumbnail, etc.). Do not use it for presentations; follow the tool description for those.
  3. Show the returned candidates and let the user choose one.
  4. Call `create-design-from-candidate` with `job_id` and `candidate_id` to get a real `design_id` before editing, exporting or resizing.
- To create a design from a web page URL the user gives, use `import-design-from-url` instead.

## 3. Upload assets

Tool: `upload-asset-from-url` with `url` (public HTTPS only) and `name`. Returns a media/asset ID that can be passed as `asset_ids` to `generate-design`, or used in `edit-design` and `autofill-design`.
- Local or private files cannot be uploaded this way; ask the user to host the file publicly or upload it in Canva themselves.

## 4. Edit a design

1. `read-design` with `open_transaction: true` and `filter.fields` including `thumbnails` and `design_content` to get a `transaction_id` and element locator IDs.
2. `edit-design` with `transaction_id`, `page_index`, `finalize: "keep_open"` and `operations` (e.g. `replace_text`, `find_and_replace_text`, `format_text`, `update_fill`, `insert_fill`, `add_text`, `add_page`, `position_element`, `resize_element`, `update_title`).
3. Show the user the preview and get explicit approval.
4. Save with `edit-design` `finalize: "commit"` and no operations, or discard with `finalize: "cancel"`.
- Responsive pages accept only `update_title`, `replace_text`, `update_fill`, `delete_element`, `find_and_replace_text`.

## 5. Resize

Tool: `resize-design` with `design_id` and `design_type` either `{type: "preset", name: "presentation" | "whiteboard"}` or `{type: "custom", width, height}`. Creates a new design; the original is unchanged.

## 6. Export

1. `get-export-formats` with `design_id` to see which formats and pages are supported.
2. `export-design` with `design_id` and `format`: `type` (pdf, png, jpg, gif, pptx, mp4, csv) plus optional `pages`, `export_quality` (`regular`/`pro`), `size` for PDF (a4, a3, letter, legal), `width`/`height`, `transparent_background`, `as_single_image`; `quality` is required for mp4 (e.g. `horizontal_1080p`) and 1-100 for jpg.
3. Give the user the download URL promptly; it expires.

## 7. Organize with folders

- `create-folder` with `name` and `parent_folder_id` (`"root"` for top level).
- `move-item-to-folder` with `item_id` (design, folder or image) and `to_folder_id` (`"root"` for top level).
- Use `search-folders` / `list-folder-items` to find existing folders.

## 8. Autofill brand templates

1. `search-brand-templates` with `dataset: "non_empty"` to find templates that have data fields.
2. `get-brand-template-dataset` with `template_id` to list field names and types. An empty result means it cannot be autofilled.
3. `autofill-design` with `brand_template_id`, optional `title`, and `data` where each key exactly matches a field name (case-sensitive) and each value is typed: `{type: "text", text}`, `{type: "image", asset_id}`, `{type: "video", asset_id}` or `{type: "chart", chart_data: {rows: [{cells: [{type, value}]}]}}`.
- For many rows (e.g. a spreadsheet), call `autofill-design` once per row with a distinct `title`.
- Only use `design_id` with `update_in_place: true` when the user explicitly asks to overwrite an existing design; it cannot be undone.

## Other useful tools

- `copy-design`, `merge-designs`, `comment-on-design` / `list-comments` / `reply-to-comment`
- `remove-background`, `generate-image`
- `help`: answer "how do I..." Canva product questions from the official Help Center; show its answer as written.

## Rules

- Never commit edits, overwrite designs or move many items without the user's confirmation.
- If a tool returns an error, read it and fix the input; do not retry the same call blindly.
- Ask for more detail when generation returns "Common queries will not be generated".
- Stop and ask for clarification if required inputs, permissions or success criteria are missing.