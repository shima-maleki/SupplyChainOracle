from datetime import UTC, datetime
from hashlib import sha256

import httpx

from backend.app.config import get_settings
from backend.app.schemas.risk import Disruption, RiskLevel

WEATHER_REGIONS = {
    "Germany": "Berlin,DE",
    "Netherlands": "Rotterdam,NL",
    "China": "Shanghai,CN",
    "Spain": "Madrid,ES",
}


def fetch_weather_disruptions() -> list[Disruption]:
    settings = get_settings()
    if not settings.openweather_api_key:
        return []

    disruptions: list[Disruption] = []
    for region, location in WEATHER_REGIONS.items():
        response = httpx.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": location,
                "appid": settings.openweather_api_key,
                "units": "metric",
            },
            timeout=15,
        )
        response.raise_for_status()
        disruption = normalize_current_weather(response.json(), region)
        if disruption:
            disruptions.append(disruption)

    return disruptions


def normalize_weather_alert(payload: dict) -> Disruption:
    region = str(payload.get("region") or payload.get("country") or "Unknown")
    event = str(payload.get("event") or "Weather Alert")
    severity = RiskLevel(str(payload.get("severity") or "Medium"))
    timestamp = payload.get("timestamp")

    return Disruption(
        id=f"weather-{region.lower()}-{event.lower()}".replace(" ", "-"),
        title=f"{event} detected in {region}",
        description=str(payload.get("description") or f"{event} may affect supply chain routes in {region}."),
        region=region,
        severity=severity,
        source="OpenWeather API",
        url=None,
        created_at=datetime.fromisoformat(timestamp) if timestamp else datetime.now(UTC),
    )


def normalize_current_weather(payload: dict, region: str) -> Disruption | None:
    weather = (payload.get("weather") or [{}])[0]
    main = str(weather.get("main") or "Weather")
    description = str(weather.get("description") or main).title()
    wind_speed = float(payload.get("wind", {}).get("speed") or 0)
    rainfall = float(payload.get("rain", {}).get("1h") or payload.get("rain", {}).get("3h") or 0)
    snow = float(payload.get("snow", {}).get("1h") or payload.get("snow", {}).get("3h") or 0)
    temperature = float(payload.get("main", {}).get("temp") or 0)

    severity = classify_weather_severity(main, wind_speed, rainfall, snow, temperature)
    if severity == RiskLevel.low:
        return None

    created_at = datetime.fromtimestamp(int(payload.get("dt") or datetime.now(UTC).timestamp()), UTC)
    event_key = f"{region}|{main}|{created_at.isoformat()}"

    return Disruption(
        id=f"weather-{sha256(event_key.encode()).hexdigest()[:16]}",
        title=f"{description} conditions reported in {region}",
        description=(
            f"OpenWeather reports {description.lower()} near {region}; "
            f"wind {wind_speed:.1f} m/s, rain {rainfall:.1f} mm, snow {snow:.1f} mm, "
            f"temperature {temperature:.1f} C."
        ),
        region=region,
        severity=severity,
        source="OpenWeather API",
        url=None,
        created_at=created_at,
    )


def classify_weather_severity(
    condition: str,
    wind_speed: float,
    rainfall: float,
    snow: float,
    temperature: float,
) -> RiskLevel:
    condition_lower = condition.lower()
    if (
        condition_lower in {"thunderstorm", "tornado", "squall"}
        or wind_speed >= 15
        or rainfall >= 8
        or snow >= 5
        or temperature <= -10
        or temperature >= 40
    ):
        return RiskLevel.high
    if condition_lower in {"rain", "snow", "drizzle"} or wind_speed >= 9 or rainfall >= 2 or snow > 0:
        return RiskLevel.medium
    return RiskLevel.low
