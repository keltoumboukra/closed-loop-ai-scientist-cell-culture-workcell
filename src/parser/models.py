"""
Data models for the parser component.

These Pydantic models define the contracts between the data parser and the
rest of the system (experiment designer, Bayesian optimizer, webapp).

Terminology
-----------
- **Well**: A single position in a 96-well plate where cells grow.
- **OD600 (Optical Density at 600nm)**: A measurement of how much light passes
  through the cell suspension. Higher OD = more cells. This is the standard
  proxy for cell density.

Growth Metrics
--------------
The parser computes the following values per well from the OD600 time series:

- **growth_rate** (1/hour): The specific growth rate (mu) during exponential
  phase. Cells in exponential phase follow OD(t) = OD_0 * e^(mu*t). We compute
  mu by fitting a linear regression to ln(OD) vs time -- the slope is mu.
  **This is the primary optimization target**: higher growth_rate = faster
  cell division = what the Bayesian optimizer maximizes.

- **doubling_time_hours** (hours): How long it takes the cell population to
  double. Calculated as ln(2) / growth_rate. This is a more intuitive way to
  express the same information -- a doubling time of 2h means faster growth
  than 4h. Useful for sanity-checking against known literature values.

- **r_squared** (0 to 1): Coefficient of determination for the exponential
  fit. Measures how well the exponential model explains the observed data.
  Values above ~0.95 indicate a reliable growth rate estimate. Low values
  suggest the well may not have entered proper exponential growth, or the
  data window includes lag/stationary phase. This is a **data quality
  indicator** -- it flags unreliable wells so the optimizer can down-weight
  or exclude them.

- **max_od** (float): The highest OD600 reading observed during the valid
  data window. Represents the peak cell density achieved in the well.
  **Second optimization target** for multi-objective BO: higher max_od =
  more total biomass produced. Can trade off against growth_rate (e.g.,
  high glucose may give fast initial growth but acid crash lowers final OD).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Input models (well-to-design mapping from experiment designer)
# ---------------------------------------------------------------------------


class WellDesign(BaseModel):
    """A single well's experimental design parameters."""

    well: str = Field(description="Well position on the plate, e.g. 'A3'")
    params: dict[str, float] = Field(
        description=(
            "Design parameters for this well. Examples: reagent LHS uses keys like "
            "`nacl_g_per_L`, `mops_mM`, `design_type`, `final_volume_uL`; "
            "older layouts used `cell_volume_uL`, `mix_height_mm`, `mix_reps`."
        )
    )


class DesignMapping(BaseModel):
    """Maps each well in a plate to its experimental design parameters.

    Produced by the experiment designer before each iteration and stored at:
        data/iterations/iter_NNN/input/well_to_design_mapping.json
    """

    designs: list[WellDesign]


# ---------------------------------------------------------------------------
# Output models (growth metrics consumed by BO and webapp)
# ---------------------------------------------------------------------------


class WellResult(BaseModel):
    """Growth metrics for a single well, linked to its design parameters.

    See module docstring for detailed metric definitions.
    """

    well: str = Field(description="Well position, e.g. 'A3'")
    parent_well: str = Field(description="Well this was passaged from (e.g. 'A1' or 'stock')")
    params: dict[str, float] = Field(description="Design parameters used for this well")
    growth_rate: float = Field(
        description="Specific growth rate mu (1/hour). "
        "Slope of ln(OD) vs time during exponential phase. "
        "PRIMARY OPTIMIZATION TARGET: higher = faster growth."
    )
    doubling_time_hours: float | None = Field(
        description="Time for population to double: ln(2)/growth_rate. "
        "None if growth_rate <= 0 (no valid growth detected)."
    )
    r_squared: float = Field(
        description="R-squared of the exponential fit (0-1). "
        "Data quality indicator: >0.95 = reliable, <0.8 = suspect."
    )
    max_od: float = Field(
        description="Peak OD600 observed during valid data window. "
        "Second optimization target for multi-objective BO: higher = more biomass."
    )
    n_datapoints: int = Field(description="Number of valid OD readings used in the fit")
    time_range_hours: float = Field(description="Time span of valid data in hours")


class IterationMetrics(BaseModel):
    """Complete growth metrics for one iteration (all wells).

    Stored at: data/iterations/iter_NNN/analysis/growth_metrics.json
    Consumed by: experiment designer (BO), webapp dashboard.
    """

    iteration_id: str = Field(description="Iteration identifier, e.g. 'iter_001'")
    results: list[WellResult]
