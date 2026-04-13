# iter_001 design summary

## Latin hypercube

- **94** LHS points in **5** dimensions (one per free well).
- **2** fixed controls: media-only blank and base-only control.
- RNG seed: **42**.
- Optional **LHS figures** (PNG): run `scripts/generate_reagent_design.py` with `--plots` to write `*_lhs_marginals.png` (1 row x 5 histograms) and `*_lhs_pairwise.png` (5x5 matrix) alongside this file.

### What is a Latin hypercube (LHS)?

A **Latin hypercube** is a recipe for choosing **N** combinations of **D** numeric factors inside fixed min/max bounds. If you project those N points onto any **one** factor, the values are **spread out in strata** along that axis (more even coverage than drawing N fully random points, which can clump). It is **not** a full factorial (which would need every combo of levels and explodes in well count). Here, **D = 5** medium parameters and **N = 94** wells, so the first workcell pass samples the search box efficiently before Bayesian optimization narrows in.

## Parameter bounds (final medium)

| Parameter | Low | High | Unit |
| --- | --- | --- | --- |
| `nacl_g_per_L` | 5.0 | 15.0 | g/L |
| `mops_mM` | 100.0 | 400.0 | mM |
| `glucose_g_per_L` | 5.0 | 20.0 | g/L |
| `mgso4_mM` | 1.0 | 25.0 | mM |
| `casamino_g_per_L` | 0.0 | 5.0 | g/L |

## Control wells

- **Media blank** (`design_type=1`): `H11` - base fill only, **no** inoculum transfer.
- **Base control** (`design_type=2`): `H12` - **no** transfers from the five variable stock wells; base + inoculum only.

## Workcell setup

### Source plate (24-well, one per run)

Plate id in transfer array: `source_24w`. Max fill per well: 8.5 mL.

Prepare the 24-well plate with the following wells before starting the run. Volumes below are the total the robot will aspirate; prepare at least this much plus dead volume for your labware (typically 0.5-1 mL extra per well).

| Well | Contents | Stock conc. | Total aspirated |
| --- | --- | --- | --- |
| A1 | NaCl stock | 150.0 g/L | 1292 µL (1.29 mL) |
| A2 | MOPS pH 8 stock | 1000.0 mM | 4699 µL (4.70 mL) |
| A3 | Glucose stock | 200.0 g/L | 1254 µL (1.25 mL) |
| A4 | MgSO4 stock | 1000.0 mM | 940 µL (0.94 mL) |
| A5 | Casamino acids stock | 50.0 g/L | 1175 µL (1.17 mL) |
| A6 | Base medium (diluent / salts / trace) | n/a | 7940 µL (7.94 mL) |
| B1 | Bacterial inoculum (preculture) | n/a | 1900 µL (1.90 mL) |

**Bacterial inoculum prep (well `B1`):** grow an exponential-phase preculture (OD600 ~1.5) in BHI+v2 or LBv2 at 37 C / 350 rpm for 3-4 h. Place in the 24-well source plate immediately before starting the run. See `src/literature/vnatriegens_operational_parameters.md` for detail.

**Seed feasibility note:** not every `--seed` value produces a transfer array that fits within the 8.5 mL source well cap. If generation fails with a volume cap error, rerun `scripts/generate_reagent_design.py` with a different `--seed` or increase stock concentrations in `StockConfig`.

### Experiment plate (96-well, starts empty)

- **Starts empty**; all liquid arrives via `transfer_array.json`.
- **Max total volume per well:** 200 µL. Base top-up uses a floored remainder so rounded stock aliquots cannot push the sum over this cap.
- **Minimum transfer volume:** 10 µL per non-zero dispense (reagent, base, or inoculum).
