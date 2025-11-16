from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Integer, DateTime, ForeignKey, func
from app.models.base import Base

class Major(Base):
    __tablename__ = "major"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("department.id"), nullable=False)
    major_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
