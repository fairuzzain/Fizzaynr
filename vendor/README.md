# vendor/

Put external kits here (ignored by git). Defaults the skills look for:

| Kit | Default path | Used by | Override |
|---|---|---|---|
| Motion as Code kit (incl. `nexabot/nexabot.ts`, `.env.nexabot`) | `vendor/Motion_as_kit` | travelcut, recap-reel, collage-motion, window-pass-through, codex-image, title-to-motion-video, vox-colored-nexabot | `MOTION_KIT`, `NEXABOT_TS` |
| video-3d kit | `vendor/video-3d-kit` | video-3d, video-3d-toons | `VIDEO3D_KIT` |

Copy them from your PC (`C:\Users\fairus\Documents\Motion_as_kit`, `C:\Users\fairus\.video-3d-kit`)
or set the override variables in `.env` to where they live.
