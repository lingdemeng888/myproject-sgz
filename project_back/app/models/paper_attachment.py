"""
论文附件表模型
存储论文的附件文件（如开题报告、参考文献等）
"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Integer, ForeignKey, DateTime, func
from app.models.base import Base


class PaperAttachment(Base):
    __tablename__ = "paper_attachment"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    paper_version_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("paper_version.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="论文版本ID"
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="原始文件名")
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False, comment="MIME类型")
    file_size: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=False,
        comment="文件大小字节"
    )
    storage_url: Mapped[str] = mapped_column(String(1024), nullable=False, comment="存储地址/URL")
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="文件哈希(SHA256)")
    uploaded_by: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        comment="上传人ID"
    )
    
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False,
        comment="上传时间"
    )
