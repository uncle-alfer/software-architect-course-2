from fastapi import FastAPI
from app.proxy_router import router
from app.settings import get_settings

app = FastAPI(title="CinemaAbyss Proxy")

@app.get("/health") 
@app.get("/healthz")
def health():
    return {"status": "ok"}

app.include_router(router)

def run():  # точка входа для Docker CMD
    import uvicorn, os
    settings = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, log_level=os.getenv("LOG_LEVEL", "info"))
