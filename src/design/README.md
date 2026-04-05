# Experiment design (`src/design`)

Code that builds **reagent Latin hypercube** layouts for the Monomer workcell: per-well medium parameters, `well_to_design_mapping.json`, and `transfer_array.json`.

| Module | Role |
|--------|------|
| [`constants.py`](constants.py) | `MAX_WELL_VOLUME_UL`, `MIN_TRANSFER_VOLUME_UL` (shared with transfer validation). |
| [`reagent_iteration.py`](reagent_iteration.py) | LHS sampling, well assignment, volume math, `build_transfer_array`, summary markdown. |
| [`transfer_validation.py`](transfer_validation.py) | Pydantic row models and `validate_transfer_array` (schema + per-well caps) before JSON is written. |
| [`lhs_plots.py`](lhs_plots.py) | Optional marginal and pairwise LHS PNGs (requires dev dependency `matplotlib`). |

**CLI (repo root):** `uv run python scripts/generate_reagent_design.py`  
See the root [README.md](../../README.md) Quick start for flags (`--seed`, `--plots`, iteration argument).

**Library:** import `generate_reagent_lhs_bundle`, `write_reagent_design_outputs`, and `validate_transfer_array` from [`src.design`](__init__.py). The names `generate_iter_001_bundle` and `write_iter_001_outputs` are aliases for older call sites.
