#!/usr/bin/env python3
"""
diagnose_legacy_xapi_package.py

Sanity checks for a converted hybrid Rise package:

- index.html and index_lms.html exist.
- tincan.xml exists.
- lib/tincan.js and lib/lms.js exist.
- index.html initialises window.LMSProxy = lms().
- index.html uses pick(LMSProxySelections, window.LMSProxy, …).
- Warns if scormcontent/ or scormdriver/ strings remain.
"""

import sys
from pathlib import Path


def check(path: Path, label: str):
    if path.exists():
        print(f"[OK] {label}: {path}")
        return True
    else:
        print(f"[FAIL] {label} missing: {path}")
        return False


def main(folder):
    root = Path(folder)

    print(f"\n=== Diagnosing hybrid package at {root} ===\n")

    ok = True
    ok &= check(root / "index.html", "index.html")
    ok &= check(root / "index_lms.html", "index_lms.html")
    ok &= check(root / "tincan.xml", "tincan.xml")
    ok &= check(root / "lib" / "tincan.js", "lib/tincan.js")
    ok &= check(root / "lib" / "lms.js", "lib/lms.js")

    if not (root / "index.html").exists():
        print("\nindex.html missing, cannot continue wiring checks.")
        return

    idx_txt = (root / "index.html").read_text(encoding="utf-8", errors="ignore")

    print("\n=== Wiring checks (index.html) ===")

    if "window.LMSProxy = lms();" in idx_txt:
        print("[OK] window.LMSProxy initialised in index.html")
    else:
        print("[FAIL] window.LMSProxy initialisation missing in index.html")
        ok = False

    if "pick(LMSProxySelections, window.LMSProxy" in idx_txt:
        print("[OK] LMSProxySelections uses window.LMSProxy")
    else:
        print("[FAIL] LMSProxySelections does not use window.LMSProxy (still window.parent?)")
        ok = False

    print("\n=== Scan for scormcontent/ or scormdriver/ references ===")
    bad_refs = []
    for f in root.rglob("*"):
        if f.suffix.lower() in (".html", ".js") and f.is_file():
            txt = f.read_text(encoding="utf-8", errors="ignore")
            if "scormcontent/" in txt or "scormdriver/" in txt:
                bad_refs.append(f.relative_to(root))

    if bad_refs:
        print("[WARN] References to scormcontent/ or scormdriver/ remain in:")
        for f in bad_refs[:20]:
            print(f"   - {f}")
    else:
        print("[OK] No scormcontent/ or scormdriver/ references found in text files")

    print("\n=== Overall ===")
    if ok:
        print("Looks structurally sound for legacy xAPI tracking.")
    else:
        print("Some critical wiring checks failed. Fix before uploading.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python diagnose_legacy_xapi_package.py OUTPUT_FOLDER")
        sys.exit(1)
    main(sys.argv[1])
