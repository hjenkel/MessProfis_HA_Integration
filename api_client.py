#!/usr/bin/env python3
"""Standalone MessProfis API client (without external dependencies)."""

from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha1
import urllib.error
import urllib.request
from typing import Any

LOGIN_URL = "https://mieterportal.mess-profis.de/api/Mieter/Login"
SUPPORTED_METRICS: tuple[str, ...] = (
    "heizung",
    "kaltwasser",
    "warmwasser",
    "warmwasserM3",
)


class ApiClientError(Exception):
    """Base API client error."""


class ApiAuthError(ApiClientError):
    """Authentication failure."""


def _parse_iso_date(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str)


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _latest_month_value(section: dict[str, Any]) -> dict[str, Any] | None:
    monate = section.get("monate", [])
    if not isinstance(monate, list) or not monate:
        return None

    valid_entries: list[tuple[datetime, str, float, bool]] = []
    for month in monate:
        if not isinstance(month, dict):
            continue
        try:
            datum = str(month["datum"])
            parsed_date = _parse_iso_date(datum)
            wert = float(month["wert"])
        except (KeyError, TypeError, ValueError):
            continue
        estimated = bool(month.get("enthaeltSchaetzung", False))
        valid_entries.append((parsed_date, datum, wert, estimated))

    if not valid_entries:
        return None

    valid_entries.sort(key=lambda item: item[0], reverse=True)
    _, datum, wert, estimated = valid_entries[0]
    return {"value": wert, "date": datum, "estimated": estimated}


def _apartment_key(title1: str, title2: str, fallback_index: int) -> str:
    base = f"{title1}|{title2}".strip("|")
    if not base:
        return f"wohnung_{fallback_index}"
    return sha1(base.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


def fetch_data(email: str, password_hash: str, timeout: int = 30) -> list[dict[str, Any]]:
    """Fetch raw payload from MessProfis login endpoint."""
    payload = json.dumps({"Mail": email, "PasswordHash": password_hash}).encode("utf-8")

    request = urllib.request.Request(
        LOGIN_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://mieterportal.mess-profis.de",
            "Referer": "https://mieterportal.mess-profis.de/login",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        if err.code in (401, 403):
            raise ApiAuthError("Authentication failed") from err
        raise ApiClientError(f"HTTP error {err.code}") from err
    except urllib.error.URLError as err:
        raise ApiClientError(f"Network error: {err.reason}") from err

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as err:
        raise ApiClientError("Invalid JSON response") from err

    if not isinstance(parsed, list):
        raise ApiClientError("Unexpected API format, expected a list")
    if not all(isinstance(item, dict) for item in parsed):
        raise ApiClientError("Unexpected API format, expected list of objects")
    return parsed


def extract_latest_values(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract compact latest-value summaries from payload."""
    result: list[dict[str, Any]] = []

    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            continue

        title1 = str(item.get("title1") or "")
        title2 = str(item.get("title2") or "")
        status_raw = item.get("status")
        status = str(status_raw) if status_raw is not None else None
        apartment_key = _apartment_key(title1, title2, fallback_index=index)

        werte = item.get("werte", {})
        if not isinstance(werte, dict):
            werte = {}

        apartment_summary: dict[str, Any] = {
            "apartment_key": apartment_key,
            "title1": title1,
            "title2": title2,
            "status": status,
            "metrics": {},
        }

        for metric in SUPPORTED_METRICS:
            metric_obj = werte.get(metric, {})
            if not isinstance(metric_obj, dict):
                metric_obj = {}
            aktuell = metric_obj.get("aktuell", {})
            if not isinstance(aktuell, dict):
                aktuell = {}

            monthly = _latest_month_value(aktuell)
            apartment_summary["metrics"][metric] = {
                "value": None if monthly is None else monthly["value"],
                "date": None if monthly is None else monthly["date"],
                "estimated": None if monthly is None else monthly["estimated"],
                "jahreswert": _safe_float(aktuell.get("jahreswert")),
            }

        result.append(apartment_summary)

    return result
