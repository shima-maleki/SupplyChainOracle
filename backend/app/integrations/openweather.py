from datetime import UTC, datetime

from backend.app.schemas.risk import Disruption, RiskLevel


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
