from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Events Service")
app.include_router(router)
