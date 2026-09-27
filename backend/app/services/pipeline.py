from sqlalchemy.orm import Session
from ..models import Ticket
from ..config import settings
from .triage import TriageService
from .guardrails import apply_priority_override
from .embeddings import EmbeddingService
from .similarity import SimilarityService

triage_service=TriageService()
embedding_service=EmbeddingService()
similarity_service=SimilarityService()

def process_ticket(db: Session, ticket: Ticket):
    result=triage_service.classify(ticket.subject,ticket.body)
    result['priority'], _ = apply_priority_override(ticket.subject,ticket.body,result['priority'])
    emb=embedding_service.embed(f'{ticket.subject}\n{ticket.body}')
    dup=similarity_service.find(emb, settings.duplicate_threshold)
    ticket.category=result['category']; ticket.priority=result['priority']; ticket.sentiment=result['sentiment']
    ticket.confidence=result['confidence']; ticket.suggested_team=result['suggested_team']; ticket.draft_reply=result['draft_reply']
    ticket.embedding_id=str(ticket.id)
    if dup and dup['ticket_id'] != ticket.id: ticket.duplicate_of=dup['ticket_id']
    ticket.status='needs_human_review' if result['confidence'] < settings.confidence_threshold else 'triaged'
    db.add(ticket); db.commit(); db.refresh(ticket)
    similarity_service.add(ticket.id, f'{ticket.subject}\n{ticket.body}', emb)
    return ticket
