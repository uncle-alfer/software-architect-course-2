from fastapi import APIRouter, BackgroundTasks
from .models import UserEvent, MovieEvent, PaymentEvent
from .kafka_bus import producer, start_consumer
from .settings import get_settings

router = APIRouter()
st = get_settings()

@router.on_event("startup")
async def _start(): await producer.start()

@router.on_event("shutdown")
async def _stop(): await producer.stop()

# --- 1. User ---
@router.post("/api/events/user", status_code=201)
async def create_user(ev: UserEvent, bg: BackgroundTasks):
    await producer.send(st.TOPIC_USERS, ev.model_dump())
    start_consumer(bg, st.TOPIC_USERS)
    return {"status": "success"}

# --- 2. Movie ---
@router.post("/api/events/movie", status_code=201)
async def create_movie(ev: MovieEvent, bg: BackgroundTasks):
    await producer.send(st.TOPIC_MOVIES, ev.model_dump())
    start_consumer(bg, st.TOPIC_MOVIES)
    return {"status": "success"}

# --- 3. Payment ---
@router.post("/api/events/payment", status_code=201)
async def create_payment(ev: PaymentEvent, bg: BackgroundTasks):
    await producer.send(st.TOPIC_PAYMENTS, ev.model_dump())
    start_consumer(bg, st.TOPIC_PAYMENTS)
    return {"status": "success"}

@router.get("/api/events/health", tags=["health"])
def health():
    """Проверка живости сервиса для постман-тестов."""
    return {"status": True}
