"""
操作日志表模型
记录系统关键操作的审计日志
"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, BigInteger, Integer, ForeignKey, DateTime, func, Index
from app.models.base import Base


class OperationLog(Base):
    __tablename__ = "operation_log"
    __table_args__ = (
        Index('idx_log_created_at', 'created_at'),
        Index('idx_log_user_id', 'user_id'),
        Index('idx_log_action', 'action'),
        Index('idx_log_resource_type', 'resource_type'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("user.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="操作用户ID"
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False, comment="操作类型: CREATE/UPDATE/DELETE")
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False, comment="资源类型: topic/paper/user")
    resource_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=True,
        comment="资源ID"
    )
    detail: Mapped[str | None] = mapped_column(Text, nullable=True, comment="操作详情JSON")
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="IP地址")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False
    )
