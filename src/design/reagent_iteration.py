"""Reagent-plate LHS exploration: designs, well mapping JSON, Monomer transfer_array, summary.

Design rules (from project plan):
- 94 Latin Hypercube samples in 5D (five medium parameters).
- 1 media-only blank (base fill, no inoculum transfer).
- 1 base-only control (no transfers from the five variable stocks; inoculum like LHS).

Public entry points for any ``iter_NNN`` folder: :func:`generate_reagent_lhs_bundle`,
:func:`write_reagent_design_outputs`. Legacy names ``generate_iter_001_bundle`` /
``write_iter_001_outputs`` remain as aliases.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import qmc

from src.design.constants import MAX_WELL_VOLUME_UL, MIN_TRANSFER_VOLUME_UL
from src.design.transfer_validation import validate_transfer_array

# Literature bounds: src/literature/vnatriegens_parameter_research.md
BOUNDS: dict[str, tuple[float, float]] = {
    "nacl_g_per_L": (5.0, 15.0),
    "mops_mM": (100.0, 400.0),
    "glucose_g_per_L": (5.0, 20.0),
    "mgso4_mM": (1.0, 25.0),
    "casamino_g_per_L": (0.0, 5.0),
}

PARAM_ORDER = (
    "nacl_g_per_L",
    "mops_mM",
    "glucose_g_per_L",
    "mgso4_mM",
    "casamino_g_per_L",
)

# Parser uses dict[str, float] for params (models.WellDesign).
DESIGN_TYPE_LHS = 0.0
DESIGN_TYPE_MEDIA_BLANK = 1.0
DESIGN_TYPE_BASE_CONTROL = 2.0


def _base_top_up_ul(stocks_sum: float, inoc_r: float, cap_ul: float) -> float:
    """µL of base so stocks + base + inoculum never exceeds cap_ul (2 decimal µL steps).

    Uses floor on the remainder so independent rounding of stock aliquots cannot push
    the sum over ``cap_ul``.
    """
    remainder = cap_ul - stocks_sum - inoc_r
    if remainder <= 0:
        return 0.0
    return math.floor(remainder * 100 + 1e-9) / 100


def _apply_min_transfer_volumes_for_well(
    rounded_stock: dict[str, float],
    inoc_r: float,
    cap_ul: float,
    *,
    min_transfer_ul: float,
    volume_round_decimals: int,
    well_label: str,
) -> tuple[dict[str, float], float, float]:
    """Enforce min µL per non-zero transfer; keep total dispensed at or below cap_ul.

    Stock and inoculum steps use at least ``min_transfer_ul`` when non-zero.
    Base top-up uses :func:`_base_top_up_ul`; if it would be in (0, min), it is
    raised to ``min_transfer_ul`` and stock volumes are trimmed (largest first,
    never below ``min_transfer_ul`` for a well that still receives that stock).
    """
    rd = volume_round_decimals
    rs = {k: (round(v, rd) if v > 0 else 0.0) for k, v in rounded_stock.items()}
    for k in rs:
        if rs[k] > 0:
            rs[k] = max(rs[k], min_transfer_ul)

    inoc_out = round(inoc_r, rd)
    if inoc_out > 0:
        inoc_out = max(inoc_out, min_transfer_ul)

    for _ in range(80):
        stocks_sum = sum(rs.values())
        if stocks_sum + inoc_out > cap_ul + 1e-9:
            raise ValueError(
                f"{well_label}: stocks+inoc exceed cap after min transfer enforce: "
                f"stocks_sum={stocks_sum} inoc={inoc_out} cap={cap_ul}"
            )
        base_r = _base_top_up_ul(stocks_sum, inoc_out, cap_ul)
        if base_r < 1e-9:
            return rs, inoc_out, 0.0
        if base_r + 1e-9 >= min_transfer_ul:
            return rs, inoc_out, base_r

        shortfall = min_transfer_ul - base_r
        to_remove = shortfall
        for k in sorted(rs, key=lambda x: rs[x], reverse=True):
            if to_remove <= 1e-9:
                break
            if rs[k] <= 0:
                continue
            can_remove = rs[k] - min_transfer_ul
            if can_remove <= 1e-9:
                continue
            take = min(to_remove, can_remove)
            rs[k] = round(rs[k] - take, rd)
            to_remove -= take

        if to_remove > 1e-9:
            raise ValueError(
                f"{well_label}: cannot satisfy {min_transfer_ul} µL minimum transfer "
                f"and {cap_ul} µL cap (still {to_remove:.2f} µL over budget after trimming)"
            )

    raise ValueError(f"{well_label}: min-transfer reconcile did not converge")


@dataclass(frozen=True)
class StockConfig:
    """Reagent stock plate layout and concentrations for volume math."""

    # Source wells on logical plate "reagent"
    well_nacl: str = "A1"
    well_mops: str = "A2"
    well_glucose: str = "A3"
    well_mgso4: str = "A4"
    well_casamino: str = "A5"
    well_base: str = "A6"
    # Cell culture source
    cell_stock_well: str = "A1"
    # Stock concentrations (match literature prep hints; tune for real stocks)
    nacl_stock_g_per_l: float = 150.0
    mops_stock_mm: float = 1000.0
    glucose_stock_g_per_l: float = 200.0
    mgso4_stock_mm: float = 1000.0
    casamino_stock_g_per_l: float = 50.0


def _all_well_names() -> list[str]:
    rows = "ABCDEFGH"
    return [f"{r}{c}" for r in rows for c in range(1, 13)]


def latin_hypercube_scaled(n: int, *, seed: int) -> np.ndarray:
    """Return shape (n, 5) with columns in PARAM_ORDER ranges."""
    engine = qmc.LatinHypercube(d=len(PARAM_ORDER), seed=seed)
    unit = engine.random(n=n)
    lo = np.array([BOUNDS[k][0] for k in PARAM_ORDER], dtype=np.float64)
    hi = np.array([BOUNDS[k][1] for k in PARAM_ORDER], dtype=np.float64)
    scaled: np.ndarray = lo + unit * (hi - lo)
    return scaled


def assign_designs_to_wells(
    lhs: np.ndarray,
    *,
    reserved_media_blank: str,
    reserved_base_control: str,
    seed: int,
) -> dict[str, dict[str, float]]:
    """Map well IDs to params (94 LHS + 2 controls)."""
    all_wells = _all_well_names()
    reserved = {reserved_media_blank, reserved_base_control}
    free = [w for w in all_wells if w not in reserved]
    if len(free) != lhs.shape[0]:
        raise ValueError(f"Need {lhs.shape[0]} free wells, got {len(free)}")

    rng = random.Random(seed)
    rng.shuffle(free)

    out: dict[str, dict[str, float]] = {}
    final_vol = MAX_WELL_VOLUME_UL
    inoc_lhs = 20.0
    inoc_blank = 0.0

    for i, well in enumerate(free):
        row = lhs[i]
        params = {k: float(row[j]) for j, k in enumerate(PARAM_ORDER)}
        params["design_type"] = DESIGN_TYPE_LHS
        params["final_volume_uL"] = final_vol
        params["inoculum_volume_uL"] = inoc_lhs
        out[well] = params

    out[reserved_media_blank] = {
        "nacl_g_per_L": 0.0,
        "mops_mM": 0.0,
        "glucose_g_per_L": 0.0,
        "mgso4_mM": 0.0,
        "casamino_g_per_L": 0.0,
        "design_type": DESIGN_TYPE_MEDIA_BLANK,
        "final_volume_uL": final_vol,
        "inoculum_volume_uL": inoc_blank,
    }
    out[reserved_base_control] = {
        "nacl_g_per_L": 0.0,
        "mops_mM": 0.0,
        "glucose_g_per_L": 0.0,
        "mgso4_mM": 0.0,
        "casamino_g_per_L": 0.0,
        "design_type": DESIGN_TYPE_BASE_CONTROL,
        "final_volume_uL": final_vol,
        "inoculum_volume_uL": inoc_lhs,
    }
    return out


def _vol_from_g_per_l(
    c_final_g_l: float,
    c_stock_g_l: float,
    final_ul: float,
) -> float:
    """µL to transfer from g/L stock to hit c_final in final_ul total."""
    if c_final_g_l <= 0:
        return 0.0
    return (c_final_g_l * final_ul) / c_stock_g_l


def _vol_from_mm(
    c_final_mm: float,
    c_stock_mm: float,
    final_ul: float,
) -> float:
    """µL to transfer from mM stock to hit c_final_mm in final_ul."""
    if c_final_mm <= 0:
        return 0.0
    return (c_final_mm * final_ul) / c_stock_mm


def stock_volumes_ul(
    params: dict[str, float],
    final_ul: float,
    stocks: StockConfig,
) -> tuple[dict[str, float], float, float]:
    """Return per-variable-stock volumes (µL), base volume (µL), inoculum (µL)."""
    v_nacl = _vol_from_g_per_l(params["nacl_g_per_L"], stocks.nacl_stock_g_per_l, final_ul)
    v_mops = _vol_from_mm(params["mops_mM"], stocks.mops_stock_mm, final_ul)
    v_gluc = _vol_from_g_per_l(params["glucose_g_per_L"], stocks.glucose_stock_g_per_l, final_ul)
    v_mg = _vol_from_mm(params["mgso4_mM"], stocks.mgso4_stock_mm, final_ul)
    v_caa = _vol_from_g_per_l(params["casamino_g_per_L"], stocks.casamino_stock_g_per_l, final_ul)

    dtype = params["design_type"]
    inoc = float(params.get("inoculum_volume_uL", 0.0))

    if dtype == DESIGN_TYPE_MEDIA_BLANK:
        return {}, final_ul, 0.0
    if dtype == DESIGN_TYPE_BASE_CONTROL:
        v_stocks_sum = 0.0
        base = final_ul - v_stocks_sum - inoc
        return {}, base, inoc

    v_stocks = {
        "nacl": v_nacl,
        "mops": v_mops,
        "glucose": v_gluc,
        "mgso4": v_mg,
        "casamino": v_caa,
    }
    v_stocks_sum = sum(v_stocks.values())
    base = final_ul - v_stocks_sum - inoc
    if base < -1e-6:
        msg = (
            f"Infeasible volumes: final={final_ul} stocks_sum={v_stocks_sum} "
            f"inoc={inoc} base={base}"
        )
        raise ValueError(msg)
    return v_stocks, max(base, 0.0), inoc


def _transfer_well_order(well_params: dict[str, dict[str, float]]) -> list[str]:
    """Media blank first, base control second, then remaining wells in plate sort order."""
    blanks = sorted(
        (
            w
            for w, p in well_params.items()
            if float(p.get("design_type", -1.0)) == DESIGN_TYPE_MEDIA_BLANK
        ),
        key=_well_sort_key,
    )
    controls = sorted(
        (
            w
            for w, p in well_params.items()
            if float(p.get("design_type", -1.0)) == DESIGN_TYPE_BASE_CONTROL
        ),
        key=_well_sort_key,
    )
    lead = set(blanks) | set(controls)
    rest = sorted((w for w in well_params if w not in lead), key=_well_sort_key)
    return [*blanks, *controls, *rest]


def build_transfer_array(
    well_params: dict[str, dict[str, float]],
    stocks: StockConfig | None = None,
    *,
    post_mix_volume: float = 40.0,
    post_mix_reps: int = 5,
    volume_round_decimals: int = 2,
    min_transfer_volume_ul: float = MIN_TRANSFER_VOLUME_UL,
) -> list[dict[str, Any]]:
    """Build Monomer-style transfer_array for all wells.

    Wells run in order: media blank(s), base control(s), then LHS wells in plate order.
    """
    stocks = stocks or StockConfig()
    transfers: list[dict[str, Any]] = []

    well_to_stock_well = {
        "nacl": stocks.well_nacl,
        "mops": stocks.well_mops,
        "glucose": stocks.well_glucose,
        "mgso4": stocks.well_mgso4,
        "casamino": stocks.well_casamino,
    }

    for dst_well in _transfer_well_order(well_params):
        params = well_params[dst_well]
        final_ul = float(params["final_volume_uL"])
        v_stocks, _base_ul, inoc_ul = stock_volumes_ul(params, final_ul, stocks)

        rounded_stock: dict[str, float] = {}
        # Concentrated stocks first, then base, then cells (mix last).
        for key in ("nacl", "mops", "glucose", "mgso4", "casamino"):
            vol = float(v_stocks.get(key, 0.0))
            vol_r = round(vol, volume_round_decimals)
            rounded_stock[key] = vol_r if vol_r > 0 else 0.0

        inoc_r = round(inoc_ul, volume_round_decimals)
        cap_ul = min(float(final_ul), MAX_WELL_VOLUME_UL)
        rounded_stock, inoc_r, base_r = _apply_min_transfer_volumes_for_well(
            rounded_stock,
            inoc_r,
            cap_ul,
            min_transfer_ul=min_transfer_volume_ul,
            volume_round_decimals=volume_round_decimals,
            well_label=dst_well,
        )

        for key in ("nacl", "mops", "glucose", "mgso4", "casamino"):
            vol_r = rounded_stock[key]
            if vol_r <= 0:
                continue
            transfers.append(
                {
                    "src_plate": "reagent",
                    "src_well": well_to_stock_well[key],
                    "dst_plate": "experiment",
                    "dst_well": dst_well,
                    "volume": vol_r,
                    "new_tip": "once",
                    "blow_out": True,
                }
            )

        if base_r > 0:
            transfers.append(
                {
                    "src_plate": "reagent",
                    "src_well": stocks.well_base,
                    "dst_plate": "experiment",
                    "dst_well": dst_well,
                    "volume": base_r,
                    "new_tip": "once",
                    "blow_out": True,
                }
            )

        if inoc_r > 0:
            transfers.append(
                {
                    "src_plate": "cell_culture_stock",
                    "src_well": stocks.cell_stock_well,
                    "dst_plate": "experiment",
                    "dst_well": dst_well,
                    "volume": inoc_r,
                    "post_mix_volume": post_mix_volume,
                    "post_mix_reps": post_mix_reps,
                    "new_tip": "once",
                    "blow_out": False,
                }
            )

    return transfers


def _well_sort_key(w: str) -> tuple[int, str]:
    return (int(w[1:]), w[0])


def render_summary_markdown(
    well_params: dict[str, dict[str, float]],
    stocks: StockConfig,
    *,
    iteration_id: str,
    reserved_media_blank: str,
    reserved_base_control: str,
    seed: int,
) -> str:
    lines = [
        f"# {iteration_id} design summary",
        "",
        "## Latin hypercube",
        "",
        "- **94** LHS points in **5** dimensions (one per free well).",
        "- **2** fixed controls: media-only blank and base-only control.",
        f"- RNG seed: **{seed}**.",
        (
            "- Optional **LHS figures** (PNG): run `scripts/generate_reagent_design.py` "
            "with `--plots` to write `*_lhs_marginals.png` (1 row x 5 histograms) and "
            "`*_lhs_pairwise.png` (5x5 matrix) alongside this file."
        ),
        "",
        "### What is a Latin hypercube (LHS)?",
        "",
        (
            "A **Latin hypercube** is a recipe for choosing **N** combinations of **D** numeric "
            "factors inside fixed min/max bounds. If you project those N points onto any **one** "
            "factor, the values are **spread out in strata** along that axis (more even coverage "
            "than drawing N fully random points, which can clump). It is **not** a full factorial "
            "(which would need every combo of levels and explodes in well count). Here, **D = 5** "
            "medium parameters and **N = 94** wells, so the first workcell pass samples the "
            "search box efficiently before Bayesian optimization narrows in."
        ),
        "",
        "## Parameter bounds (final medium)",
        "",
        "| Parameter | Low | High | Unit |",
        "| --- | --- | --- | --- |",
    ]
    for k in PARAM_ORDER:
        lo, hi = BOUNDS[k]
        unit = "g/L" if "g_per_L" in k else "mM"
        lines.append(f"| `{k}` | {lo} | {hi} | {unit} |")
    lines.extend(
        [
            "",
            "## Control wells",
            "",
            (
                f"- **Media blank** (`design_type={int(DESIGN_TYPE_MEDIA_BLANK)}`): "
                f"`{reserved_media_blank}` - base fill only, **no** inoculum transfer."
            ),
            (
                f"- **Base control** (`design_type={int(DESIGN_TYPE_BASE_CONTROL)}`): "
                f"`{reserved_base_control}` - **no** transfers from the five variable "
                "stock wells; base + inoculum only."
            ),
            "",
            "## Reagent stock plate (logical `reagent`)",
            "",
            "| Well | Contents | Concentration (for volume math) |",
            "| --- | --- | --- |",
            f"| {stocks.well_nacl} | NaCl stock | {stocks.nacl_stock_g_per_l} g/L |",
            f"| {stocks.well_mops} | MOPS (pH 8) stock | {stocks.mops_stock_mm} mM |",
            f"| {stocks.well_glucose} | Glucose stock | {stocks.glucose_stock_g_per_l} g/L |",
            f"| {stocks.well_mgso4} | MgSO₄ stock | {stocks.mgso4_stock_mm} mM |",
            (
                f"| {stocks.well_casamino} | Casamino acids stock | "
                f"{stocks.casamino_stock_g_per_l} g/L |"
            ),
            f"| {stocks.well_base} | Base medium (diluent / salts / trace as prepared) | n/a |",
            "",
            "## Cell culture stock plate (logical `cell_culture_stock`)",
            "",
            f"- Source well for inoculum: **`{stocks.cell_stock_well}`** (preculture per lab SOP).",
            "",
            "## Experiment plate",
            "",
            "- **Starts empty**; all liquid arrives via `transfer_array`.",
            (
                f"- **Max total volume per well:** {MAX_WELL_VOLUME_UL:.0f} µL. "
                "Base top-up uses a floored remainder so rounded stock aliquots "
                "cannot push the sum over this cap."
            ),
            (
                f"- **Minimum transfer volume:** {MIN_TRANSFER_VOLUME_UL:.0f} µL per "
                "non-zero dispense (reagent, base, or inoculum)."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def generate_reagent_lhs_bundle(
    *,
    iteration_id: str = "iter_001",
    seed: int = 42,
    reserved_media_blank: str = "H11",
    reserved_base_control: str = "H12",
    stocks: StockConfig | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Return (well_to_design_mapping dict, transfer_array, summary markdown)."""
    stocks = stocks or StockConfig()
    lhs = latin_hypercube_scaled(94, seed=seed)
    well_params = assign_designs_to_wells(
        lhs,
        reserved_media_blank=reserved_media_blank,
        reserved_base_control=reserved_base_control,
        seed=seed + 11,
    )
    sorted_items = sorted(well_params.items(), key=lambda x: _well_sort_key(x[0]))
    mapping = {"designs": [{"well": w, "params": p} for w, p in sorted_items]}
    xfer = build_transfer_array(well_params, stocks)
    summary = render_summary_markdown(
        well_params,
        stocks,
        iteration_id=iteration_id,
        reserved_media_blank=reserved_media_blank,
        reserved_base_control=reserved_base_control,
        seed=seed,
    )
    return mapping, xfer, summary


