"""
系部管理路由
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.schemas.response import ApiResponse, PaginatedResponse
from app.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse
)
from app.services.department_service import department_service
from app.models.user import User

router = APIRouter(prefix="/departments", tags=["系部管理"])


@router.post("", response_model=ApiResponse[DepartmentResponse], summary="创建系部")
async def create_department(
    data: DepartmentCreate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)]
):
    """创建系部（仅管理员）"""
    dept = department_service.create(db, data)
    return ApiResponse(data=DepartmentResponse.model_validate(dept))


@router.get("", response_model=ApiResponse[PaginatedResponse[DepartmentResponse]], summary="系部列表")
async def list_departments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键字"),
    status: int = Query(None, ge=0, le=1, description="状态筛选"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """系部列表（分页、搜索、筛选）"""
    result = department_service.get_list(db, page, page_size, keyword, status)
    return ApiResponse(data=PaginatedResponse(
        total=result["total"],
        page=page,
        page_size=page_size,
        items=[DepartmentResponse.model_validate(item) for item in result["items"]]
    ))


@router.get("/{dept_id}", response_model=ApiResponse[DepartmentResponse], summary="系部详情")
async def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """根据ID查询系部详情"""
    dept = department_service.get_by_id(db, dept_id)
    return ApiResponse(data=DepartmentResponse.model_validate(dept))


@router.put("/{dept_id}", response_model=ApiResponse[DepartmentResponse], summary="更新系部")
async def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """更新系部信息"""
    dept = department_service.update(db, dept_id, data)
    return ApiResponse(data=DepartmentResponse.model_validate(dept))


@router.delete("/{dept_id}", response_model=ApiResponse[None], summary="删除系部")
async def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """删除系部（检查关联专业）"""
    department_service.delete(db, dept_id)
    return ApiResponse(message="删除成功")
