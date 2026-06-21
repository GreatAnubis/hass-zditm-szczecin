# ZDiTM Szczecin — integracja Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.11%2B-blue.svg)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data: ZDiTM Szczecin (CC0)](https://img.shields.io/badge/data-ZDiTM%20Szczecin%20(CC0)-2e7d32.svg)](https://www.zditm.szczecin.pl/)

**Polski** · [English ↓](#english)

Integracja udostępniająca odjazdy komunikacji miejskiej **ZDiTM Szczecin** jako encje
Home Assistant — do automatyzacji, powiadomień i dashboardów.

## Funkcje (v1)

- Jedno urządzenie na przystanek; można dodać wiele przystanków.
- **Sensor „następny odjazd"** na przystanek: stan = liczba minut do najbliższego odjazdu,
  a w atrybutach pełna lista odjazdów (linia, kierunek, minuty, live/rozkładowy, kategoria).
- Opcjonalne sensory **per linia+kierunek** do wygodnych automatyzacji `numeric_state`
  (np. „tramwaj 3 w kierunku Pomorzan odjeżdża za ≤ 8 min").
- Wyszukiwanie przystanku po nazwie w konfiguracji; pary linia+kierunek wybierane z bieżącej tablicy.
- Konfigurowalny interwał odświeżania (30/60/90/120/300 s); odpytywanie per przystanek
  respektuje limit 100 zapytań/min ZDiTM.

> v1 korzysta wyłącznie z API tablicy „na żywo", które pokazuje odjazdy do najbliższego
> horyzontu czasowego. Nocą może nie pokazywać odjazdów. Pełna obsługa 24h/nocna (GTFS)
> planowana jest osobno.

## Instalacja (HACS)

Dodaj to repozytorium jako repozytorium własne (kategoria: **Integration**), zainstaluj,
zrestartuj Home Assistant, a następnie **Ustawienia → Urządzenia i usługi → Dodaj integrację
→ ZDiTM Szczecin**.

## Dane

Dane o odjazdach: **ZDiTM Szczecin** (licencja CC0).

---

## English

[↑ Polski](#zditm-szczecin--integracja-home-assistant)

Custom integration exposing **ZDiTM Szczecin** public-transport departures as Home Assistant
entities, for automations, notifications and dashboards.

### Features (v1)

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

### Installation (HACS)

Add this repository as a custom repository (category: **Integration**), install, restart HA,
then **Settings → Devices & Services → Add Integration → ZDiTM Szczecin**.

### Data

Departure data: **ZDiTM Szczecin** (licence CC0).
