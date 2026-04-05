"""Experiment design generation (e.g. reagent LHS layouts for iter_001)."""

from src.design.reagent_iteration import (
    MAX_WELL_VOLUME_UL,
    StockConfig,
    build_transfer_array,
    generate_iter_001_bundle,
    write_iter_001_outputs,
)

__all__ = [
    "MAX_WELL_VOLUME_UL",
    "StockConfig",
    "build_transfer_array",
    "generate_iter_001_bundle",
    "write_iter_001_outputs",
]
