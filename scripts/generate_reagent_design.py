"""CLI: write reagent LHS design files under data/iterations/<iter_NNN>/input/.

Usage (from repo root, after ``uv sync``):

    uv run python scripts/generate_reagent_design.py
    uv run python scripts/generate_reagent_design.py iter_002 --seed 99
    uv run python scripts/generate_reagent_design.py --plots
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _ensure_repo_root_on_path() -> None:
    """Allow ``uv run python scripts/...`` to import ``src.*`` (repo root not on PYTHONPATH)."""
    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)


def _resolve_iteration_dir(arg: str | None) -> Path:
    if arg is None:
        return Path("data/iterations/iter_001")
    p = Path(arg)
    if len(p.parts) == 1 and re.match(r"^iter_\d+$", p.name):
        return Path("data/iterations") / p.name
    return p


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate reagent LHS design: mapping, transfer_array, summary (any iter_NNN).",
    )
    parser.add_argument(
        "iteration",
        nargs="?",
        default="iter_001",
        help="Iteration folder name or path (default: iter_001)",
    )
    parser.add_argument("--seed", type=int, default=42, help="LHS and well-shuffle seed")
    parser.add_argument(
        "--media-blank-well",
        default="H11",
        help="Well reserved for media-only blank",
    )
    parser.add_argument(
        "--base-control-well",
        default="H12",
        help="Well reserved for base-only control",
    )
    parser.add_argument(
        "--plots",
        action="store_true",
        help="Write LHS marginal and pairwise PNGs under input/ (requires matplotlib)",
    )
    args = parser.parse_args()

    _ensure_repo_root_on_path()

    iteration_dir = _resolve_iteration_dir(args.iteration)
    if not re.match(r"^iter_\d+$", iteration_dir.name):
        print(
            f"Error: iteration folder should be named iter_NNN, got {iteration_dir.name}",
            file=sys.stderr,
        )
        sys.exit(1)

    from src.design.reagent_iteration import write_reagent_design_outputs

    write_reagent_design_outputs(
        iteration_dir,
        seed=args.seed,
        reserved_media_blank=args.media_blank_well,
        reserved_base_control=args.base_control_well,
        write_plots=args.plots,
    )
    inp = iteration_dir / "input"
    print(f"Wrote {inp / 'well_to_design_mapping.json'}")
    print(f"Wrote {inp / 'transfer_array.json'}")
    summary_name = f"{iteration_dir.name}_design_summary.md"
    print(f"Wrote {inp / summary_name}")
    if args.plots:
        stem = iteration_dir.name
        print(f"Wrote {inp / f'{stem}_lhs_marginals.png'}")
        print(f"Wrote {inp / f'{stem}_lhs_pairwise.png'}")


if __name__ == "__main__":
    main()
