"""Tests for src.design.reagent_iteration (iter_001 LHS + transfer_array)."""

from __future__ import annotations

import json
from pathlib import Path

from src.design.reagent_iteration import (
    BOUNDS,
    DESIGN_TYPE_BASE_CONTROL,
    DESIGN_TYPE_LHS,
    DESIGN_TYPE_MEDIA_BLANK,
    MAX_WELL_VOLUME_UL,
    PARAM_ORDER,
    StockConfig,
    assign_designs_to_wells,
    generate_iter_001_bundle,
    latin_hypercube_scaled,
    stock_volumes_ul,
    write_iter_001_outputs,
)


def test_latin_hypercube_scaled_in_bounds() -> None:
    lhs = latin_hypercube_scaled(94, seed=1)
    assert lhs.shape == (94, 5)
    for j, k in enumerate(PARAM_ORDER):
        lo, hi = BOUNDS[k]
        assert lhs[:, j].min() >= lo - 1e-9
        assert lhs[:, j].max() <= hi + 1e-9


def test_assign_designs_to_wells_counts_and_controls() -> None:
    lhs = latin_hypercube_scaled(94, seed=2)
    wp = assign_designs_to_wells(
        lhs,
        reserved_media_blank="H11",
        reserved_base_control="H12",
        seed=3,
    )
    assert len(wp) == 96
    blanks = [w for w, p in wp.items() if p["design_type"] == DESIGN_TYPE_MEDIA_BLANK]
    bases = [w for w, p in wp.items() if p["design_type"] == DESIGN_TYPE_BASE_CONTROL]
    lhs_w = [w for w, p in wp.items() if p["design_type"] == DESIGN_TYPE_LHS]
    assert blanks == ["H11"]
    assert bases == ["H12"]
    assert len(lhs_w) == 94
    assert wp["H11"]["inoculum_volume_uL"] == 0.0
    assert wp["H12"]["inoculum_volume_uL"] == 20.0


def test_transfer_volumes_sum_to_final() -> None:
    mapping, xfer, _summary = generate_iter_001_bundle(seed=4)
    assert len(mapping["designs"]) == 96
    by_well: dict[str, dict] = {d["well"]: d["params"] for d in mapping["designs"]}

    def total_in_for_well(well: str) -> float:
        t = 0.0
        for step in xfer:
            if step.get("dst_plate") == "experiment" and step.get("dst_well") == well:
                t += float(step["volume"])
        return t

    for well, params in by_well.items():
        final = float(params["final_volume_uL"])
        total_in = total_in_for_well(well)
        assert total_in <= final + 1e-6, (well, total_in, final)
        assert total_in <= MAX_WELL_VOLUME_UL + 1e-6, (well, total_in)


def test_dispensed_volume_never_exceeds_200_ul() -> None:
    _mapping, xfer, _s = generate_iter_001_bundle(seed=123)
    per_well: dict[str, float] = {}
    for step in xfer:
        if step.get("dst_plate") != "experiment":
            continue
        w = str(step["dst_well"])
        per_well[w] = per_well.get(w, 0.0) + float(step["volume"])
    assert len(per_well) == 96
    for well, total in per_well.items():
        assert total <= MAX_WELL_VOLUME_UL + 1e-9, f"{well} total {total} > {MAX_WELL_VOLUME_UL}"


def test_media_blank_no_cell_transfer() -> None:
    _mapping, xfer, _s = generate_iter_001_bundle(seed=5)
    cell_to_h11 = [
        x for x in xfer if x.get("dst_well") == "H11" and x.get("src_plate") == "cell_culture_stock"
    ]
    assert cell_to_h11 == []


def test_base_control_no_variable_stocks() -> None:
    stocks = StockConfig()
    mapping, xfer, _s = generate_iter_001_bundle(seed=6)
    by_well = {d["well"]: d["params"] for d in mapping["designs"]}
    xfer_h12 = [x for x in xfer if x.get("dst_well") == "H12"]
    for step in xfer_h12:
        if step.get("src_plate") == "reagent":
            assert step["src_well"] == stocks.well_base
    assert by_well["H12"]["design_type"] == DESIGN_TYPE_BASE_CONTROL


def test_stock_volumes_ul_base_control() -> None:
    stocks = StockConfig()
    p = {
        "nacl_g_per_L": 0.0,
        "mops_mM": 0.0,
        "glucose_g_per_L": 0.0,
        "mgso4_mM": 0.0,
        "casamino_g_per_L": 0.0,
        "design_type": DESIGN_TYPE_BASE_CONTROL,
        "final_volume_uL": 200.0,
        "inoculum_volume_uL": 20.0,
    }
    v_s, base, inoc = stock_volumes_ul(p, 200.0, stocks)
    assert v_s == {}
    assert inoc == 20.0
    assert base == 180.0


def test_write_iter_001_outputs(tmp_path: Path) -> None:
    iteration_dir = tmp_path / "iter_001"
    write_iter_001_outputs(iteration_dir, seed=7)
    mapping_path = iteration_dir / "input" / "well_to_design_mapping.json"
    assert mapping_path.is_file()
    data = json.loads(mapping_path.read_text())
    assert len(data["designs"]) == 96
    assert (iteration_dir / "input" / "transfer_array.json").is_file()
    assert (iteration_dir / "input" / "iter_001_design_summary.md").is_file()


def test_transfer_array_keys_match_monomer_shape() -> None:
    _m, xfer, _s = generate_iter_001_bundle(seed=8)
    assert len(xfer) > 0
    for step in xfer[:3]:
        assert "src_plate" in step
        assert "src_well" in step
        assert step["dst_plate"] == "experiment"
        assert "dst_well" in step
        assert "volume" in step
        assert "new_tip" in step
        assert "blow_out" in step
    cell_steps = [x for x in xfer if x["src_plate"] == "cell_culture_stock"]
    assert cell_steps
    assert "post_mix_volume" in cell_steps[0]
    assert "post_mix_reps" in cell_steps[0]
