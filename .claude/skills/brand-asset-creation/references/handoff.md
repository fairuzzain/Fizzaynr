# Brandkit state routing

Brandkit approval state lives in `.brandkit/state.json` inside the sandbox working directory. Drafts never enter it. The script writes atomically and preserves independent logo, palette, typography, visual-axis, and downstream-element revisions.

Run every operation through `sandbox_exec`:

```bash
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py state --action ACTION [--input INPUT.json]
```

Create payload files with a quoted heredoc (`cat > brandkit/input.json <<'JSON' … JSON`); never interpolate JSON or user text into the shell command arguments.

Before the first state write, load [exact state payloads](state-payloads.md) and copy only the matching complete object shape. Replace values, not keys or nesting.

## State carry protocol (ephemeral sandbox)

The sandbox is per user and may disappear between calls. The durable source of truth is the latest **confirmed state JSON URL from this conversation**, not a sandbox file, account-wide media listing, or another chat's state. Keep the existing `.brandkit/state.json` schema; renaming the skill does not rename state keys or asset origins.

1. Before a mutating batch, call `media_upload` for `brand-state.json` with `content_type: "application/json"`. Keep its upload URL and file ID.
2. Start EVERY batch in an isolated working directory created by `mktemp -d`, then `cd` into it and `mkdir -p .brandkit brandkit`. All commands in that batch run there. Restore `.brandkit/state.json` with `curl -fL` from this conversation's last confirmed snapshot. If this is a new conversation with no approvals, initialize it with `printf '%s\n' '{}' > .brandkit/state.json`. Never adopt a leftover file. This also applies to QA and retries: never search `/tmp` or pick a directory by a matching filename; restore the exact confirmed URLs from this conversation in a new isolated batch. For an older conversation with a complete printed snapshot but no hosted snapshot, restore that exact JSON once with a quoted heredoc; never use a truncated copy.
3. Create the input with a quoted heredoc. Run the state action, redirecting its potentially large JSON result to `brandkit/state-action.json`. Continue only on exit 0. Print a narrow `get_status` response when needed, not the full ledger.
4. Append `curl -f -X PUT --upload-file .brandkit/state.json '<reserved upload_url>'` in that SAME command. Chain restore → action → PUT with `&&` so failures cannot publish stale state. Use the upload tool's headers verbatim.
5. After successful PUT, call `media_confirm` with the reserved ID and `type: "file"`. Remember that confirmed URL as the new snapshot. Do not announce the slot as saved until mutation, upload, and confirmation all succeed. Do not expose internal snapshot links as user deliverables.

Read-only/render batches restore the snapshot but need no new snapshot upload. All asset IDs/URLs stored in state must be durable confirmed uploads or generation results; never store sandbox-local paths. Re-download temporary inputs within the batch that consumes them.

Do not retry a paid generation after a snapshot/upload failure. Recover from the last confirmed snapshot and the explicit selection already in this conversation; if the selected asset or approval evidence is missing, stop and explain the recovery failure. Never invent approvals. A sandbox restart does not revoke brand approvals: restore the last confirmed snapshot afterward. Initialize a new empty ledger only when the user explicitly resets the brand decisions, not when a runtime is restarted.

## Call moments

### Start of any Brandkit turn

```bash
python3 ${HF_WORKFLOWS}/brand-asset-creation/scripts/brandkit.py state --action get_status
```

(after the restore/initialization step above)

### Lock user-supplied official assets

Immediately after asset analysis, write one input object with the matching top-level slot, then call only its action:

```text
lock_authoritative_logo       {"source_summary": "...", "logo": {...}}
lock_authoritative_palette    {"source_summary": "...", "palette": {...}}
lock_authoritative_typography {"source_summary": "...", "typography": {...}}
```

These actions preserve official assets the user already owns. They do not approve generated work, and an authoritative slot cannot be replaced by a later generated choice.

### Persist visual axes

```json
{
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  }
}
```

Call `set_visual_axes`; later read with `get_visual_axes`.

### Read only the required slot

- `get_logo` before logo placement, export, or logo-dependent revisions.
- `get_palette` for color-dependent work.
- `get_typography` for type-dependent work.
- `get_essential_kit` only when logo, palette, and typography are all genuinely required.

Never use `get_essential_kit` as a universal gate for partial outputs.

### Browse approved downstream elements

Call `list_brandbook_elements`, then use `get_brandbook_element` with:

```json
{ "key": "exact-element-key" }
```

### Approve generated elements independently

After an explicit user selection, write the exact selected object under its slot and call:

```text
approve_logo       {"approval_summary": "...", "logo": {...}}
approve_palette    {"approval_summary": "...", "palette": {...}}
approve_typography {"approval_summary": "...", "typography": {...}}
```

The script assigns the next revision. Do not put generated-but-unapproved work into state.

### Approve a downstream element

Only after explicit approval:

```json
{
  "approval_summary": "User approved the primary mockup.",
  "required_slots": ["logo", "palette"],
  "brandbook_element": {
    "key": "mockup-primary",
    "kind": "mockup",
    "name": "Primary packaging mockup",
    "asset": { "id": "...", "url": "..." }
  }
}
```

Call `approve_brandbook_element`. Declare exactly the foundation slots the output used.

## Recovery

If this conversation previously had approvals but neither a confirmed snapshot nor a complete legacy export is available, stop and report the recovery failure. A narrow `get_status` response is not a restorable snapshot. Never reconstruct state from an account-wide media listing.

## Never

- Never load the entire state file directly when a narrow read action is enough (uploading the bytes does not require reading them into context).
- Never put drafts into an authoritative lock.
- Never delay locking a user-declared official asset.
- Never store generated-but-unapproved assets.
- Never require or request approval for an unrelated missing slot.
- Never ask for combined approval after independent selections.
- Never use this state outside Brandkit.
- Never use user memory or any cross-chat store as a substitute.
