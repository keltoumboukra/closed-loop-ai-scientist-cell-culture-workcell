#!/usr/bin/env python3
"""
Rename legacy screenshot exports (if present) and copy manual Loopy PNGs into the webapp.

Also updates GitHub template assets and favicons.

Source of truth: assets/mascot/manual_exports/loopy-*.png
Run from repo root: uv run python scripts/sync_mascot_manual_exports.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
MANUAL = REPO_ROOT / "assets" / "mascot" / "manual_exports"
PUBLIC_MASCOT = REPO_ROOT / "frontend" / "public" / "mascot"
PUBLIC_EXPORTS = PUBLIC_MASCOT / "exports"
GITHUB_ASSETS = REPO_ROOT / ".github" / "assets"

# macOS screenshots use a narrow no-break space (U+202F) before "PM".
_RE = "\u202f"

# Ordered rename: (old_name, canonical loopy-*.png name)
LEGACY_RENAMES: list[tuple[str, str]] = [
    (f"Screenshot 2026-04-05 at 1.13.28{_RE}PM.png", "loopy-neutral.png"),
    (f"Screenshot 2026-04-05 at 1.13.33{_RE}PM.png", "loopy-pipette.png"),
    (f"Screenshot 2026-04-05 at 1.13.39{_RE}PM.png", "loopy-microscope.png"),
    (f"Screenshot 2026-04-05 at 1.13.45{_RE}PM.png", "loopy-petri-dish.png"),
    (f"Screenshot 2026-04-05 at 1.13.50{_RE}PM.png", "loopy-question-chart.png"),
    (f"Screenshot 2026-04-05 at 1.14.05{_RE}PM.png", "loopy-dashboard.png"),
    (f"Screenshot 2026-04-05 at 1.14.11{_RE}PM.png", "loopy-closed-loop.png"),
    (f"Screenshot 2026-04-05 at 1.14.16{_RE}PM.png", "loopy-success-metrics.png"),
    (f"Screenshot 2026-04-05 at 1.14.22{_RE}PM.png", "loopy-error.png"),
    (f"Screenshot 2026-04-05 at 1.14.29{_RE}PM.png", "loopy-hourglass.png"),
    (f"Screenshot 2026-04-05 at 1.14.33{_RE}PM.png", "loopy-collaboration.png"),
    (f"Screenshot 2026-04-05 at 1.14.39{_RE}PM.png", "loopy-head.png"),
    (f"Screenshot 2026-04-05 at 1.14.55{_RE}PM.png", "loopy-human-in-the-loop.png"),
]

# Friendly names for web routes and existing paths (copy from manual canonical file)
SEMANTIC_COPIES: dict[str, str] = {
    "dashboard.png": "loopy-dashboard.png",
    "iteration.png": "loopy-microscope.png",
    "history.png": "loopy-hourglass.png",
    "compare.png": "loopy-question-chart.png",
    "error.png": "loopy-error.png",
    "empty.png": "loopy-neutral.png",
    "collaboration.png": "loopy-collaboration.png",
}


def main() -> None:
    if not MANUAL.is_dir():
        raise SystemExit(f"Missing directory: {MANUAL}")

    for old, new in LEGACY_RENAMES:
        src = MANUAL / old
        dst = MANUAL / new
        if src.is_file():
            if dst.is_file() and dst != src:
                dst.unlink()
            src.rename(dst)
            print(f"Renamed {old!r} -> {new}")

    expected = [n for _, n in LEGACY_RENAMES]
    missing = [n for n in expected if not (MANUAL / n).is_file()]
    if missing:
        raise SystemExit(f"Missing canonical files in {MANUAL}: {missing}")

    head = MANUAL / "loopy-head.png"
    img = Image.open(head).convert("RGBA")
    img.resize((32, 32), Image.Resampling.LANCZOS).save(
        REPO_ROOT / "frontend" / "public" / "favicon.png", "PNG"
    )
    img.resize((180, 180), Image.Resampling.LANCZOS).save(
        REPO_ROOT / "frontend" / "public" / "apple-touch-icon.png", "PNG"
    )

    PUBLIC_EXPORTS.mkdir(parents=True, exist_ok=True)
    GITHUB_ASSETS.mkdir(parents=True, exist_ok=True)

    for name in sorted(expected):
        shutil.copy2(MANUAL / name, PUBLIC_EXPORTS / name)

    readme_manual = MANUAL / "README.txt"
    if readme_manual.is_file():
        shutil.copy2(readme_manual, PUBLIC_EXPORTS / "README.txt")

    for dest, src_name in SEMANTIC_COPIES.items():
        shutil.copy2(MANUAL / src_name, PUBLIC_MASCOT / dest)

    shutil.copy2(MANUAL / "loopy-error.png", GITHUB_ASSETS / "loopy-bug.png")
    shutil.copy2(MANUAL / "loopy-collaboration.png", GITHUB_ASSETS / "loopy-pr-collaborative.png")
    readme_dst = REPO_ROOT / "assets" / "mascot" / "readme-loopy.png"
    shutil.copy2(MANUAL / "loopy-dashboard.png", readme_dst)

    print(f"Synced {len(expected)} files to {PUBLIC_EXPORTS}")
    print(f"Semantic copies under {PUBLIC_MASCOT}")
    print("GitHub assets and readme-loopy.png updated")


if __name__ == "__main__":
    main()
