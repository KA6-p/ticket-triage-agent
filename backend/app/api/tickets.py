import csv, io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models import Ticket, Feedback
from ..schemas.ticket import TicketCreate, TicketOut, FeedbackCreate
from ..services.pipeline import process_ticket
router=APIRouter(prefix='/tickets', tags=['tickets'])

@router.post('', response_model=TicketOut)
def create_ticket(payload: TicketCreate, db: Session=Depends(get_db)):
    t=Ticket(**payload.model_dump()); db.add(t); db.commit(); db.refresh(t); return process_ticket(db,t)

@router.get('', response_model=list[TicketOut])
def list_tickets(category:str|None=None, priority:str|None=None, status:str|None=None, db:Session=Depends(get_db)):
    q=select(Ticket).order_by(Ticket.created_at.desc())
    if category: q=q.where(Ticket.category==category)
    if priority: q=q.where(Ticket.priority==priority)
    if status: q=q.where(Ticket.status==status)
    return list(db.scalars(q))

@router.post('/batch')
async def batch(file:UploadFile=File(...), db:Session=Depends(get_db)):
    content=(await file.read()).decode('utf-8-sig'); reader=csv.DictReader(io.StringIO(content)); ids=[]
    for row in reader:
        t=Ticket(source='csv',subject=row.get('subject',''),body=row.get('body','')); db.add(t); db.commit(); db.refresh(t); process_ticket(db,t); ids.append(t.id)
    return {'count':len(ids),'ticket_ids':ids}

@router.get('/{ticket_id}', response_model=TicketOut)
def get_ticket(ticket_id:int, db:Session=Depends(get_db)):
    t=db.get(Ticket,ticket_id)
    if not t: raise HTTPException(404,'Ticket not found')
    return t

@router.post('/{ticket_id}/feedback')
def feedback(ticket_id:int, payload:FeedbackCreate, db:Session=Depends(get_db)):
    if not db.get(Ticket,ticket_id): raise HTTPException(404,'Ticket not found')
    f=Feedback(ticket_id=ticket_id,**payload.model_dump()); db.add(f); db.commit(); return {'ok':True,'feedback_id':f.id}

