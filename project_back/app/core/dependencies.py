"""
FastAPI依赖注入:认证、权限验证
"""
from typing import Annotated, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from jose import JWTError, jwt
from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.services.permission_service import PermissionService

settings = get_settings()
security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解析JWT
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 查询用户
    stmt = select(User).where(User.username == username)
    user = db.execute(stmt).scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    if user.status == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被锁定")
    if user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被删除")
    
    return user


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """要求管理员权限"""
    # 查询用户角色
    stmt = (
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == current_user.id)
    )
    roles = db.execute(stmt).scalars().all()
    
    # 检查是否有ADMIN角色
    has_admin = any(role.role_key == "ADMIN" for role in roles)
    if not has_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    return current_user


def require_roles(*role_keys: str) -> Callable:
    """
    通用角色权限检查装饰器工厂
    
    Args:
        *role_keys: 允许的角色key列表（OR关系，满足任一即可）
        
    Returns:
        依赖函数
        
    Example:
        @router.get("/endpoint", dependencies=[Depends(require_roles("ADMIN", "TUTOR"))])
    """
    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)]
    ) -> User:
        # 查询用户角色
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == current_user.id)
        )
        roles = db.execute(stmt).scalars().all()
        user_role_keys = {role.role_key for role in roles}
        
        # 检查是否有任一允许的角色
        has_permission = any(key in user_role_keys for key in role_keys)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下任一角色: {', '.join(role_keys)}"
            )
        
        return current_user
    
    return role_checker


def require_permissions(*perm_keys: str, require_all: bool = False) -> Callable:
    """
    权限检查装饰器工厂
    
    Args:
        *perm_keys: 需要的权限key列表
        require_all: True=需要全部权限(AND), False=需要任一权限(OR)，默认False
        
    Returns:
        依赖函数
        
    Example:
        # 需要任一权限
        @router.post("/topic", dependencies=[Depends(require_permissions("topic:create", "topic:manage"))])
        
        # 需要全部权限
        @router.delete("/topic", dependencies=[Depends(require_permissions("topic:delete", "topic:manage", require_all=True))])
    """
    def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)]
    ) -> User:
        if require_all:
            # AND关系：需要全部权限
            has_permission = PermissionService.has_all_permissions(db, current_user.id, *perm_keys)
            error_msg = f"需要以下全部权限: {', '.join(perm_keys)}"
        else:
            # OR关系：需要任一权限
            has_permission = PermissionService.has_any_permission(db, current_user.id, *perm_keys)
            error_msg = f"需要以下任一权限: {', '.join(perm_keys)}"
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
        
        return current_user
    
    return permission_checker


def get_current_user_permissions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> List[str]:
    """
    获取当前用户的所有权限列表（可用于依赖注入）
    
    Returns:
        List[str]: 权限key列表
        
    Example:
        @router.get("/permissions")
        def my_permissions(permissions: Annotated[List[str], Depends(get_current_user_permissions)]):
            return {"permissions": permissions}
    """
    return PermissionService.get_user_permissions(db, current_user.id)


