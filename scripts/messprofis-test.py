#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys

from api_client import ApiAuthError, ApiClientError, extract_latest_values, fetch_data


def main() -> int:
    """Simple CLI test script for the MessProfis API."""
    email = os.getenv("MESSPROFIS_EMAIL", "").strip()
    password_hash = os.getenv("MESSPROFIS_PASSWORD_HASH", "").strip()

    if not email or not password_hash:
        print(
            "Bitte Umgebungsvariablen setzen: MESSPROFIS_EMAIL und "
            "MESSPROFIS_PASSWORD_HASH"
        )
        return 2

    try:
        raw_data = fetch_data(email=email, password_hash=password_hash)
        summary = extract_latest_values(raw_data)
    except ApiAuthError as err:
        print(f"Auth-Fehler: {err}")
        return 3
    except ApiClientError as err:
        print(f"API-Fehler: {err}")
        return 4

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
