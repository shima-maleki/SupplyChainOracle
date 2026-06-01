from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class Region(BaseModel):
    id: str
    name: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    last_updated: datetime


class Disruption(BaseModel):
    id: str
    title: str
    description: str
    region: str
    severity: RiskLevel
    source: str
    url: HttpUrl | None = None
    created_at: datetime


class Document(BaseModel):
    id: str
    title: str
    content: str
    region: str
    source: str
    url: HttpUrl | None = None
    published_at: datetime
    embedding_id: str | None = None


class TradeMetric(BaseModel):
    id: str
    country: str
    partner_country: str
    trade_flow: str
    commodity: str
    period: str
    trade_value: float
    quantity: float | None = None
    created_at: datetime


class HistoricalShipment(BaseModel):
    id: str
    order_id: str
    region: str
    warehouse: str
    delivery_status: str
    delay_days: int
    shipping_mode: str
    created_at: datetime


class RiskBreakdown(BaseModel):
    weather_severity: int = Field(ge=0, le=30)
    news_disruption_frequency: int = Field(ge=0, le=25)
    negative_sentiment: int = Field(ge=0, le=20)
    historical_delay_patterns: int = Field(ge=0, le=15)
    trade_activity_changes: int = Field(ge=0, le=10)


class RiskScoreResult(BaseModel):
    region: str
    score: int = Field(ge=0, le=100)
    level: RiskLevel
    breakdown: RiskBreakdown
    explanation: str


class DashboardSummary(BaseModel):
    global_risk_index: int = Field(ge=0, le=100)
    high_risk_regions: list[Region]
    disruptions_today: int
    regions: list[Region]
    recent_disruptions: list[Disruption]
    trade_metrics: list[TradeMetric]
    historical_shipments: list[HistoricalShipment]
