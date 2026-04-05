"""Shared numeric limits for reagent design and transfer validation."""

# Total liquid per experiment well must not exceed this (96-well plate target fill).
MAX_WELL_VOLUME_UL = 200.0

# Liquid handler: do not schedule transfers below this volume (µL).
MIN_TRANSFER_VOLUME_UL = 10.0
