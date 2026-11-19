---
name: camera-arc
description: Turn a flat, already-shot clip into a slow, real-feeling 3D camera ARC (orbit) move — 2.5D parallax from per-frame AI depth, rendered by a true perspective camera that orbits the subject on an eased arc with gentle rise, push-in, bank and operator drift. Handles occlusion edges with a clean background plate so the subject's outline stays crisp. Use for "3D camera move", "camera arc/orbit/parallax on this clip", "make this shot feel 3D", "2.5D", "fake a slider/gimbal arc" on any 16:9 or vertical footage.
---

# Camera Arc

One script: `scripts/camera_arc.py`. Runs locally (Apple GPU via moderngl, depth via ONNX/CoreML).

## Setup (once)
```
python3 -m venv ~/.claude/motion-kit/venv-camarc
~/.claude/motion-kit/venv-camarc/bin/pip install onnxruntime opencv-python-headless moderngl numpy pillow huggingface_hub
~/.claude/motion-kit/venv-camarc/bin/python -c "from huggingface_hub import hf_hub_download as d; d('onnx-community/depth-anything-v2-small','onnx/model.onnx',local_dir='$HOME/.claude/motion-kit/models/da2s')"
```

## Run
```
~/.claude/motion-kit/venv-camarc/bin/python scripts/camera_arc.py IN.mp4 OUT.mp4 --start 8 --dur 10 --arc 7 --zfar 1.8 --overscan 1.12
```
Output defaults to 3840×2160 H.264 (crf 15, bt709) with the source audio; `--width/--height` for other sizes (1080×1920 for vertical).

| flag | default | meaning |
|---|---|---|
| `--arc` | 9 | total yaw sweep, degrees. 5–8 = slow, believable; >10 reveals too much behind the subject |
| `--zfar` | 2.0 | far/near depth ratio = parallax strength. 1.6–2.0 for close product/desk shots |
| `--tilt` | 2 | camera rises this many degrees mid-move (real arcs are rarely flat) |
| `--push` | 0.06 | dolly-in over the move |
| `--drift` | 0.12 | low-frequency operator wobble, degrees (0 = robotic) |
| `--direction` | 1 | 1 = orbit left→right, -1 = reverse |
| `--overscan` | 1.16 | crop factor; raise if frame edges show at the ends of the arc |
| `--pivot-pct` | 80 | disparity percentile the camera orbits around (the near subject) |
| `--edge` | 0.018 | depth jump treated as an occlusion edge |

## How it works (why it looks real)
1. **Depth**: Depth Anything V2 Small per frame → robust per-frame normalisation with time-smoothed percentiles → bilateral + EMA so depth doesn't flicker.
2. **Upsample** depth to 960 px with plain cubic. Do NOT use guided/edge-aware upsampling: it copies screen/texture detail into depth and punches holes inside objects.
3. **Two layers**: foreground mesh (depth eroded ~2 px so no background rim rides along) + a background plate. The plate is built by refilling a band on the near side of each depth jump ring-by-ring from the *farthest* neighbour (colour + depth), then blurring only the revealed area so reveals read as out-of-focus background.
4. **Render**: 960-column mesh displaced in the vertex shader, true perspective camera orbiting the pivot with smootherstep easing (zero velocity at both ends), rise, push, bank proportional to velocity, sine-sum drift. Foreground fragments fade out on occlusion edges (no rubber-sheet streaks). Mesh overhangs the frame 10% so edges never show.

## QA checklist
- Grab a 1920×1080 crop around the subject at the first and last frame (biggest reveal) — look for streaks, halos, hard cut-out shapes.
- Fast check of the extremes: render `--dur 1` at the same `--arc` (the whole sweep in 1 s) and inspect the last frame.
- Artifacts at the ends → lower `--arc` or `--zfar` before touching anything else.

## Limits
Monocular depth is relative; thin things (hair, cables) and glass are weak. Best on one clear subject in front of a soft background. Footage with its own big camera move works but the arc adds on top.
