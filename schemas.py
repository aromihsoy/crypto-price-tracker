from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Literal



#user
class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


#alert
class AlertCreate(BaseModel):
    symbol: str
    condition: Literal["gt", "lt"]
    threshold: Decimal


class AlertRead(BaseModel):
    id: int
    user_id: int
    symbol: str
    condition: str
    threshold: Decimal
    is_active: bool
    last_triggered_at: datetime | None

    model_config = {"from_attributes": True}

class AlertUpdate(BaseModel):
    symbol: str | None = None
    condition: Literal["gt", "lt"] | None = None
    threshold: Decimal | None = None
    is_active: bool | None = None