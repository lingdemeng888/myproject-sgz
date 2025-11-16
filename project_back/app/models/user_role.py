"""
用户-角色关联表模型
多对多关系：一个用户可以有多个角色，一个角色可以分配给多个用户
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Integer, ForeignKey
from app.models.base import Base


class UserRole(Base):
    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False
    )
