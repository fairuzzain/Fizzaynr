# Exact Brandkit logo-export payloads

Use with `logo-export --input`:

```json
{
  "name": "northline-symbol",
  "logo_svg": "https://replace-with-selected-recraft-result.svg",
  "delivery": "user",
  "replacements": [],
  "include_monochrome": false
}
```

For an explicitly requested one-color export, add `"single_color": "#101820"`.

For explicitly requested black/white production variants, set `"include_monochrome": true` and add `"primary_color": "#00AEEF"`.

Upload returned SVG and PNG paths together from the sandbox via `media_upload` → `curl` PUT → `media_confirm` (SVGs confirm as `type: "file"` and keep their exact bytes; PNGs confirm as `type: "image"`). Use the confirmed URLs exactly; never label a rasterized `.png` as SVG.
