#!/usr/bin/env python3
"""Install Rhubarb Lip Sync (v1.13.0) once and print the path to the binary.

  python setup_rhubarb.py            -> installs into ~/.rbdigital/rhubarb-1.13.0/ (if missing), prints path
  python setup_rhubarb.py --check    -> prints path or exits 1 (no download)

Works on Windows, macOS and Linux. Needs internet the first time (~90 MB zip from
github.com/DanielSWolf/rhubarb-lip-sync releases). Idempotent.
"""
import os, platform, shutil, stat, subprocess, sys, tempfile, urllib.request, zipfile

VER = "1.13.0"
ROOT = os.path.join(os.path.expanduser("~"), ".rbdigital", f"rhubarb-{VER}")
EXE = "rhubarb.exe" if os.name == "nt" else "rhubarb"


def osname():
    s = platform.system()
    if s == "Windows":
        return "Windows"
    if s == "Darwin":
        return "macOS"
    return "Linux"


def find():
    for cand in (shutil.which("rhubarb"),):
        if cand:
            return cand
    for dirpath, _, files in os.walk(ROOT):
        if EXE in files:
            return os.path.join(dirpath, EXE)
    return None


def works(path):
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=30)
        return r.returncode == 0 and "Rhubarb" in (r.stdout + r.stderr)
    except Exception:
        return False


def install():
    url = (f"https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v{VER}/"
           f"Rhubarb-Lip-Sync-{VER}-{osname()}.zip")
    os.makedirs(ROOT, exist_ok=True)
    tmp = os.path.join(tempfile.mkdtemp(), "rhubarb.zip")
    print(f"downloading {url}", file=sys.stderr)
    try:
        urllib.request.urlretrieve(url, tmp)
    except Exception as e:
        # some sandboxes only allow curl through the proxy
        if shutil.which("curl") and subprocess.run(["curl", "-sSL", "-o", tmp, url]).returncode == 0:
            pass
        else:
            sys.exit(f"download failed: {e}\nDownload manually: {url}\nand extract it into {ROOT}")
    with zipfile.ZipFile(tmp) as z:
        z.extractall(ROOT)
    p = find()
    if not p:
        sys.exit("rhubarb binary not found after extract")
    if os.name != "nt":
        os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if osname() == "macOS":
        subprocess.run(["xattr", "-dr", "com.apple.quarantine", ROOT], capture_output=True)
    return p


def main():
    p = find()
    if p and works(p):
        print(p)
        return
    if "--check" in sys.argv:
        sys.exit(1)
    p = install()
    if not works(p):
        sys.exit(f"rhubarb installed at {p} but does not run on this machine")
    print(p)


if __name__ == "__main__":
    main()
