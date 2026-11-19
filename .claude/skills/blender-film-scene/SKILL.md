---
name: blender-film-scene
description: Build a short cinematic film scene in Blender through the MCP for Blender connection - shot plan, set, light, animation, cameras, test renders, final render and sound. Use when the user wants Claude to make a Blender scene, a 3D shot or a short animated film, or to fix one that does not look real yet.
---

# Blender film scene

You are directing and building a short film scene inside Blender through the MCP for Blender tools (`execute_blender_code`, scene info, viewport screenshots, asset search). You write Python that runs inside the user's open Blender file. The user judges the result with their eyes, so every claim you make about how the scene looks must come from a render or a screenshot you actually looked at.

This skill came out of a real project (a fly landing on a watchmaker's pocket watch, five shots, about 15 seconds). It took many rounds of fixes. The rules below are the fixes, written down so the next scene needs fewer rounds.

## Before you touch Blender

1. **Shot plan first, one line per shot.** Write the film as a numbered list: what we see, camera size and move, roughly how many seconds. Nothing else. The user reads it and changes it line by line. Only build after they agree.
2. **Pick the hero and the light.** One subject the eye follows (the fly, the car, the cup) and one motivated light source (a desk lamp, low sun through a window). Write both down. Most "looks like a render" problems are a missing hero or light that comes from nowhere.
3. **Ask the user to save their file.** `execute_blender_code` runs any Python. Save before big steps and keep numbered copies (`scene_v1.blend`, `scene_v2.blend`).

## Build order

Work in this order and show the user a picture after each step. Do not jump ahead to details.

1. **Blockout.** Real-world scale in metres (a desk is 0.75 m high, a pocket watch is 5 cm across). Simple shapes for the set, the hero and the cameras. Render one grey frame per planned shot so the user sees the framing before anything is pretty.
2. **Set and assets.** Replace blockout pieces with real assets: free models from BlenderKit or Poly Haven (CC0 models, HDRIs and textures; Poly Haven can be switched on in the MCP for Blender sidebar). Download one asset per call; two big downloads in one call can time out. After every import, check the scale and the position numerically (bounding box), not by guessing.
3. **Materials.** Check every hero material by rendering it close. Typical traps:
   - Fur, hair and thin parts with Transmission turned up render white. Use dark base colours, low specular, transmission 0.
   - Imported characters can arrive with pale or grey skin because of a desaturation input in their node group. Check the node values, or replace the skin with a simple Principled material with subsurface.
   - Glass needs something behind it to look like glass. Give a window a dark or detailed interior.
4. **Light.** One key from the motivated source, a soft fill, an HDRI only for reflections and sky. Volumetric haze is strong: start with a density around 0.02-0.05, not 0.5. Animate exposure with keyframes when the light changes during a shot instead of letting it blow out.
5. **Animation.** Give every motion weight and a reason:
   - Paths for flying or moving objects: make the path smooth first, then add small noise. Take the orientation from the smoothed path, or the object flips.
   - Vehicles and heavy objects: compute the motion with simple physics (speed, gravity, ramps) instead of hand keys. It reads as real.
   - People: a still, perfectly timed figure looks like a mannequin. Stagger left and right (one hand leads, the other follows), let the head and shoulders move first, add a little tremble. For complex body motion, recommend motion capture from a phone video (Rokoko Vision, QuickMagic, Move AI) and retarget only the upper body. Single-camera mocap loses depth, so push the arms forward afterwards until they clear the head.
   - Camera moves: real cameras shake a little. Add a small noise modifier to camera rotation (and more for vehicle-mounted shots). A perfectly smooth camera is the most common reason a shot looks CG.
6. **Cameras.** One camera per shot, bound with timeline markers. Choose the lens for the feeling (24-28 mm for action close to the subject, 45-85 mm for calm detail). Set focus distance on the hero. Check that no prop crosses the lens during the shot.

## Test renders - the loop

- Preview renders run as a separate background Blender process from a saved copy of the file (`blender -b copy.blend -o folder/f_#### -F PNG -a`), so the user's Blender stays usable. Use separate `-f` flags for single frames; a comma-separated list does not work.
- Previews: 30-40 % resolution, 12-16 samples. Turn **Persistent Data off** for test renders inside the UI, or material changes will not show up and you will judge an old image.
- Look at every preview yourself before you describe it. Make a contact sheet (ffmpeg `tile`) of key frames and check: hero visible and in focus, light direction, scale, intersections (hands through heads, objects through walls), and whether each shot reads in one second.
- Show the user the video, not just a description. When they point at a problem, check the exact frame before you answer.
- If a test shows something the user did not ask about, fix it only if it clearly breaks the shot. Otherwise mention it in one line.

## Final render

- Same background-process method, full resolution, 32-128 samples with denoising, motion blur on for anything fast.
- GPU memory (8 GB cards): close OBS, streaming tools and video editors first. Set a texture size limit (2048), use tiles, and keep motion blur steps low. If the render crashes with a CUDA error, these are the first suspects. Use OptiX on NVIDIA cards.
- Thousands of small animated objects (debris, glass shards) slow every frame down, even before they appear. Render the frames before they appear from a copy with that collection excluded.
- Write a small retry script that checks which frames exist and continues from the first missing one.

## Sound and delivery

- Sound effects can come from Openverse or Freesound. Keep a credits list for every CC-BY sound and give it to the user.
- Mix to around -16 LUFS with a limiter for social media.
- Export one master, then crop versions for 16:9, 9:16, 1:1 and 4:5 with ffmpeg. Check that titles and the hero stay inside the frame in every version.

## How to talk to the user

- Short status lines, no essays. Say what you changed and what to look at.
- Never say "done" or "it works" before you have rendered and looked at the frames.
- If you were wrong about what is on screen, say so plainly and fix it.
