"""Typed models for parsed MessProfis API data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MonthlyValue:
    """A normalized monthly value entry."""

    datum: str
    wert: float
    estimated: bool


@dataclass(slots=True)
class ApartmentReading:
    """Normalized readings for one apartment/unit."""

    apartment_key: str
    title1: str
    title2: str
    status: str | None
    values: dict[str, MonthlyValue | None]
    jahreswerte: dict[str, float | None]
