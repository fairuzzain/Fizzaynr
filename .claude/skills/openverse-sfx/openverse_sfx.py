"""Search and download sound effects from Openverse (https://api.openverse.org/v1/).

No key needed for basic searches (anonymous: ~100 requests/day, page_size <= 20).

  python openverse_sfx.py search "rising whoosh" [--n 10] [--license cc0|commercial|all] [--max-dur 5]
  python openverse_sfx.py get "rising whoosh" --n 3 --out sfx/            # download top N + credits
  python openverse_sfx.py id <uuid> --out sfx/                            # download one result by id

Every download appends a line to <out>/CREDITS.txt (title, creator, licence, source) so CC-BY
sounds can be credited. Default licence filter is cc0 (no attribution needed).
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.openverse.org/v1/audio/"
UA = {"User-Agent": "motion-claude-sfx/1.0"}


def _get(url, tries=3):
    req = urllib.request.Request(url, headers=UA)
    for i in range(tries):  # the API is sometimes slow to answer
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except (TimeoutError, OSError):
            if i == tries - 1:
                raise


def search(q, n=10, lic="cc0", max_dur=None):
    params = {"q": q, "page_size": min(max(n * 2, n), 20)}
    if lic == "cc0":
        params["license"] = "cc0"
    elif lic == "commercial":
        params["license_type"] = "commercial"
    res = _get(API + "?" + urllib.parse.urlencode(params)).get("results", [])
    out = []
    for r in res:
        dur = (r.get("duration") or 0) / 1000.0
        if max_dur and dur and dur > max_dur:
            continue
        out.append({
            "id": r["id"], "title": r.get("title"), "dur": round(dur, 2),
            "license": f'{r.get("license")} {r.get("license_version") or ""}'.strip(),
            "creator": r.get("creator"), "url": r.get("url"), "filetype": r.get("filetype"),
            "source": r.get("foreign_landing_url"),
            "tags": [t["name"] for t in (r.get("tags") or [])][:8],
        })
    return out[:n]


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "_", (s or "sound").lower()).strip("_")[:40] or "sound"


def download(item, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = item.get("filetype") or Path(urllib.parse.urlparse(item["url"]).path).suffix.lstrip(".") or "mp3"
    path = out_dir / f'{_slug(item["title"])}_{item["id"][:8]}.{ext}'
    req = urllib.request.Request(item["url"], headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        path.write_bytes(r.read())
    with open(out_dir / "CREDITS.txt", "a", encoding="utf-8") as f:
        f.write(f'{path.name}: "{item["title"]}" by {item["creator"]} ({item["license"]}) {item["source"]}\n')
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["search", "get", "id"])
    ap.add_argument("query")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--license", default="cc0", choices=["cc0", "commercial", "all"])
    ap.add_argument("--max-dur", type=float)
    ap.add_argument("--out", default="sfx")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.cmd == "id":
        r = _get(API + a.query + "/")
        item = {"id": r["id"], "title": r.get("title"), "url": r["url"], "filetype": r.get("filetype"),
                "creator": r.get("creator"), "source": r.get("foreign_landing_url"),
                "license": f'{r.get("license")} {r.get("license_version") or ""}'.strip()}
        print(download(item, a.out))
        return

    items = search(a.query, a.n, a.license, a.max_dur)
    if not items:
        sys.exit(f"no matches for {a.query!r} (licence {a.license}); try other words or --license all")
    if a.cmd == "search":
        if a.json:
            print(json.dumps(items, indent=1))
        else:
            for i, it in enumerate(items, 1):
                print(f'{i:2}. {it["dur"]:5.2f}s  {it["license"]:10} {it["title"]}  [{it["id"]}]  {",".join(it["tags"])}')
        return
    for it in items:
        try:
            print("saved", download(it, a.out))
        except Exception as e:  # one bad CDN link should not stop the rest
            print("skip", it["title"], e, file=sys.stderr)


if __name__ == "__main__":
    main()
