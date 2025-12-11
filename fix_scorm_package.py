#!/usr/bin/env python3
"""
fix_scorm_package.py

Takes:
  1) NEW_RISE_FOLDER  - Dec-2025 Rise export (the broken one, with scormcontent/scormdriver)
  2) DONOR_FOLDER     - Any pre-Dec Rise xAPI export that tracks correctly (contains lib/tincan.js + lib/lms.js)
  3) OUTPUT_FOLDER    - Where to write the hybrid, fixed package

It:
  - Flattens the new Rise structure into an old-style layout (index.html at root, lib/, assets/).
  - Copies tincan.js and lms.js from the donor into lib/.
  - Patches index.html and index_lms.html to:
        * load tincan.js + lms.js
        * create window.LMSProxy = lms()
        * wire SetReachedEnd / TCAPI_SetCompleted to SetPassed if needed
        * point LMSProxySelections at window.LMSProxy instead of window.parent
  - Updates tincan.xml to launch index_lms.html at root.
"""

import os
import re
import sys
import shutil
from pathlib import Path


def log(msg):
    print(msg)


def copy_tree(src: Path, dst: Path, allow_overwrite=False):
    for root, dirs, files in os.walk(src):
        root_path = Path(root)
        rel = root_path.relative_to(src)
        out_root = dst / rel
        out_root.mkdir(parents=True, exist_ok=True)
        for f in files:
            s = root_path / f
            d = out_root / f
            if d.exists() and not allow_overwrite:
                continue
            shutil.copy2(s, d)


def find_legacy_libs(donor_root: Path):
    # look anywhere under donor_root for these
    tincans = list(donor_root.rglob("tincan.js"))
    lms_files = list(donor_root.rglob("lms.js"))

    if not tincans or not lms_files:
        raise SystemExit(
            f"ERROR: Could not find tincan.js and lms.js under {donor_root}.\n"
            f"       Make sure DONOR_FOLDER points at any pre-Dec Rise xAPI export\n"
            f"       (extracted, not zipped) that you know tracks correctly."
        )

    return tincans[0], lms_files[0]


def patch_index_html(path: Path):
    if not path.exists():
        return

    txt = path.read_text(encoding="utf-8")
    original = txt

    # 1) Fix tc-config path if present and inject tincan.js + lms.js
    if '"../tc-config.js"' in txt:
        txt = txt.replace('"../tc-config.js"', '"tc-config.js"')

    if "lib/tincan.js" not in txt and "lib/lms.js" not in txt:
        if "tc-config.js" in txt:
            txt = txt.replace(
                'tc-config.js"></script>',
                'tc-config.js"></script>\n'
                '    <script type="text/javascript" src="lib/tincan.js"></script>\n'
                '    <script type="text/javascript" src="lib/lms.js"></script>'
            )
        else:
            # fall back to adding them at top of <head>
            txt = re.sub(
                r"<head([^>]*)>",
                r'<head\1>\n    <script type="text/javascript" src="lib/tincan.js"></script>\n'
                r'    <script type="text/javascript" src="lib/lms.js"></script>',
                txt,
                count=1,
                flags=re.IGNORECASE,
            )

    # 2) Initialise LMSProxy and completion wrappers
    if "window.LMSProxy = lms();" not in txt:
        shim = """<script>
window.LMSProxy = lms();
if (window.LMSProxy) {
  if (!window.LMSProxy.SetReachedEnd && window.LMSProxy.SetPassed) {
    window.LMSProxy.SetReachedEnd = function () { window.LMSProxy.SetPassed(); };
  }
  if (!window.LMSProxy.TCAPI_SetCompleted && window.LMSProxy.SetPassed) {
    window.LMSProxy.TCAPI_SetCompleted = function () { window.LMSProxy.SetPassed(); };
  }
}
</script>
"""
        if "</head>" in txt:
            txt = txt.replace("</head>", shim + "</head>", 1)
        else:
            txt = shim + txt

    # 3) Redirect LMSProxySelections to window.LMSProxy instead of window.parent
    txt, n = re.subn(
        r"pick\(LMSProxySelections,\s*window\.parent",
        "pick(LMSProxySelections, window.LMSProxy",
        txt,
    )
    if n:
        log(f"   • Patched LMSProxySelections pick() in {path.name}")

    if txt != original:
        path.write_text(txt, encoding="utf-8")


def update_tincan_launch(tincan_path: Path):
    if not tincan_path.exists():
        return

    txt = tincan_path.read_text(encoding="utf-8")

    def repl(m):
        attrs = m.group(1)
        return f"<launch{attrs}>index_lms.html</launch>"

    new_txt, count = re.subn(
        r"<launch([^>]*)>.*?</launch>",
        repl,
        txt,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if count:
        tincan_path.write_text(new_txt, encoding="utf-8")
        log("   • Updated tincan.xml <launch> → index_lms.html")


def main(new_rise_folder, donor_folder, output_folder):
    new_rise = Path(new_rise_folder)
    donor = Path(donor_folder)
    outdir = Path(output_folder)

    if not new_rise.is_dir():
        raise SystemExit(f"NEW_RISE_FOLDER is not a directory: {new_rise}")
    if not donor.is_dir():
        raise SystemExit(f"DONOR_FOLDER is not a directory: {donor}")

    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    log("=== STEP 1: Flatten NEW Rise structure to old-style layout ===")

    scormcontent = new_rise / "scormcontent"
    scormdriver = new_rise / "scormdriver"

    if scormcontent.exists():
        log("   • Copying scormcontent/ → root")
        copy_tree(scormcontent, outdir, allow_overwrite=True)
    else:
        log("   • WARNING: scormcontent/ not found in NEW_RISE_FOLDER")

    if scormdriver.exists():
        log("   • Copying scormdriver/ → root (no overwrite)")
        copy_tree(scormdriver, outdir, allow_overwrite=False)

    for item in new_rise.iterdir():
        if item.name in ("scormcontent", "scormdriver"):
            continue
        if item.is_file():
            shutil.copy2(item, outdir / item.name)

    root_index = outdir / "index.html"
    if not root_index.exists() and (scormcontent / "index.html").exists():
        shutil.copy2(scormcontent / "index.html", root_index)
        log("   • Created root index.html from scormcontent/index.html")

    log("\n=== STEP 2: Import legacy tincan.js + lms.js from DONOR package ===")
    tincan_js, lms_js = find_legacy_libs(donor)
    log(f"   • Using tincan.js from: {tincan_js}")
    log(f"   • Using lms.js from:   {lms_js}")

    lib_dir = outdir / "lib"
    lib_dir.mkdir(exist_ok=True)
    shutil.copy2(tincan_js, lib_dir / "tincan.js")
    shutil.copy2(lms_js, lib_dir / "lms.js")
    log("   • Copied legacy libs into lib/")

    log("\n=== STEP 3: Patch index.html / index_lms.html to use LMSProxy ===")

    patch_index_html(root_index)

    root_index_lms = outdir / "index_lms.html"
    if not root_index_lms.exists() and root_index.exists():
        shutil.copy2(root_index, root_index_lms)
        log("   • Created index_lms.html from index.html")
    patch_index_html(root_index_lms)

    log("\n=== STEP 4: Update tincan.xml launch target ===")
    update_tincan_launch(outdir / "tincan.xml")

    log("\nDone. Zip the *contents* of this folder and upload as the course:")
    log(f"   {outdir}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python fix_scorm_package.py NEW_RISE_FOLDER DONOR_PACKAGE_FOLDER OUTPUT_FOLDER")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
