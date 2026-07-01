from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime
from decimal import Decimal
from datetime import datetime

from database import Base




class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    symbol: Mapped[str]
    condition: Mapped[str]
    threshold: Mapped[Decimal]
    is_active: Mapped[bool] = mapped_column(default=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),default=None)

