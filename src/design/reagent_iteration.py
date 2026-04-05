"""Generate iter_001 reagent exploration: LHS designs, mapping JSON, transfer_array, summary.

Design rules (from project plan):
- 94 Latin Hypercube samples in 5D (media knobs).
- 1 media-only blank (base fill, no inoculum transfer).
- 1 base-only control (no transfers from the five variable stocks; inoculum like LHS).
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import qmc

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
    final_vol = 200.0
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


def build_transfer_array(
    well_params: dict[str, dict[str, float]],
    stocks: StockConfig | None = None,
    *,
    post_mix_volume: float = 40.0,
    post_mix_reps: int = 5,
    volume_round_decimals: int = 2,
) -> list[dict[str, Any]]:
    """Build Monomer-style transfer_array for all wells."""
    stocks = stocks or StockConfig()
    transfers: list[dict[str, Any]] = []

    well_to_stock_well = {
        "nacl": stocks.well_nacl,
        "mops": stocks.well_mops,
        "glucose": stocks.well_glucose,
        "mgso4": stocks.well_mgso4,
        "casamino": stocks.well_casamino,
    }

    for dst_well in sorted(well_params.keys(), key=_well_sort_key):
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
        stocks_sum = sum(rounded_stock.values())
        base_r = round(final_ul - stocks_sum - inoc_r, volume_round_decimals)
        if base_r < 0:
            raise ValueError(
                f"{dst_well}: negative base after rounding "
                f"(final={final_ul} stocks={stocks_sum} inoc={inoc_r})"
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
                    "new_tip": "always",
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
    reserved_media_blank: str,
    reserved_base_control: str,
    seed: int,
) -> str:
    lines = [
        "# iter_001 design summary",
        "",
        "## Latin hypercube",
        "",
        "- **94** LHS points in **5** dimensions (one per free well).",
        "- **2** fixed controls: media-only blank and base-only control.",
        f"- RNG seed: **{seed}**.",
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
                f"`{reserved_media_blank}` — base fill only, **no** inoculum transfer."
            ),
            (
                f"- **Base control** (`design_type={int(DESIGN_TYPE_BASE_CONTROL)}`): "
                f"`{reserved_base_control}` — **no** transfers from the five variable "
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
            "",
        ]
    )
    return "\n".join(lines)


def generate_iter_001_bundle(
    *,
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
        reserved_media_blank=reserved_media_blank,
        reserved_base_control=reserved_base_control,
        seed=seed,
    )
    return mapping, xfer, summary


def write_iter_001_outputs(
    iteration_dir: Path,
    *,
    seed: int = 42,
    reserved_media_blank: str = "H11",
    reserved_base_control: str = "H12",
    stocks: StockConfig | None = None,
) -> None:
    """Write input files under iteration_dir/input/."""
    mapping, xfer, summary = generate_iter_001_bundle(
        seed=seed,
        reserved_media_blank=reserved_media_blank,
        reserved_base_control=reserved_base_control,
        stocks=stocks,
    )
    input_dir = iteration_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "well_to_design_mapping.json").write_text(json.dumps(mapping, indent=2))
    (input_dir / "transfer_array.json").write_text(json.dumps(xfer, indent=2))
    summary_name = f"{iteration_dir.name}_design_summary.md"
    (input_dir / summary_name).write_text(summary, newline="\n")