def write_reagent_design_outputs(
    iteration_dir: Path,
    *,
    seed: int = 42,
    reserved_media_blank: str = "H11",
    reserved_base_control: str = "H12",
    stocks: StockConfig | None = None,
    write_plots: bool = False,
) -> None:
    """Write input files under iteration_dir/input/."""
    mapping, xfer, summary = generate_reagent_lhs_bundle(
        iteration_id=iteration_dir.name,
        seed=seed,
        reserved_media_blank=reserved_media_blank,
        reserved_base_control=reserved_base_control,
        stocks=stocks,
    )
    input_dir = iteration_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "well_to_design_mapping.json").write_text(json.dumps(mapping, indent=2))
    xfer_validated = validate_transfer_array(xfer)
    xfer_out = [row.model_dump(mode="json") for row in xfer_validated]
    (input_dir / "transfer_array.json").write_text(json.dumps(xfer_out, indent=2))
    summary_name = f"{iteration_dir.name}_design_summary.md"
    (input_dir / summary_name).write_text(summary, newline="\n")
    if write_plots:
        from src.design.lhs_plots import write_lhs_visualization_files

        write_lhs_visualization_files(mapping, input_dir, iteration_dir.name)


# Backward-compatible names (prefer generate_reagent_lhs_bundle / write_reagent_design_outputs).
generate_iter_001_bundle = generate_reagent_lhs_bundle
write_iter_001_outputs = write_reagent_design_outputs
