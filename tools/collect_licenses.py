"""
Collect the licence texts of every installed Python package into ./build_licenses
so they can be shipped next to DeskLedger.exe (MIT/BSD/Apache licences require the
licence text to travel with redistributed copies).

Run from the project root inside the build virtual environment:
    python tools/collect_licenses.py
"""

import re
import shutil
import sys
from importlib import metadata
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "build_licenses"
PATTERN = re.compile(r"(^|[/\\])(licen[cs]e|copying|notice|authors)[^/\\]*$", re.I)
# Build tooling that is not shipped inside DeskLedger.exe
SKIP = {
    "pip",
    "setuptools",
    "wheel",
    "pyinstaller",
    "pyinstaller-hooks-contrib",
    "altgraph",
    "pefile",
    "pywin32-ctypes",
}


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    summary = []
    for dist in sorted(
        metadata.distributions(), key=lambda d: (d.metadata["Name"] or "").lower()
    ):
        name = dist.metadata["Name"]
        if not name or name.lower() in SKIP:
            continue
        files = [f for f in (dist.files or []) if PATTERN.search(str(f))]
        dest = OUT / re.sub(r"[^\w.-]", "_", name)
        copied = 0
        for f in files:
            src = Path(dist.locate_file(f))
            if src.is_file():
                dest.mkdir(exist_ok=True)
                shutil.copy2(src, dest / src.name)
                copied += 1
        lic = dist.metadata.get("License-Expression") or dist.metadata.get("License") or ""
        lic = lic.strip().splitlines()[0][:60] if lic.strip() else ""
        summary.append(f"{name} {dist.version} | {lic or 'see licence files'} | {copied} file(s)")
    (OUT / "_INDEX.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    missing = [s for s in summary if s.endswith("| 0 file(s)")]
    print(f"Collected licences for {len(summary)} packages into {OUT}")
    if missing:
        print("No licence file shipped by:\n  " + "\n  ".join(missing))
        print("Check these by hand and list them in THIRD_PARTY_NOTICES.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
