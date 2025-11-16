"""
角色-权限关联表模型
多对多关系：一个角色可以有多个权限，一个权限可以分配给多个角色
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Integer, ForeignKey
from app.models.base import Base


class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False
    )
    permission_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("permission.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False
    )
