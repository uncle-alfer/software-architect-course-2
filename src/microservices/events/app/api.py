import logging, asyncio
from fastapi import APIRouter, HTTPException, status
from .models import UserEvent, MovieEvent, PaymentEvent
from . import kafka_bus as kb
from .settings import get_settings

router = APIRouter()
st = get_settings()
log = logging.getLogger("events-api")

TOPIC = {
    "user": st.TOPIC_USERS,
    "movie": st.TOPIC_MOVIES,
    "payment": st.TOPIC_PAYMENTS,
}


@router.on_event("startup")
async def _startup():
    await kb.wait_kafka()


@router.on_event("shutdown")
async def _shutdown():
    await kb.stop_kafka()


async def _produce(topic: str, payload: dict):
    try:
        await kb.producer.send_and_wait(topic, payload)
    except Exception as exc:
        log.error("Kafka send failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="kafka unavailable")


@router.post("/api/events/user", status_code=201)
async def create_user(ev: UserEvent):
    await _produce(TOPIC["user"], ev.model_dump())
    return {"status": "success"}


@router.post("/api/events/movie", status_code=201)
async def create_movie(ev: MovieEvent):
    await _produce(TOPIC["movie"], ev.model_dump())
    return {"status": "success"}


@router.post("/api/events/payment", status_code=201)
async def create_payment(ev: PaymentEvent):
    await _produce(TOPIC["payment"], ev.model_dump())
    return {"status": "success"}


@router.get("/api/events/health", tags=["health"])
def health():
    return {"status": True}
