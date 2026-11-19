#!/usr/bin/env python3
"""
ACBEATZ / MH8 AI Music Production Helper CLI
Focused purely on Suno prompt engineering, hook indexing, style search, and prompt validation.
No telemetry, no email collection, no hashing, no KV storage.
"""
import sys
import os
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'references')

def search_hooks(query: str):
    """Searches reference files for matching bracket hooks."""
    results = []
    q = query.lower()
    if not os.path.exists(REFERENCES_DIR):
        print(f"References directory not found at {REFERENCES_DIR}")
        return []

    for fname in os.listdir(REFERENCES_DIR):
        if fname.endswith(('.txt', '.md', '.json')):
            fpath = os.path.join(REFERENCES_DIR, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                    for line in fp:
                        if q in line.lower() and '[' in line and ']' in line:
                            # Extract bracket tokens
                            found_brackets = re.findall(r'\[.*?\]', line)
                            for b in found_brackets:
                                if q in b.lower() and b not in results:
                                    results.append(b)
            except Exception:
                pass
    return results[:35]

def validate_prompt(style_prompt: str, lyrics: str = "") -> dict:
    """Validates Suno prompt against MH8 production principles."""
    char_count = len(style_prompt)
    brackets = re.findall(r'\[(.*?)\]', style_prompt)
    has_mono_bass = any('mono' in b.lower() and 'bass' in b.lower() for b in brackets) or 'mono below' in style_prompt.lower()
    has_lufs = any('lufs' in b.lower() for b in brackets)
    has_drums = any(k in style_prompt.lower() for k in ['drum', 'kick', 'snare', 'hat', 'percussion'])
    has_vocal = any(k in style_prompt.lower() for k in ['vocal', 'voice', 'intimate', 'up front', 'falsetto', 'rap', 'belt'])
    has_master = any(k in style_prompt.lower() for k in ['master', 'ssl', 'neve', 'pultec', 'api', 'limiter', 'clipper'])

    status = "OPTIMAL" if char_count <= 1000 and len(brackets) >= 4 else "REVIEW"

    suggestions = []
    if char_count > 1000:
        suggestions.append(f"Prompt length ({char_count} chars) exceeds Suno's 1000 character limit. Trim down.")
    if not has_mono_bass:
        suggestions.append("Add stereo rule: [Stereo Rule: Keep Bass Mono | sub centered] to protect club/phone playback.")
    if not has_lufs:
        suggestions.append("Specify master target, e.g. [Master: Streaming | Target -14 LUFS | True Peak -1.0dB].")
    if not has_master:
        suggestions.append("Consider a hardware console master hook, e.g. [Master: SSL 4000 G-Bus Glue] or [Master: Neve Console Warmth].")

    return {
        "status": status,
        "style_character_count": char_count,
        "character_limit_ok": char_count <= 1000,
        "detected_bracket_count": len(brackets),
        "detected_modules": {
            "mono_bass_rule": has_mono_bass,
            "master_lufs": has_lufs,
            "hardware_mastering": has_master,
            "drum_architecture": has_drums,
            "vocal_profile": has_vocal
        },
        "suggestions": suggestions
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: mh8_tools.py [search|validate] [args...]")
        return

    cmd = sys.argv[1].lower()
    if cmd == "search":
        if len(sys.argv) < 3:
            print("Provide search query. Example: mh8_tools.py search pultec")
            return
        query = " ".join(sys.argv[2:])
        hooks = search_hooks(query)
        if not hooks:
            print(f"No hooks found matching: {query}")
        else:
            print(f"Found {len(hooks)} matching MH8 hooks:")
            for h in hooks:
                print(f"  {h}")

    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Provide style prompt text or file path to validate.")
            return
        arg = sys.argv[2]
        if os.path.isfile(arg):
            with open(arg, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        else:
            content = " ".join(sys.argv[2:])
        report = validate_prompt(content)
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
