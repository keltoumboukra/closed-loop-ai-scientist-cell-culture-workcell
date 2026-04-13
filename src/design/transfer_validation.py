"""Pydantic validation for Monomer-style transfer_array JSON."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.design.constants import (
    MAX_SOURCE_WELL_VOLUME_UL,
    MAX_WELL_VOLUME_UL,
    MIN_TRANSFER_VOLUME_UL,
    SOURCE_PLATE_ID,
)


class MonomerTransferRow(BaseModel):
    """One transfer step from the 24-well source plate to the 96-well experiment plate.

    Reagent rows have no post-mix fields.  Inoculum rows carry post_mix_volume and
    post_mix_reps (both required together when present).
    """

    model_config = ConfigDict(extra="forbid")

    src_plate: str
    src_well: str
    dst_plate: str
    dst_well: str
    volume: float = Field(gt=0)
    new_tip: str
    blow_out: bool
    post_mix_volume: float | None = Field(default=None, gt=0)
    post_mix_reps: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _post_mix_fields_consistent(self) -> MonomerTransferRow:
        has_vol = self.post_mix_volume is not None
        has_reps = self.post_mix_reps is not None
        if has_vol != has_reps:
            raise ValueError(
                "post_mix_volume and post_mix_reps must both be present or both absent"
            )
        return self

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        """Omit None post-mix fields so JSON stays clean for reagent rows."""
        d = super().model_dump(**kwargs)
        if d.get("post_mix_volume") is None:
            d.pop("post_mix_volume", None)
        if d.get("post_mix_reps") is None:
            d.pop("post_mix_reps", None)
        return d


# Keep old names as aliases so any external code that imported them still works.
MonomerReagentTransferRow = MonomerTransferRow
MonomerCellCultureTransferRow = MonomerTransferRow


def validate_transfer_array(
    xfer: list[Any],
    *,
    max_well_volume_ul: float = MAX_WELL_VOLUME_UL,
    min_transfer_volume_ul: float = MIN_TRANSFER_VOLUME_UL,
    max_source_well_volume_ul: float = MAX_SOURCE_WELL_VOLUME_UL,
) -> list[MonomerTransferRow]:
    """Parse and validate transfer rows before JSON hits the workcell.

    Checks:
    - Each row matches the ``MonomerTransferRow`` schema (extra keys forbidden).
    - Every ``volume`` is at least ``min_transfer_volume_ul``.
    - Total volume dispensed into each ``(dst_plate, dst_well)`` is at most
      ``max_well_volume_ul``.
    - Total volume aspirated from each ``(src_plate, src_well)`` is at most
      ``max_source_well_volume_ul`` (24-well source plate cap).

    Raises:
        pydantic.ValidationError: invalid row shape or forbidden keys.
        ValueError: minimum transfer or per-well volume cap violated.
    """
    rows = [MonomerTransferRow.model_validate(r) for r in xfer]
    eps = 1e-9

    for idx, r in enumerate(rows):
        if r.volume + eps < min_transfer_volume_ul:
            msg = (
                f"Transfer index {idx}: volume {r.volume} µL is below minimum "
                f"{min_transfer_volume_ul} µL"
            )
            raise ValueError(msg)

    per_dst: dict[tuple[str, str], float] = defaultdict(float)
    per_src: dict[tuple[str, str], float] = defaultdict(float)
    for r in rows:
        per_dst[(r.dst_plate, r.dst_well)] += r.volume
        per_src[(r.src_plate, r.src_well)] += r.volume

    for (plate, well), total in sorted(per_dst.items()):
        if total > max_well_volume_ul + eps:
            msg = (
                f"Total dispensed into {plate!r} well {well!r} is {total:.4f} µL, "
                f"above cap {max_well_volume_ul:.4f} µL"
            )
            raise ValueError(msg)

    for (plate, well), total in sorted(per_src.items()):
        if total > max_source_well_volume_ul + eps:
            msg = (
                f"Total aspirated from {plate!r} well {well!r} is {total:.2f} µL "
                f"({total / 1000:.2f} mL), above 24-well source cap "
                f"{max_source_well_volume_ul:.0f} µL "
                f"({max_source_well_volume_ul / 1000:.1f} mL). "
                f"Try a different --seed or increase stock concentration."
            )
            raise ValueError(msg)

    return rows


__all__ = [
    "SOURCE_PLATE_ID",  # re-exported for convenience
    "MonomerCellCultureTransferRow",
    "MonomerReagentTransferRow",
    "MonomerTransferRow",
    "validate_transfer_array",
]
