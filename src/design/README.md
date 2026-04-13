# Experiment design (`src/design`)

Code that builds **reagent Latin hypercube** layouts for the Monomer workcell: per-well medium parameters, `well_to_design_mapping.json`, `transfer_array.json`, and `*_design_summary.md`.

| Module | Role |
|--------|------|
| [`constants.py`](constants.py) | `MAX_WELL_VOLUME_UL`, `MIN_TRANSFER_VOLUME_UL`, `SOURCE_PLATE_ID`, `MAX_SOURCE_WELL_VOLUME_UL` (shared with transfer validation). |
| [`reagent_iteration.py`](reagent_iteration.py) | LHS sampling, well assignment, volume math, `build_transfer_array`, summary markdown (includes workcell setup section). |
| [`transfer_validation.py`](transfer_validation.py) | `MonomerTransferRow` Pydantic model and `validate_transfer_array` (schema + destination per-well cap + 24-well source well cap). |
| [`lhs_plots.py`](lhs_plots.py) | Optional marginal and pairwise LHS PNGs (requires dev dependency `matplotlib`). |

**Plate layout:** all liquid handler steps use a single **24-well source plate** (`source_24w`) holding six reagent stocks (`A1`-`A6`) and the bacterial inoculum (`B1`). Transfers land in a **96-well experiment plate** (`experiment`, starts empty). The source well cap is **8.5 mL**; `validate_transfer_array` raises a `ValueError` if any source well exceeds it. Not every `--seed` will be feasible -- if generation fails, try a different seed or increase stock concentrations in `StockConfig`.

**CLI (repo root):** `uv run python scripts/generate_reagent_design.py`  
See the root [README.md](../../README.md) Quick start for flags (`--seed`, `--plots`, iteration argument).

**Library:** import `generate_reagent_lhs_bundle`, `write_reagent_design_outputs`, and `validate_transfer_array` from [`src.design`](__init__.py). The names `generate_iter_001_bundle` and `write_iter_001_outputs` are aliases for older call sites.
