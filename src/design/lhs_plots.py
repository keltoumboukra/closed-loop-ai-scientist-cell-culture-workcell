"""LHS design visualization (marginal histograms and pairwise scatter matrix)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from src.design.reagent_iteration import BOUNDS, DESIGN_TYPE_LHS, PARAM_ORDER

# Short axis labels for figures
PARAM_LABELS: tuple[str, ...] = (
    "NaCl (g/L)",
    "MOPS (mM)",
    "Glucose (g/L)",
    "MgSO4 (mM)",
    "Casamino (g/L)",
)

# On-figure captions (keep short so PNG export does not clip)
MARGINALS_FOOTNOTE = (
    "Histograms: 94 LHS wells per parameter (no controls). Bars = well counts. "
    "Axis limits match the search box."
)

PAIRWISE_FOOTNOTE = (
    "Diagonal: one parameter per panel. Below diagonal: two parameters; each dot = one well. "
    "Upper triangle empty on purpose."
)


def lhs_sample_matrix_from_mapping(mapping: dict[str, Any]) -> np.ndarray:
    """Extract shape (n_lhs, 5) array of LHS wells only from well_to_design_mapping JSON."""
    rows: list[list[float]] = []
    for entry in mapping["designs"]:
        p = entry["params"]
        if float(p.get("design_type", -1.0)) != DESIGN_TYPE_LHS:
            continue
        rows.append([float(p[k]) for k in PARAM_ORDER])
    if not rows:
        raise ValueError("No LHS designs found in mapping (design_type == 0)")
    return np.array(rows, dtype=np.float64)


def write_lhs_visualization_files(
    mapping: dict[str, Any],
    input_dir: Path,
    iteration_name: str,
    *,
    dpi: int = 120,
) -> list[Path]:
    """Write PNGs under input_dir: marginals and pairwise scatter matrix.

    Uses non-interactive Agg backend suitable for CI and headless runs.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x = lhs_sample_matrix_from_mapping(mapping)
    n = x.shape[0]
    d = len(PARAM_ORDER)
    written: list[Path] = []

    # --- Marginal histograms (1 x d) + footnote ---
    fig1 = plt.figure(figsize=(2.5 * d + 0.5, 4.2), layout="constrained")
    gs1 = fig1.add_gridspec(2, 1, height_ratios=[1, 0.16])
    panel1 = fig1.add_subfigure(gs1[0, 0])
    axes1 = panel1.subplots(1, d, sharey=False)
    if d == 1:
        axes1 = np.array([axes1])
    for j in range(d):
        ax = axes1[j]
        key = PARAM_ORDER[j]
        lo, hi = BOUNDS[key]
        span = hi - lo
        pad = 0.02 * span if span > 0 else 1.0
        ax.hist(
            x[:, j],
            bins=min(20, max(8, n // 5)),
            color="steelblue",
            edgecolor="white",
            alpha=0.9,
            range=(lo - pad, hi + pad),
        )
        ax.set_title(PARAM_LABELS[j], fontsize=10, fontweight="medium")
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylabel("well count" if j == 0 else "")
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=8)
    panel1.suptitle(
        f"{iteration_name}: one-dimensional coverage (Latin Hypercube, n={n} wells)",
        fontsize=12,
        fontweight="bold",
        y=1.03,
    )
    fig1.text(
        0.5,
        0.08,
        MARGINALS_FOOTNOTE,
        ha="center",
        va="center",
        fontsize=8,
        linespacing=1.25,
    )
    path1 = input_dir / f"{iteration_name}_lhs_marginals.png"
    fig1.savefig(path1, dpi=dpi, bbox_inches="tight")
    plt.close(fig1)
    written.append(path1)

    # --- Pairwise matrix + footnote ---
    # Do not use sharex/sharey: diagonal hists use y=counts; scatters use y=concentration.
    # Sharing a row breaks histograms (e.g. MOPS diagonal looked empty).
    fig2 = plt.figure(figsize=(11, 11.4), layout="constrained")
    gs2 = fig2.add_gridspec(2, 1, height_ratios=[1, 0.11])
    panel2 = fig2.add_subfigure(gs2[0, 0])
    axes2 = panel2.subplots(d, d)
    for i in range(d):
        for j in range(d):
            ax = axes2[i, j]
            xi_key, xj_key = PARAM_ORDER[i], PARAM_ORDER[j]
            lo_i, hi_i = BOUNDS[xi_key]
            lo_j, hi_j = BOUNDS[xj_key]
            pad_i = 0.02 * (hi_i - lo_i) if hi_i > lo_i else 1.0
            pad_j = 0.02 * (hi_j - lo_j) if hi_j > lo_j else 1.0
            if i == j:
                ax.hist(
                    x[:, i],
                    bins=min(18, max(6, n // 6)),
                    color="cadetblue",
                    edgecolor="white",
                    alpha=0.85,
                    range=(lo_i - pad_i, hi_i + pad_i),
                )
                ax.set_xlim(lo_i - pad_i, hi_i + pad_i)
                ax.set_title(PARAM_LABELS[i], fontsize=9, fontweight="medium", pad=2)
                if i == d - 1:
                    ax.set_xlabel(PARAM_LABELS[j], fontsize=9)
                if j == 0:
                    ax.set_ylabel("wells", fontsize=9)
            elif i > j:
                ax.scatter(
                    x[:, j],
                    x[:, i],
                    s=14,
                    alpha=0.55,
                    c="darkslategray",
                    edgecolors="none",
                )
                ax.set_xlim(lo_j - pad_j, hi_j + pad_j)
                ax.set_ylim(lo_i - pad_i, hi_i + pad_i)
                if i == d - 1:
                    ax.set_xlabel(PARAM_LABELS[j], fontsize=9)
                if j == 0:
                    ax.set_ylabel(PARAM_LABELS[i], fontsize=9)
            else:
                ax.axis("off")
    panel2.suptitle(
        f"{iteration_name}: two-parameter projections (same {n} LHS wells)",
        fontsize=12,
        fontweight="bold",
        y=1.01,
    )
    fig2.text(
        0.5,
        0.035,
        PAIRWISE_FOOTNOTE,
        ha="center",
        va="bottom",
        fontsize=7.5,
        linespacing=1.2,
    )
    path2 = input_dir / f"{iteration_name}_lhs_pairwise.png"
    fig2.savefig(path2, dpi=dpi, bbox_inches="tight")
    plt.close(fig2)
    written.append(path2)

    return written
