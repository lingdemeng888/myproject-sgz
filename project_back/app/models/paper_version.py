"""
论文版本表模型
存储论文的多个修订版本
"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, BigInteger, Integer, ForeignKey, DateTime, func
from app.models.base import Base


class PaperVersion(Base):
    __tablename__ = "paper_version"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    paper_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("paper.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="论文ID"
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, comment="版本序号(1开始递增)")
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True, comment="正文内容(可选)")
    content_format: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="0=无,1=markdown,2=html,3=text"
    )
    is_final: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="是否标记为最终版本"
    )
    submitted_by: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        comment="提交人ID"
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False,
        comment="提交时间"
    )
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")
