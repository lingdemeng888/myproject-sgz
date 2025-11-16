"""
权限服务层逻辑
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission


class PermissionService:
    """权限服务类"""

    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> List[str]:
        """
        获取用户的所有权限key列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            List[str]: 权限key列表（如 ["topic:create", "topic:edit"]）
            
        逻辑：
            user -> user_role -> role -> role_permission -> permission
        """
        # 联表查询：user_role -> role_permission -> permission
        stmt = (
            select(Permission.perm_key)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
            .distinct()  # 去重（用户可能有多个角色，权限会重复）
        )
        
        result = db.execute(stmt)
        permission_keys = [row[0] for row in result.all()]
        
        return permission_keys

    @staticmethod
    def get_user_roles(db: Session, user_id: int) -> List[str]:
        """
        获取用户的所有角色key列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            List[str]: 角色key列表（如 ["ADMIN", "TUTOR"]）
        """
        stmt = (
            select(Role.role_key)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        
        result = db.execute(stmt)
        role_keys = [row[0] for row in result.all()]
        
        return role_keys

    @staticmethod
    def has_permission(db: Session, user_id: int, perm_key: str) -> bool:
        """
        检查用户是否拥有指定权限
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            perm_key: 权限key
            
        Returns:
            bool: True=有权限, False=无权限
        """
        user_permissions = PermissionService.get_user_permissions(db, user_id)
        return perm_key in user_permissions

    @staticmethod
    def has_any_permission(db: Session, user_id: int, *perm_keys: str) -> bool:
        """
        检查用户是否拥有任一权限（OR关系）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            *perm_keys: 权限key列表
            
        Returns:
            bool: True=至少有一个权限, False=都没有
        """
        user_permissions = PermissionService.get_user_permissions(db, user_id)
        return any(perm in user_permissions for perm in perm_keys)

    @staticmethod
    def has_all_permissions(db: Session, user_id: int, *perm_keys: str) -> bool:
        """
        检查用户是否拥有所有权限（AND关系）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            *perm_keys: 权限key列表
            
        Returns:
            bool: True=全部拥有, False=缺少至少一个
        """
        user_permissions = PermissionService.get_user_permissions(db, user_id)
        return all(perm in user_permissions for perm in perm_keys)
