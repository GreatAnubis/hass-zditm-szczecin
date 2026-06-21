# ZDiTM Szczecin — Home Assistant integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.11%2B-blue.svg)](https://www.home-assistant.io/)
[![Data: ZDiTM Szczecin (CC0)](https://img.shields.io/badge/data-ZDiTM%20Szczecin%20(CC0)-2e7d32.svg)](https://www.zditm.szczecin.pl/)

Custom integration exposing ZDiTM Szczecin public-transport departures as Home Assistant
entities, for automations, notifications and dashboards.

## Features (v1)

- One device per stop; add multiple stops.
- **Next-departure sensor** per stop: state = minutes to the next departure, with the full
  departures list (line, direction, minutes, live/scheduled, category) in attributes.
- Optional **per line+direction** sensors for clean `numeric_state` automations
  (e.g. "tram 3 toward Pomorzany departs in ≤ 8 min").
- Stop search by name in the config flow; line+direction pairs picked from the live board.
- Configurable refresh interval (30/60/90/120/300 s); per-stop polling respects the
  ZDiTM 100 req/min limit.

> v1 uses the live-board API only, which shows departures up to the near-term horizon.
> At night it may report no departures. Full 24h/night support (GTFS) is planned separately.

## Installation (HACS)

Add this repository as a custom repository (category: **Integration**), install, restart HA,
then **Settings → Devices & Services → Add Integration → ZDiTM Szczecin**.

## Data

Departure data: **ZDiTM Szczecin** (licence CC0).
