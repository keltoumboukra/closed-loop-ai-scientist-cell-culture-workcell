"""Experiment design generation (reagent LHS, Monomer transfer_array, validation)."""

from src.design.constants import MAX_WELL_VOLUME_UL, MIN_TRANSFER_VOLUME_UL
from src.design.lhs_plots import (
    lhs_sample_matrix_from_mapping,
    write_lhs_visualization_files,
)
from src.design.reagent_iteration import (
    StockConfig,
    build_transfer_array,
    generate_iter_001_bundle,
    generate_reagent_lhs_bundle,
    write_iter_001_outputs,
    write_reagent_design_outputs,
)
from src.design.transfer_validation import (
    MonomerCellCultureTransferRow,
    MonomerReagentTransferRow,
    MonomerTransferRow,
    validate_transfer_array,
)

__all__ = [
    "MAX_WELL_VOLUME_UL",
    "MIN_TRANSFER_VOLUME_UL",
    "MonomerCellCultureTransferRow",
    "MonomerReagentTransferRow",
    "MonomerTransferRow",
    "StockConfig",
    "build_transfer_array",
    "generate_iter_001_bundle",
    "generate_reagent_lhs_bundle",
    "lhs_sample_matrix_from_mapping",
    "validate_transfer_array",
    "write_iter_001_outputs",
    "write_lhs_visualization_files",
    "write_reagent_design_outputs",
]
