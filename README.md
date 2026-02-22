# MessProfis Mieterportal Home Assistant Integration

Custom Home Assistant integration for the Mess-Profis Mieterportal API.

Current MVP scope:
- Login/data fetch via `Mail` + `PasswordHash`
- 4 sensors per apartment:
  - `Heizung aktuell` (kWh)
  - `Kaltwasser aktuell` (m³)
  - `Warmwasser aktuell` (kWh)
  - `Warmwasser aktuell (m³)`
- Attributes per sensor:
  - `last_month_date`
  - `estimated`
  - `jahreswert`

## Installation

### Option A: HACS (Custom Repository)
1. Open `HACS -> Integrations -> ⋮ -> Custom repositories`.
2. Add repository URL:
   - `https://github.com/hjenkel/MessProfis_Mieterportal_HAIntegration`
3. Category: `Integration`.
4. Search for `MessProfis Mieterportal` in HACS and install.
5. Restart Home Assistant.

### Option B: Manual
1. Copy `custom_components/messprofis_mieterportal` to:
   - `<config>/custom_components/messprofis_mieterportal`
2. Restart Home Assistant.

## Configuration
1. Open `Settings -> Devices & Services -> Add Integration`.
2. Select `MessProfis Mieterportal`.
3. Enter:
   - `Email`
   - `PasswordHash`

Optional:
- In integration options, adjust `update_interval_hours` (default: `12`, allowed: `6..48`).

## Notes
- This MVP expects a ready-to-use `PasswordHash`.
- Plain password login flow and hash generation are not included yet.
- The integration uses the latest available monthly entry as the "current" value.

## Local API Test Client
For API debugging outside Home Assistant (developer tool, not required for HA installation):

```bash
export MESSPROFIS_EMAIL="user@example.com"
export MESSPROFIS_PASSWORD_HASH="your_hash"
python3 scripts/messprofis-test.py
```

## Data Source
- Endpoint: `POST https://mieterportal.mess-profis.de/api/Mieter/Login`
