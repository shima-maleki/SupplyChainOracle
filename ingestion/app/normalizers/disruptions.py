def normalize_severity(value: str | None) -> str:
    if not value:
        return "Medium"
    normalized = value.strip().title()
    if normalized in {"Low", "Medium", "High"}:
        return normalized
    return "Medium"
