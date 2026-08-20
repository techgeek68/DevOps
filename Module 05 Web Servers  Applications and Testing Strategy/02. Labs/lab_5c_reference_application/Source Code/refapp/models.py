from datetime import datetime, timezone
from sqlalchemy import Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Order(Base):
    __tablename__ = "orders"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    item_count: Mapped[int]      = mapped_column(Integer, nullable=False)
    total:      Mapped[float]    = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "item_count": self.item_count,
            "total": str(self.total),
            "created_at": self.created_at.isoformat(),
        }
