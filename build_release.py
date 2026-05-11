#!/usr/bin/env python3
"""Build a release ZIP of the Poliscope QGIS plugin.

Creates ``../poliscope_qgis_plugin/`` (a clean copy of this repo with dev-only
files removed) and packages it as ``../poliscope_qgis_plugin.zip``, ready for
upload to plugins.qgis.org.

Usage:
    python build_release.py

"""

import shutil
import sys
import zipfile
from pathlib import Path

PLUGIN_NAME = "poliscope_qgis_plugin"

EXCLUDE_PATTERNS = (
    ".git",
    ".claude",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    ".gitignore",
    "CLAUDE.md",
    "HANDOVER.md",
    "build_release.py",
    "*.pyc",
)


def main() -> int:
    repo = Path(__file__).resolve().parent
    parent = repo.parent
    staging = parent / PLUGIN_NAME
    zip_path = parent / f"{PLUGIN_NAME}.zip"

    if staging.resolve() == repo:
        sys.stderr.write(
            "Refusing to overwrite the repo itself. Rename the repo folder "
            f"so it is not '{PLUGIN_NAME}'.\n"
        )
        return 1

    if staging.exists():
        print(f"Removing stale staging dir: {staging}")
        shutil.rmtree(staging)
    if zip_path.exists():
        print(f"Removing stale ZIP: {zip_path}")
        zip_path.unlink()

    print(f"Copying repo -> {staging}")
    shutil.copytree(
        repo,
        staging,
        ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS),
    )

    print(f"Zipping -> {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(parent))

    file_count = sum(1 for _ in zip_path.parent.glob(f"{PLUGIN_NAME}.zip"))
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"\nDone: {zip_path} ({size_mb:.2f} MB)")
    print(f"Staging dir kept at: {staging}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
