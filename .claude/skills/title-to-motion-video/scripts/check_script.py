"""Lint a voiceover script before spending credits on a voice or running alignment.

    python check_script.py <project> [--wps 2.5]

Reads SCRIPT / SPOKEN from <project>/analysis/align_vo.py and the cut('…') anchors from
<project>/app/src/timeline.ts, and the lineOf(ly, '…') anchors from the plates. Reports:
  - word count and estimated duration at --wps (2.2 calm, 2.5 conversational, 2.8 energetic);
  - tokens the aligner would silently mangle (digits, symbols, hyphens) that have no SPOKEN entry;
  - anchors that match no line, or more than one line (Lyrics.get matches a case-insensitive
    substring anywhere in a line, with curly/straight quotes folded, and takes the FIRST match).
Exit code 1 if anything blocking was found.
"""
import argparse, ast, re, sys
from pathlib import Path


def load_assign(src: str, name: str):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    return None


def fold(s: str) -> str:
    return s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--wps", type=float, default=2.5)
    a = ap.parse_args()
    root = Path(a.project)
    src = (root / "analysis" / "align_vo.py").read_text(encoding="utf-8")
    script = load_assign(src, "SCRIPT") or []
    spoken = load_assign(src, "SPOKEN") or {}
    bad = 0

    words = [w for line in script for w in line.split()]
    n_spoken = sum(len(spoken[w]) if w in spoken else 1 for w in words if not (w in spoken and spoken[w] == []))
    print(f"{len(script)} lines, {len(words)} display words (~{n_spoken} spoken)")
    print(f"estimated voice: {n_spoken / a.wps:.1f} s at {a.wps} w/s  (+0.3 s tail)")

    # tokens the aligner's spoken() would drop or merge
    risky = []
    for i, line in enumerate(script):
        for w in line.split():
            if w in spoken:
                continue
            core = w.strip(".,;:!?\"'“”‘’()…")
            # a bare dash is fine (it becomes a pause); arrows, digits, symbols and hyphenated words are not
            if re.search(r"[0-9$%&@#+=/\\<>*^~|→←]", core) or ("-" in core.strip("-")):
                risky.append((i, w))
    if risky:
        bad += 1
        print("\nTokens needing a SPOKEN entry (the aligner would drop digits/symbols or merge hyphens):")
        for i, w in risky:
            print(f"  line {i + 1}: {w!r}   e.g. SPOKEN[{w!r}] = [...]  (a dash/pause token -> [])")

    # anchors
    tl = root / "app" / "src" / "timeline.ts"
    anchors = []
    if tl.exists():
        anchors += [("timeline cut", q) for q in re.findall(r"cut\(\s*'([^']+)'", tl.read_text(encoding="utf-8"))]
    for f in sorted((root / "app" / "src" / "scenes").glob("*.ts")):
        txt = f.read_text(encoding="utf-8")
        anchors += [(f"scenes/{f.name}", q) for q in re.findall(r"lineOf\(\s*\w+\s*,\s*'([^']+)'", txt)]
    if anchors:
        print(f"\nAnchors ({len(anchors)}):")
        for where, q in anchors:
            hits = [i for i, l in enumerate(script) if fold(q) in fold(l)]
            if not hits:
                bad += 1
                print(f"  MISSING  {where}: '{q}' matches no line  (stale plate or typo)")
            elif len(hits) > 1:
                print(f"  AMBIG    {where}: '{q}' matches lines {[h + 1 for h in hits]} - first one wins")
            else:
                print(f"  ok       {where}: '{q}' -> line {hits[0] + 1}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
