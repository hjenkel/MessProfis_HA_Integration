# MessProfis Mieterportal Home Assistant Integration

Benutzerdefinierte Home-Assistant-Integration für die API des Mess-Profis Mieterportals.

Aktueller MVP-Umfang:
- Login/Datenabruf über `Mail` + `PasswordHash`
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
1. Öffne `HACS -> Integrationen -> ⋮ -> Benutzerdefinierte Repositories`.
2. Füge die Repository-URL hinzu:
   - `https://github.com/hjenkel/MessProfis_Mieterportal_HAIntegration`
3. Kategorie: `Integration`.
4. Suche in HACS nach `MessProfis Mieterportal` und installiere die Integration.
5. Starte Home Assistant neu.

### Option B: Manuell (ohne HACS)
1. Kopiere `custom_components/messprofis_mieterportal` nach:
   - `<config>/custom_components/messprofis_mieterportal`
2. Starte Home Assistant neu.
3. Öffne in Home Assistant `Einstellungen -> Geräte & Dienste -> Integration hinzufügen`.
4. Suche nach `MessProfis Mieterportal` und richte die Integration ein.

## Konfiguration
1. Öffne `Einstellungen -> Geräte & Dienste -> Integration hinzufügen`.
2. Wähle `MessProfis Mieterportal`.
3. Trage ein:
   - `Email`
   - `PasswordHash`

Optional:
- In den Integrationsoptionen kannst du `update_interval_hours` anpassen (Standard: `12`, erlaubt: `6..48`).

## Hinweise
- Dieses MVP erwartet einen bereits vorhandenen `PasswordHash`.
- Ein Login-Flow mit Klartextpasswort und Hash-Erzeugung ist noch nicht enthalten.
- Als "aktueller" Wert wird immer der zuletzt verfügbare Monatseintrag verwendet.

## So kommst du an den PasswordHash
1. Logge dich im Mieterportal im Browser normal ein.
2. Öffne die Entwicklerwerkzeuge des Browsers.
3. Wechsle in den Tab `Netzwerk`.
4. Suche die Anfrage `Login`.
5. Kopiere diese Anfrage als `cURL`.
6. Öffne den cURL-Text in einem Texteditor.
7. In der letzten Zeile siehst du in der JSON-Nutzlast sowohl `Mail` als auch `PasswordHash`.

## Lokaler API-Testclient
Für API-Debugging außerhalb von Home Assistant (Entwicklerwerkzeug, nicht für die HA-Installation erforderlich):

```bash
export MESSPROFIS_EMAIL="user@example.com"
export MESSPROFIS_PASSWORD_HASH="your_hash"
python3 scripts/messprofis-test.py
```

## Datenquelle
- Endpoint: `POST https://mieterportal.mess-profis.de/api/Mieter/Login`
