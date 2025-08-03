from pydantic import BaseModel, Field
from uuid import uuid4

class BaseEvent(BaseModel):
    id: str   = Field(default_factory=lambda: str(uuid4()))
    ts: int   = Field(default_factory=lambda: __import__("time").time_ns())

class UserEvent(BaseEvent):
    user_id: int
    action:  str

class MovieEvent(BaseEvent):
    movie_id: int
    action:   str

class PaymentEvent(BaseEvent):
    payment_id: int
    status:     str
