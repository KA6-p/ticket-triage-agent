from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from .api.tickets import router as tickets_router
from .api.stats import router as stats_router

Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name, version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(tickets_router)
app.include_router(stats_router)
@app.get('/health')
def health(): return {'status':'ok','service':settings.app_name}
