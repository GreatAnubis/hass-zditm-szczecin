"""Thin async client for the ZDiTM Szczecin public API."""
from __future__ import annotations

import asyncio

import aiohttp

API_BASE = "https://www.zditm.szczecin.pl/api/v1"
_TIMEOUT = aiohttp.ClientTimeout(total=15)


class ZditmApiError(Exception):
    """Raised when the API returns an unexpected response."""


class ZditmConnectionError(ZditmApiError):
    """Raised when the API cannot be reached."""


async def _get_json(session: aiohttp.ClientSession, path: str):
    url = f"{API_BASE}{path}"
    try:
        async with session.get(url, timeout=_TIMEOUT) as resp:
            if resp.status != 200:
                raise ZditmApiError(f"HTTP {resp.status} for {url}")
            return await resp.json()
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise ZditmConnectionError(f"Cannot reach {url}: {err}") from err


async def fetch_display(session: aiohttp.ClientSession, stop_number: str) -> dict:
    """Live board for one stop."""
    return await _get_json(session, f"/displays/{stop_number}")


async def fetch_stops(session: aiohttp.ClientSession) -> list[dict]:
    """All stops (the `data` list)."""
    data = await _get_json(session, "/stops")
    return data.get("data", [])


async def fetch_lines(session: aiohttp.ClientSession) -> list[dict]:
    """All lines (the `data` list)."""
    data = await _get_json(session, "/lines")
    return data.get("data", [])
