from fastapi import FastAPI
from api.routes import router as rating_router

app = FastAPI(title="Go Rating API")

app.include_router(rating_router, prefix="/ratings", tags=["rating"])
