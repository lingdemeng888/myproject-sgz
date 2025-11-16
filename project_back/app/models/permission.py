"""
权限表模型
存储系统权限，如 topic.create、topic.read、paper.submit 等
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Integer
from app.models.base import Base


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    perm_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="权限标识: topic.read 等")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限名称")
    category: Mapped[str] = mapped_column(String(32), nullable=False, comment="分类: topic/paper/user")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="描述")
