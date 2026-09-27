from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Feedback(Base):
    __tablename__ = 'feedback'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(Integer)
    corrected_category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    corrected_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    corrected_by: Mapped[str] = mapped_column(String(100), default='human')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
