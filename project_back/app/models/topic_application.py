"""
选题申请表模型
存储学生申请选题的记录
"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, BigInteger, Integer, ForeignKey, DateTime, func
from app.models.base import Base


class TopicApplication(Base):
    __tablename__ = "topic_application"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    topic_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("topic.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="选题ID"
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="申请学生ID"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="状态: 0=待审批,1=通过,2=拒绝,3=取消"
    )
    application_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="申请理由")
    
    decision_by: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="审批人ID"
    )
    decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="审批时间")
    decision_comment: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审批意见")
    
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
