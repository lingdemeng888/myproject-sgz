"""
管理员-用户管理API
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.user import (
    UserListQuery,
    UserListResponse,
    UserDetailResponse,
    UserUpdateStatusRequest,
    AssignRoleRequest
)
from app.services.admin_service import AdminService
from app.core.exceptions import BusinessException

router = APIRouter(prefix="/users", tags=["管理员-用户管理"])


@router.get("", response_model=ApiResponse[UserListResponse], summary="查询用户列表")
def list_users(
    page: int = 1,
    page_size: int = 20,
    role_key: str | None = None,
    department_id: int | None = None,
    status: int | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """
    管理员查询用户列表
    
    **权限要求：** ADMIN角色
    
    **查询参数：**
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    - **role_key**: 角色筛选（ADMIN/TUTOR/STUDENT）
    - **department_id**: 院系ID筛选
    - **status**: 状态筛选（1=启用，0=禁用）
    - **keyword**: 关键词搜索（用户名/姓名/学号/工号）
    
    **响应字段：**
    - 用户基本信息
    - 角色列表（role_key数组）
    - 院系和专业名称
    - 最后登录时间
    
    **排序：** 按创建时间降序
    """
    query = UserListQuery(
        page=page,
        page_size=page_size,
        role_key=role_key,
        department_id=department_id,
        status=status,
        keyword=keyword
    )
    
    result = AdminService.list_users(db=db, query=query)
    return ApiResponse.success(data=result)


@router.put("/{id}/status", response_model=ApiResponse[UserDetailResponse], summary="更新用户状态")
def update_user_status(
    id: int,
    data: UserUpdateStatusRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """
    管理员更新用户状态（启用/禁用）
    
    **权限要求：** ADMIN角色
    
    **路径参数：**
    - **id**: 用户ID
    
    **请求体：**
    - **status**: 状态（1=启用，0=禁用）
    
    **业务规则：**
    - 管理员不能禁用自己
    - 自动记录操作日志
    
    **可能的错误：**
    - 404: 用户不存在
    - 403: 不能修改自己的状态
    - 400: 用户已被删除
    """
    # 获取IP地址
    ip_address = request.client.host if request.client else None
    
    user = AdminService.update_user_status(
        db=db,
        user_id=id,
        status=data.status,
        operator_id=current_user.id,
        ip_address=ip_address
    )
    
    # 转换为详情响应
    user_detail = AdminService._to_user_detail_response(db, user)
    return ApiResponse.success(data=user_detail, message="用户状态更新成功")


@router.post("/{id}/roles", response_model=ApiResponse[UserDetailResponse], summary="分配角色")
def assign_role(
    id: int,
    data: AssignRoleRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """
    管理员给用户分配角色
    
    **权限要求：** ADMIN角色
    
    **路径参数：**
    - **id**: 用户ID
    
    **请求体：**
    - **role_id**: 角色ID
    
    **业务规则：**
    - 支持多角色（不覆盖已有角色）
    - 重复分配不报错（幂等）
    - 自动记录操作日志
    
    **可能的错误：**
    - 404: 用户不存在或角色不存在
    - 400: 用户已被删除
    """
    # 获取IP地址
    ip_address = request.client.host if request.client else None
    
    user = AdminService.assign_role(
        db=db,
        user_id=id,
        role_id=data.role_id,
        operator_id=current_user.id,
        ip_address=ip_address
    )
    
    # 转换为详情响应
    user_detail = AdminService._to_user_detail_response(db, user)
    return ApiResponse.success(data=user_detail, message="角色分配成功")
