"""
权限测试路由（仅用于开发测试）
"""
from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_admin,
    require_roles,
    require_permissions,
    get_current_user_permissions
)
from app.schemas.response import ApiResponse
from app.models.user import User
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/test", tags=["⚠️ 权限测试（仅开发环境）"])


@router.get("/public", response_model=ApiResponse[dict], summary="公开接口（无需认证）")
def public_endpoint():
    """公开接口，任何人都可以访问"""
    return ApiResponse.success(
        data={"message": "这是公开接口"},
        message="访问成功"
    )


@router.get("/authenticated", response_model=ApiResponse[dict], summary="需要登录")
def authenticated_endpoint(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """需要登录的接口"""
    return ApiResponse.success(
        data={
            "message": "你已登录",
            "user_id": current_user.id,
            "username": current_user.username
        },
        message="认证成功"
    )


@router.get("/admin-only", response_model=ApiResponse[dict], summary="仅管理员")
def admin_only_endpoint(
    admin: Annotated[User, Depends(require_admin)]
):
    """仅管理员可访问"""
    return ApiResponse.success(
        data={"message": "你是管理员"},
        message="权限验证通过"
    )


@router.get("/admin-or-tutor", response_model=ApiResponse[dict], summary="管理员或导师")
def admin_or_tutor_endpoint(
    current_user: Annotated[User, Depends(require_roles("ADMIN", "TUTOR"))]
):
    """管理员或导师可访问"""
    return ApiResponse.success(
        data={
            "message": "你是管理员或导师",
            "username": current_user.username
        },
        message="角色验证通过"
    )


@router.get("/student-only", response_model=ApiResponse[dict], summary="仅学生")
def student_only_endpoint(
    current_user: Annotated[User, Depends(require_roles("STUDENT"))]
):
    """仅学生可访问"""
    return ApiResponse.success(
        data={
            "message": "你是学生",
            "student_no": current_user.student_no
        },
        message="角色验证通过"
    )


@router.get("/my-permissions", response_model=ApiResponse[List[str]], summary="我的权限列表")
def get_my_permissions(
    permissions: Annotated[List[str], Depends(get_current_user_permissions)]
):
    """获取当前用户的所有权限"""
    return ApiResponse.success(
        data=permissions,
        message=f"共有 {len(permissions)} 个权限"
    )


@router.get("/my-roles", response_model=ApiResponse[dict], summary="我的角色信息")
def get_my_roles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """获取当前用户的角色和权限信息"""
    roles = PermissionService.get_user_roles(db, current_user.id)
    permissions = PermissionService.get_user_permissions(db, current_user.id)
    
    return ApiResponse.success(
        data={
            "user_id": current_user.id,
            "username": current_user.username,
            "roles": roles,
            "permissions": permissions,
            "roles_count": len(roles),
            "permissions_count": len(permissions)
        },
        message="获取成功"
    )


# 以下是权限验证示例（假设数据库中有这些权限）
@router.post("/topic-create", response_model=ApiResponse[dict], summary="创建选题（需要权限）")
def create_topic_test(
    current_user: Annotated[User, Depends(require_permissions("topic:create", "topic:manage"))]
):
    """
    测试权限：需要 topic:create 或 topic:manage 任一权限
    """
    return ApiResponse.success(
        data={"message": "权限验证通过，可以创建选题"},
        message="操作成功"
    )


@router.delete("/topic-delete", response_model=ApiResponse[dict], summary="删除选题（需要多个权限）")
def delete_topic_test(
    current_user: Annotated[User, Depends(require_permissions("topic:delete", "topic:manage", require_all=True))]
):
    """
    测试权限：需要 topic:delete AND topic:manage 两个权限都有
    """
    return ApiResponse.success(
        data={"message": "权限验证通过，可以删除选题"},
        message="操作成功"
    )
