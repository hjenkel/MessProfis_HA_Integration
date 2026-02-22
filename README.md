# MessProfis Mieterportal Home Assistant Integration

Benutzerdefinierte Home-Assistant-Integration fuer die API des Mess-Profis Mieterportals.

Aktueller MVP-Umfang:
- Login/Datenabruf ueber `Mail` + `PasswordHash`
- 4 Sensoren pro Wohnung:
  - `Heizung aktuell` (kWh)
  - `Kaltwasser aktuell` (m³)
  - `Warmwasser aktuell` (kWh)
  - `Warmwasser aktuell (m³)`
- Attribute pro Sensor:
  - `last_month_date`
  - `estimated`
  - `jahreswert`

## Installation

### Option A: HACS (Custom Repository)
1. Oeffne `HACS -> Integrationen -> ⋮ -> Benutzerdefinierte Repositories`.
2. Fuege die Repository-URL hinzu:
   - `https://github.com/hjenkel/MessProfis_Mieterportal_HAIntegration`
3. Kategorie: `Integration`.
4. Suche in HACS nach `MessProfis Mieterportal` und installiere die Integration.
5. Starte Home Assistant neu.

### Option B: Manuell
1. Kopiere `custom_components/messprofis_mieterportal` nach:
   - `<config>/custom_components/messprofis_mieterportal`
2. Starte Home Assistant neu.

## Konfiguration
1. Oeffne `Einstellungen -> Geraete & Dienste -> Integration hinzufuegen`.
2. Waehle `MessProfis Mieterportal`.
3. Trage ein:
   - `Email`
   - `PasswordHash`

Optional:
- In den Integrationsoptionen kannst du `update_interval_hours` anpassen (Standard: `12`, erlaubt: `6..48`).

## Hinweise
- Dieses MVP erwartet einen bereits vorhandenen `PasswordHash`.
- Ein Login-Flow mit Klartextpasswort und Hash-Erzeugung ist noch nicht enthalten.
- Als "aktueller" Wert wird immer der zuletzt verfuegbare Monatseintrag verwendet.

## Lokaler API-Testclient
Fuer API-Debugging ausserhalb von Home Assistant (Entwicklerwerkzeug, nicht fuer die HA-Installation erforderlich):

```bash
export MESSPROFIS_EMAIL="user@example.com"
export MESSPROFIS_PASSWORD_HASH="your_hash"
python3 scripts/messprofis-test.py
```

## Datenquelle
- Endpoint: `POST https://mieterportal.mess-profis.de/api/Mieter/Login`
