from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import traceback

from app.config import settings
from app.database import Base, engine
from app import models
from app.routes import chat, interaction, hcp, product

app = FastAPI(
    title="AI-First HCP CRM API",
    description="Backend for the AI-powered Log HCP Interaction module.",
    version="1.0.0",
)

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        traceback.print_exc()
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(chat.router)
app.include_router(interaction.router)
app.include_router(hcp.router)
app.include_router(product.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "hcp-crm-backend"}