def build_trade_query(country: str, period: str) -> dict[str, str]:
    return {"country": country, "period": period, "source": "UN Comtrade API"}
