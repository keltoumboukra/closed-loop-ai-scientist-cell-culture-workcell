"""Pydantic validation for Monomer-style transfer_array JSON."""

from __future__ import annotations

from collections import defaultdict
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Discriminator, Field, TypeAdapter

from src.design.constants import MAX_WELL_VOLUME_UL, MIN_TRANSFER_VOLUME_UL


class MonomerReagentTransferRow(BaseModel):
    """One reagent-plate dispense into the experiment plate."""

    model_config = ConfigDict(extra="forbid")

    src_plate: Literal["reagent"]
    src_well: str
    dst_plate: Literal["experiment"]
    dst_well: str
    volume: float = Field(gt=0)
    new_tip: Literal["once", "always"]
    blow_out: bool


class MonomerCellCultureTransferRow(BaseModel):
    """Inoculum transfer (cell stock) with optional post-mix parameters."""

    model_config = ConfigDict(extra="forbid")

    src_plate: Literal["cell_culture_stock"]
    src_well: str
    dst_plate: Literal["experiment"]
    dst_well: str
    volume: float = Field(gt=0)
    post_mix_volume: float = Field(gt=0)
    post_mix_reps: int = Field(ge=1)
    new_tip: Literal["once", "always"]
    blow_out: bool


MonomerTransferRow = Annotated[
    MonomerReagentTransferRow | MonomerCellCultureTransferRow,
    Discriminator("src_plate"),
]

_transfer_list_adapter = TypeAdapter(list[MonomerTransferRow])


def validate_transfer_array(
    xfer: list[Any],
    *,
    max_well_volume_ul: float = MAX_WELL_VOLUME_UL,
    min_transfer_volume_ul: float = MIN_TRANSFER_VOLUME_UL,
) -> list[MonomerReagentTransferRow | MonomerCellCultureTransferRow]:
    """Parse and check transfer rows before JSON hits the workcell.

    - Each row matches Monomer keys and types (discriminated by ``src_plate``).
    - Every dispense ``volume`` is at least ``min_transfer_volume_ul``.
    - Sum of ``volume`` into each ``(dst_plate, dst_well)`` is at most ``max_well_volume_ul``.

    Raises:
        pydantic.ValidationError: invalid row shape or forbidden keys.
        ValueError: per-well volume cap violated.
    """
    rows = _transfer_list_adapter.validate_python(xfer)
    eps = 1e-9
    for idx, r in enumerate(rows):
        if r.volume + eps < min_transfer_volume_ul:
            msg = (
                f"Transfer index {idx}: volume {r.volume} µL is below minimum "
                f"{min_transfer_volume_ul} µL"
            )
            raise ValueError(msg)
    per_well: dict[tuple[str, str], float] = defaultdict(float)
    for r in rows:
        key = (r.dst_plate, r.dst_well)
        per_well[key] += r.volume
    for (plate, well), total in sorted(per_well.items()):
        if total > max_well_volume_ul + eps:
            msg = (
                f"Total dispensed volume into {plate!r} well {well!r} is {total:.4f} µL, "
                f"above cap {max_well_volume_ul:.4f} µL"
            )
            raise ValueError(msg)
    return rows
