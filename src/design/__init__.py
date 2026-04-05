"""Experiment design generation (e.g. reagent LHS layouts for iter_001)."""

from src.design.reagent_iteration import (
    StockConfig,
    build_transfer_array,
    generate_iter_001_bundle,
    write_iter_001_outputs,
)

__all__ = [
    "StockConfig",
    "build_transfer_array",
    "generate_iter_001_bundle",
    "write_iter_001_outputs",
]
