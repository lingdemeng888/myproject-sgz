"""
用户-专业关联表模型
多对多关系：一个用户可以关联多个专业，一个专业可以有多个用户
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Integer, ForeignKey
from app.models.base import Base


class UserMajor(Base):
    __tablename__ = "user_major"

    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False
    )
    major_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("major.id", ondelete="RESTRICT", onupdate="CASCADE"),
        primary_key=True,
        nullable=False
    )
