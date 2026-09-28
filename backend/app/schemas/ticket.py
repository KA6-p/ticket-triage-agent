from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

Category = Literal['billing','bug','feature_request','account','other']
Priority = Literal['low','medium','high','critical']
Sentiment = Literal['frustrated','neutral','positive']

class TicketCreate(BaseModel):
    source: str = 'api'
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)

class TriageResult(BaseModel):
    category: Category
    priority: Priority
    sentiment: Sentiment
    confidence: float = Field(ge=0, le=1)
    suggested_team: str
    draft_reply: str

class TicketOut(BaseModel):
    id: int
    source: str
    subject: str
    body: str
    created_at: datetime
    category: str | None
    priority: str | None
    sentiment: str | None
    confidence: float | None
    suggested_team: str | None
    draft_reply: str | None
    status: str
    embedding_id: str | None
    duplicate_of: int | None
    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    correct: bool = False

    corrected_category: Category | None = None

    corrected_priority: Priority | None = None

    corrected_sentiment: Sentiment | None = None

    corrected_by: str = Field(
        default="human",
        min_length=1,
        max_length=100,
    )

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )
