from pydantic import BaseModel, Field, HttpUrl


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    region: str | None = None


class Citation(BaseModel):
    title: str
    source: str
    url: HttpUrl | None = None


class ChatResponse(BaseModel):
    summary: str
    risk_level: str
    key_drivers: list[str]
    affected_regions: list[str]
    citations: list[Citation]
