# Third-party components

This package contains no third-party code, fonts or media. `bash scripts/setup.sh --install` runs `npm ci` in `kit/` and downloads the packages below from the npm registry into `kit/node_modules`; each keeps its own licence (every package carries a `LICENSE` file there). The exact versions are locked in `kit/package-lock.json`.

| component | version | licence | used for |
|---|---|---|---|
| puppeteer-core | 25.14.0 | Apache-2.0 | drives headless Chrome (renders every frame) |
| opentype.js | 2.0.0 | MIT | reads glyph outlines for the handwriting module |
| 18 font packages: `@fontsource/abril-fatface`, `anton`, `bagel-fat-one`, `bowlby-one`, `caveat`, `dm-serif-display`, `instrument-serif`, `jetbrains-mono`, `mrs-saint-delafield`, `pacifico`, `playfair-display`, `reenie-beanie`, `rubik-mono-one`, `shrikhand`, `space-mono`; `@fontsource-variable/inter-tight`, `syne`, `unbounded` | 5.3.0 | SIL Open Font License 1.1 | the type of the videos |
| 3 font packages: `@fontsource/homemade-apple`, `permanent-marker`, `yellowtail` | 5.3.0 | Apache-2.0 | the type of the videos |

`kit/package-lock.json` lists 47 packages in all: the 23 above plus 24 that puppeteer-core needs (`@puppeteer/browsers`, `chromium-bidi`, `webdriver-bidi-protocol` under Apache-2.0, `devtools-protocol` under BSD-3-Clause, `yargs` and its helpers, `ws`, `zod` and others under MIT or ISC; opentype.js needs none). Their licences are in the lock file and in each package folder.

The OFL-1.1 and Apache-2.0 fonts may be used in videos you publish; the licences do not make the video itself free of other rights. **The song and its lyrics in a video are not covered by any of these licences:** you need the right to use and publish them (see the Rights section of the package README, and `SKILL.md`).
