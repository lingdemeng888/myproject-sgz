"""
论文表模型
存储论文的基础信息
"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, BigInteger, Integer, ForeignKey, DateTime, func
from app.models.base import Base


class Paper(Base):
    __tablename__ = "paper"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    topic_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("topic.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="关联选题ID"
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="学生ID"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="论文标题")
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True, comment="摘要")
    keywords: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="关键词")
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="0=编辑中,1=已提交,2=评审中,3=待修改,4=通过,5=归档"
    )
    academic_year: Mapped[str] = mapped_column(String(16), nullable=False, comment="学年: 2024-2025")
    term: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", comment="学期:1=上,2=下")
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        comment="首次提交时间"
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        comment="归档时间"
    )
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
