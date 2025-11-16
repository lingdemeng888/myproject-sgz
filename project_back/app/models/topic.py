"""
论文选题表模型
存储导师发布的论文选题信息
"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, BigInteger, Integer, ForeignKey, DateTime, func
from app.models.base import Base


class Topic(Base):
    __tablename__ = "topic"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="选题标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="选题详情")
    tutor_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="发布导师ID"
    )
    major_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("major.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属专业ID"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="状态: 0=草稿,1=发布,2=锁定,3=归档"
    )
    max_students: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", comment="最大选择人数")
    current_students: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0", comment="当前已选人数")
    academic_year: Mapped[str] = mapped_column(String(16), nullable=False, comment="学年: 2024-2025")
    term: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", comment="学期:1=上,2=下")
    
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="发布时间")
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="锁定时间")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="归档时间")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
