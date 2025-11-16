from datetime import datetime
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, Integer, DateTime, ForeignKey, func
from app.models.base import Base

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    real_name: Mapped[str] = mapped_column(String(64), nullable=False)
    student_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    teacher_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_salt: Mapped[str] = mapped_column(String(64), nullable=False)
    department_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("department.id"), nullable=True)
    primary_major_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("major.id"), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    # 关系映射
    roles: Mapped[List["Role"]] = relationship(
        "Role", 
        secondary="user_role", 
        lazy="selectin"
    )
