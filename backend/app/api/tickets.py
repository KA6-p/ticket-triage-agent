import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Feedback, Ticket
from ..schemas.ticket import FeedbackCreate, TicketCreate, TicketOut
from ..services.pipeline import process_ticket

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post("", response_model=TicketOut)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
):
    ticket = Ticket(**payload.model_dump())

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return process_ticket(db, ticket)


@router.get("", response_model=list[TicketOut])
def list_tickets(
    category: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Ticket).order_by(Ticket.created_at.desc())

    if category:
        query = query.where(Ticket.category == category)

    if priority:
        query = query.where(Ticket.priority == priority)

    if status:
        query = query.where(Ticket.status == status)

    return list(db.scalars(query))


@router.post("/batch")
async def batch(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = (await file.read()).decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(content))

    ids = []

    for row in reader:
        ticket = Ticket(
            source="csv",
            subject=row.get("subject", ""),
            body=row.get("body", ""),
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        process_ticket(db, ticket)

        ids.append(ticket.id)

    return {
        "count": len(ids),
        "ticket_ids": ids,
    }


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.post("/{ticket_id}/feedback")
def feedback(
    ticket_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    # Store the human feedback
    feedback_record = Feedback(
        ticket_id=ticket_id,
        **payload.model_dump(),
    )

    db.add(feedback_record)

    # Apply human corrections to the ticket
    if payload.corrected_category is not None:
        ticket.category = payload.corrected_category

    if payload.corrected_priority is not None:
        ticket.priority = payload.corrected_priority

    if payload.corrected_sentiment is not None:
        ticket.sentiment = payload.corrected_sentiment

    # A human has reviewed this ticket
    ticket.status = "reviewed"

    db.commit()
    db.refresh(feedback_record)
    db.refresh(ticket)

    return {
        "ok": True,
        "feedback_id": feedback_record.id,
        "ticket_id": ticket.id,
        "status": ticket.status,
    }
