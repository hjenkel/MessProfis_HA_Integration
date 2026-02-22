"""Constants for the MessProfis Mieterportal integration."""

from datetime import timedelta

DOMAIN = "messprofis_mieterportal"

LOGIN_URL = "https://mieterportal.mess-profis.de/api/Mieter/Login"

CONF_PASSWORD_HASH = "password_hash"
CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

DEFAULT_UPDATE_INTERVAL_HOURS = 12
MIN_UPDATE_INTERVAL_HOURS = 6
MAX_UPDATE_INTERVAL_HOURS = 48

DEFAULT_UPDATE_INTERVAL = timedelta(hours=DEFAULT_UPDATE_INTERVAL_HOURS)

METRIC_HEATING = "heizung"
METRIC_COLD_WATER = "kaltwasser"
METRIC_HOT_WATER_ENERGY = "warmwasser"
METRIC_HOT_WATER_VOLUME = "warmwasserM3"

SUPPORTED_METRICS: tuple[str, ...] = (
    METRIC_HEATING,
    METRIC_COLD_WATER,
    METRIC_HOT_WATER_ENERGY,
    METRIC_HOT_WATER_VOLUME,
)
