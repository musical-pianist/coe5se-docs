"""Finds the CoE5 Modding extension the site's hovers and code colours are read from.

The published site reads only the released extension: extension.json at the site's root pins its
version and SHA-256, and the build downloads that file from Open VSX, so a hover reaches the site
through an extension release and no other way. A local preview (the docs editor, mkdocs serve) reads
coe5-modding.vsix at the site's root instead, the build scripts/gen_docs_commands.py in the CoE5SE
sources writes there and git ignores; the footer then says "local build". In CI (CI set, as GitHub
Actions and GitLab set it) the pinned release is used even when a local build is present.
"""

import functools
import hashlib
import json
import os
import urllib.request
from pathlib import Path

LOCAL_VSIX = "coe5-modding.vsix"
PIN = "extension.json"
OPEN_VSX = "https://open-vsx.org/api/{publisher}/{name}/{version}/file/{publisher}.{name}-{version}.vsix"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@functools.cache
def find_extension_vsix(root):
    """(path, is_local) of the .vsix the build reads, for the site at root."""
    root = Path(root)
    local = root / LOCAL_VSIX
    in_ci = bool(os.environ.get("CI"))
    if local.is_file() and not in_ci:
        return local, True
    pin = json.loads((root / PIN).read_text(encoding="utf-8"))
    cached = root / ".cache" / f"{pin['publisher']}.{pin['name']}-{pin['version']}.vsix"
    if cached.is_file() and sha256(cached) == pin["sha256"]:
        return cached, False
    if not in_ci:
        raise SystemExit(f"{local} is missing: run scripts/gen_docs_commands.py in the CoE5SE sources "
                         "to build it for a local preview")
    url = OPEN_VSX.format(**pin)
    # urllib takes HTTPS_PROXY from the environment: the homelab build sets it to the PIA proxy.
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    got = hashlib.sha256(data).hexdigest()
    if got != pin["sha256"]:
        raise SystemExit(f"{url}: SHA-256 {got}, but {PIN} pins {pin['sha256']}")
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data)
    return cached, False
