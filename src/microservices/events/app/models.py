from uuid import uuid4
from datetime import datetime
from time import time_ns
from typing import Optional

from pydantic import BaseModel, Field, Extra


class BaseEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    ts: int = Field(default_factory=time_ns)

    class Config:
        extra = Extra.ignore


class UserEvent(BaseEvent):
    user_id: int
    action: str


class MovieEvent(BaseEvent):
    movie_id: int
    action: str


class PaymentEvent(BaseEvent):
    payment_id: int
    user_id: int
    amount: float
    status: str
    method_type: Optional[str] = None
    timestamp: Optional[datetime] = None
