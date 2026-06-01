def build_weather_query(region: str) -> dict[str, str]:
    return {"region": region, "source": "OpenWeather API"}
