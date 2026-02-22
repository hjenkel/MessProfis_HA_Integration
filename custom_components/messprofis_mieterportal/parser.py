"""Parser helpers for the MessProfis API response payload."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha1
from typing import Any

from .const import SUPPORTED_METRICS
from .models import ApartmentReading, MonthlyValue


def parse_iso_date(date_str: str) -> datetime:
    """Parse API date values like '2026-01-31T00:00:00'."""
    return datetime.fromisoformat(date_str)


def _safe_float(value: Any) -> float | None:
    """Convert values to float where possible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_latest_month_value(section: dict[str, Any]) -> MonthlyValue | None:
    """Return the newest valid value in section['monate']."""
    monate = section.get("monate", [])
    if not isinstance(monate, list) or not monate:
        return None

    valid_entries: list[tuple[datetime, str, float, bool]] = []
    for month in monate:
        if not isinstance(month, dict):
            continue
        try:
            datum = str(month["datum"])
            parsed_date = parse_iso_date(datum)
            wert = float(month["wert"])
        except (KeyError, TypeError, ValueError):
            continue

        estimated = bool(month.get("enthaeltSchaetzung", False))
        valid_entries.append((parsed_date, datum, wert, estimated))

    if not valid_entries:
        return None

    valid_entries.sort(key=lambda item: item[0], reverse=True)
    _, datum, wert, estimated = valid_entries[0]
    return MonthlyValue(datum=datum, wert=wert, estimated=estimated)


def _build_apartment_key(title1: str, title2: str, fallback_index: int) -> str:
    """Generate a stable key from titles and fallback index."""
    base = f"{title1}|{title2}".strip("|")
    if not base:
        return f"wohnung_{fallback_index}"
    return sha1(base.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


def extract_apartment_readings(payload: list[dict[str, Any]]) -> list[ApartmentReading]:
    """Normalize API payload to apartment readings."""
    readings: list[ApartmentReading] = []

    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            continue

        title1 = str(item.get("title1") or "")
        title2 = str(item.get("title2") or "")
        status_raw = item.get("status")
        status = str(status_raw) if status_raw is not None else None
        apartment_key = _build_apartment_key(title1, title2, fallback_index=index)

        werte = item.get("werte", {})
        if not isinstance(werte, dict):
            werte = {}

        values: dict[str, MonthlyValue | None] = {}
        jahreswerte: dict[str, float | None] = {}

        for metric in SUPPORTED_METRICS:
            metric_obj = werte.get(metric, {})
            if not isinstance(metric_obj, dict):
                metric_obj = {}
            aktuell = metric_obj.get("aktuell", {})
            if not isinstance(aktuell, dict):
                aktuell = {}

            values[metric] = get_latest_month_value(aktuell)
            jahreswerte[metric] = _safe_float(aktuell.get("jahreswert"))

        readings.append(
            ApartmentReading(
                apartment_key=apartment_key,
                title1=title1,
                title2=title2,
                status=status,
                values=values,
                jahreswerte=jahreswerte,
            )
        )

    return readings
