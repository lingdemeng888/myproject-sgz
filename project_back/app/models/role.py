"""
角色表模型
存储系统角色：ADMIN(管理员)、TUTOR(导师)、STUDENT(学生)
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Integer
from app.models.base import Base


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    role_key: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, comment="系统标识: ADMIN/TUTOR/STUDENT")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="角色名称")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="描述")
