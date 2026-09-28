from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Ticket

router = APIRouter(tags=["stats"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    tickets = list(db.scalars(select(Ticket)))
    return {
        "total": len(tickets),
        "categories": dict(Counter(t.category for t in tickets if t.category)),
        "priorities": dict(Counter(t.priority for t in tickets if t.priority)),
        "statuses": dict(Counter(t.status for t in tickets)),
        "duplicates": sum(t.duplicate_of is not None for t in tickets),
    }
