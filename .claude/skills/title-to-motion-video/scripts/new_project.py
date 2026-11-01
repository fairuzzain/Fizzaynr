"""Create a fresh Motion-as-Code project for a new video.

    python new_project.py "My Video Title" [--slug NAME] [--kit PATH] [--root PATH] [--no-venv]

  --slug     folder name (default: slugified title). If the folder exists the script stops:
             continue in that project, or pass a new --slug.
  --kit      template kit (default: $MOTION_KIT or ~/Documents/Motion_as_kit)
  --root     where projects live (default: ~/Documents/Motion_videos)
  --no-venv  skip creating/checking the shared analysis venv

Copies the template (without old renders, the old voiceover, caches or unused data), writes a
project CLAUDE.md for the title-to-motion-video workflow, adds the generic `animatic` plate,
patches known kit pitfalls, picks a free preview port, and makes sure the shared analysis venv
(<root>/.venv with numpy + onnxruntime) exists. The last lines are KEY=VALUE pairs to use later.
Output is ASCII only (the Windows console is cp1252).
"""
import argparse, json, os, re, shutil, socket, subprocess, sys
from pathlib import Path

HOME = Path.home()
SKILL = Path(__file__).resolve().parent.parent
TOP_SKIP = {"out", ".vite", "__pycache__", ".git"}

PROJECT_CLAUDE_MD = """# {title} - a Motion-as-Code video project

Created from the Motion as Code kit by the `title-to-motion-video` skill. Follow that skill's
stages; this file replaces the kit's setup-only instructions.

- The voiceover is part of this workflow: generating it with ElevenLabs is allowed **after the
  user approved the script and the credit estimate** (skill Stage 3). Never regenerate on your own
  to "retry" - every call spends credits.
- Never run a full video render (`render.ts video`, `bun run render`) unless the user asks for it
  in this conversation. Stills and contact sheets (`render.ts stills` / `sheet`) are fine at any time.
- Run the SFX mix / mux only when the user asks.
- Do not edit `app/src/engine/`.
- Preview: `.claude/launch.json` here (port {port}); pass `--url http://localhost:{port}` to every
  `render.ts` call while that preview runs, so stills come from this project.
- Analysis scripts: `PYTHONIOENCODING=utf-8 "{venv}" analysis/<script>.py` (no uv on this machine).
"""


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48].rstrip("-") or "video"


def make_ignore(kit: Path):
    kit = kit.resolve()

    def ignore(src, names):
        here = Path(src).resolve()
        if here == kit:  # top level only: node_modules has its own out/ and .git folders
            return {n for n in names if n in TOP_SKIP}
        if here == kit / "audio":
            return {n for n in names if n.lower() == "voiceover.mp3"}
        if here == kit / "data":
            return {n for n in names if n == "voiceover.words.json"}  # unused leftover
        if here == kit / ".claude":
            return {n for n in names if n in ("launch.json", "settings.local.json")}
        return {n for n in names if n == "__pycache__"}

    return ignore


def patch(path: Path, pattern: str, repl: str, flags=0, already: str | None = None) -> str:
    if not path.exists():
        return f"skip (missing): {path.name}"
    txt = path.read_text(encoding="utf-8")
    if already and already in txt:
        return f"already fixed in template: {path.name}"
    new, n = re.subn(pattern, repl, txt, flags=flags)
    if n:
        path.write_text(new, encoding="utf-8")
        return f"patched: {path.name}"
    return f"WARNING pattern not found, check by hand: {path.name}"


def free_port(start: int) -> int:
    for p in range(start, start + 200):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("title")
    ap.add_argument("--kit", default=os.environ.get("MOTION_KIT", str(HOME / "Documents" / "Motion_as_kit")))
    ap.add_argument("--root", default=str(HOME / "Documents" / "Motion_videos"))
    ap.add_argument("--slug")
    ap.add_argument("--no-venv", action="store_true")
    a = ap.parse_args()

    kit, root = Path(a.kit), Path(a.root)
    if not (kit / "app" / "src" / "engine").is_dir():
        sys.exit(f"template kit not found at {kit} (set --kit or MOTION_KIT)")
    slug = a.slug or slugify(a.title)
    dst = root / slug
    if dst.exists():
        sys.exit(f"{dst} already exists - continue in that project, or pass a different --slug")
    root.mkdir(parents=True, exist_ok=True)

    print(f"copying {kit} -> {dst} (node_modules and models included, ~230 MB)...")
    shutil.copytree(kit, dst, ignore=make_ignore(kit), ignore_dangling_symlinks=True)
    (dst / "out" / "wip").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SKILL / "assets" / "animatic.ts", dst / "app" / "src" / "scenes" / "animatic.ts")
    print("  added: app/src/scenes/animatic.ts (placeholder plate)")

    # --- known pitfalls of the template (idempotent) ---
    print("  " + patch(dst / "analysis" / "sfx_mix.py", r"^DUR = [0-9.]+\s*$",
                       'DUR = json.loads((ROOT / "data" / "audio.json").read_text(encoding="utf-8"))["duration"]',
                       re.M, already='DUR = json.loads('))
    print("  " + patch(dst / "app" / "scripts" / "render.ts",
                       r"if \(withAudio\) args\.push\('-c:a', 'aac'",
                       "if (withAudio) args.push('-af', 'apad', '-c:a', 'aac'", already="'-af', 'apad'"))
    print("  " + patch(dst / "analysis" / "audio_vo.py", r"y = np\.frombuffer\(raw, dtype=np\.float32\)",
                       "TAIL = 0.3  # silent seconds after the voice (the last plate holds into it)\n"
                       "y = np.concatenate([np.frombuffer(raw, dtype=np.float32), np.zeros(int(TAIL * SR), dtype=np.float32)])",
                       already="TAIL ="))

    # --- shared analysis venv ---
    venv = root / ".venv"
    py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not a.no_venv:
        if not py.exists():
            print(f"creating analysis venv at {venv}...")
            subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        if subprocess.run([str(py), "-c", "import numpy, onnxruntime"], capture_output=True).returncode:
            print("installing numpy + onnxruntime into the venv...")
            subprocess.run([str(py), "-m", "pip", "install", "-q", "numpy", "onnxruntime"], check=True)

    # --- preview config + project instructions ---
    port = free_port(5174)
    app = (dst / "app").as_posix()
    name = f"motion-{slug}"
    entry = {"name": name, "runtimeExecutable": "bun",
             "runtimeArgs": [f"{app}/node_modules/vite/bin/vite.js", app, "--port", str(port), "--strictPort"],
             "port": port}
    (dst / ".claude").mkdir(exist_ok=True)
    (dst / ".claude" / "launch.json").write_text(json.dumps({"version": "0.0.1", "configurations": [entry]}, indent=2), encoding="utf-8")
    (dst / "CLAUDE.md").write_text(PROJECT_CLAUDE_MD.format(title=a.title, port=port, venv=py.as_posix()), encoding="utf-8")
    print("  wrote: CLAUDE.md (project rules), .claude/launch.json")
    print("  note: data/lyrics.json + audio.json and the scenes are still the template's until Stage 4/5 replace them")

    print(f"PROJECT={dst}")
    print(f"VENV_PYTHON={py}")
    print(f"PREVIEW_NAME={name}")
    print(f"PREVIEW_PORT={port}")
    print("LAUNCH_ENTRY=" + json.dumps(entry))


if __name__ == "__main__":
    main()
