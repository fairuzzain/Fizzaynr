# Fizzaynr

Remotion project for a short animated hook: a photo with a voiceover.

- **Format:** 1440×1080 (4:3), 24000/1001 fps (23.976)
- **Composition:** `Hook` (`src/Hook.tsx`)

## Usage

```bash
npm install
npm run dev      # open Remotion Studio at http://localhost:3000
npm run render   # render out/hook.mp4
```

Put your photo and voiceover files in `public/`. Then set the `photo` and `voiceover` props, for example `"photo.jpg"` and `"voiceover.mp3"`, in `src/Hook.tsx` or in the Studio props panel. Set `durationInSeconds` to match the voiceover.
