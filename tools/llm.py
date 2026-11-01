#!/usr/bin/env python3
"""Delegate a text task to the provided APIs so Claude Code itself does less of the writing.

Order (auto): ChatGPT on the stationine provider (OPENAI_API_KEY, Responses API)
-> Claude on Sub2API (SUB2API_API_KEY, Messages API). Falls through on rate limits,
5xx, timeouts or missing keys. The answer goes to stdout (or --out); which model served it
goes to stderr.

Usage:
  python tools/llm.py "Write a 60-second voiceover about ..." [--out vo.txt]
  python tools/llm.py --prompt-file brief.md --system "You are a scriptwriter." --out script.md
  cat notes.txt | python tools/llm.py - --model claude          # gpt | claude | auto | <model id>

Env (repo .env): OPENAI_API_KEY, SUB2API_API_KEY, LLM_BASE_URL (default https://space.stationine.com/v1),
LLM_GPT_MODELS (default "gpt-5.5,gpt-5.6-terra,gpt-6-astra,gpt-5.6-sol,gpt-6.1-sol,gpt-5.6"), LLM_CLAUDE_MODELS (default "claude-sonnet-4-6,claude-haiku-4-5").
"""
import argparse, json, os, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

UA = "curl/8.5.0 fizzaynr-llm/1.0"   # provider is behind Cloudflare; Python's default UA is blocked


def root():
    try:
        return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True,
                                            cwd=Path(__file__).resolve().parent).strip())
    except Exception:
        return Path(__file__).resolve().parents[1]


def load_env(p):
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class Skip(Exception):
    """Try the next model."""


def request(url, headers, body, timeout):
    h = {"Content-Type": "application/json", "User-Agent": UA, **headers}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="POST")
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:300]
        if e.code in (408, 409, 425, 429) or e.code >= 500:
            raise Skip(f"HTTP {e.code}: {msg}")
        if e.code == 404 and "model" in msg.lower():
            raise Skip(f"HTTP 404: {msg}")
        sys.exit(f"HTTP {e.code}: {msg}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise Skip(str(e))


def call_gpt(base, key, model, system, prompt, max_tokens, timeout):
    body = {"model": model, "input": prompt, "stream": True, "max_output_tokens": max_tokens}
    if system:
        body["instructions"] = system
    out = []
    with request(f"{base}/responses", {"Authorization": f"Bearer {key}"}, body, timeout) as r:
        for raw in r:
            line = raw.decode(errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                ev = json.loads(data)
            except json.JSONDecodeError:
                continue
            t = ev.get("type", "")
            if t == "response.output_text.delta":
                out.append(ev.get("delta", ""))
            elif t in ("error", "response.failed"):
                raise Skip(json.dumps(ev)[:300])
    text = "".join(out).strip()
    if not text:
        raise Skip("empty answer")
    return text


def call_claude(base, key, model, system, prompt, max_tokens, timeout):
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    headers = {"x-api-key": key, "Authorization": f"Bearer {key}", "anthropic-version": "2023-06-01"}
    with request(f"{base}/messages", headers, body, timeout) as r:
        d = json.loads(r.read())
    text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text").strip()
    if not text:
        raise Skip(f"empty answer: {json.dumps(d)[:200]}")
    return text


def main():
    load_env(root() / ".env")
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="?", help="prompt text, or - for stdin")
    ap.add_argument("--prompt-file")
    ap.add_argument("--system", help="system text, or a path to a file")
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL", "auto"))
    ap.add_argument("--max-tokens", type=int, default=int(os.environ.get("LLM_MAX_TOKENS", "8000")))
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--out")
    a = ap.parse_args()

    if a.prompt_file:
        prompt = Path(a.prompt_file).read_text(encoding="utf-8")
    elif a.prompt in (None, "-"):
        prompt = sys.stdin.read()
    else:
        prompt = a.prompt
    if not prompt.strip():
        sys.exit("No prompt given.")
    system = a.system
    if system and len(system) < 400 and Path(system).is_file():
        system = Path(system).read_text(encoding="utf-8")

    base = os.environ.get("LLM_BASE_URL", "https://space.stationine.com/v1").rstrip("/")
    gpt_key, claude_key = os.environ.get("OPENAI_API_KEY"), os.environ.get("SUB2API_API_KEY")
    gpts = [m.strip() for m in os.environ.get("LLM_GPT_MODELS", "gpt-5.5,gpt-5.6-terra,gpt-6-astra,gpt-5.6-sol,gpt-6.1-sol,gpt-5.6").split(",") if m.strip()]
    claudes = [m.strip() for m in os.environ.get("LLM_CLAUDE_MODELS", "claude-sonnet-4-6,claude-haiku-4-5").split(",") if m.strip()]
    if a.model == "gpt":
        plan = [("gpt", m) for m in gpts]
    elif a.model == "claude":
        plan = [("claude", m) for m in claudes]
    elif a.model == "auto":
        plan = [("gpt", m) for m in gpts] + [("claude", m) for m in claudes]
    else:
        plan = [("claude" if a.model.startswith("claude") else "gpt", a.model)]

    errors = []
    for kind, model in plan:
        key = gpt_key if kind == "gpt" else claude_key
        if not key:
            errors.append(f"{model}: {'OPENAI_API_KEY' if kind == 'gpt' else 'SUB2API_API_KEY'} not set")
            continue
        fn = call_gpt if kind == "gpt" else call_claude
        for attempt in (1, 2):
            try:
                t0 = time.time()
                text = fn(base, key, model, system, prompt, a.max_tokens, a.timeout)
                print(f"[llm] served by {model} in {time.time() - t0:.1f}s", file=sys.stderr)
                if a.out:
                    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
                    Path(a.out).write_text(text + "\n", encoding="utf-8")
                    print(f"[llm] wrote {a.out}", file=sys.stderr)
                else:
                    print(text)
                return
            except Skip as e:
                errors.append(f"{model} (try {attempt}): {e}")
                if attempt == 1 and "rate" not in str(e).lower():
                    time.sleep(3)
                else:
                    break
    sys.exit("[llm] all providers failed:\n  " + "\n  ".join(errors))


if __name__ == "__main__":
    main()
