"""
专业管理路由
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.schemas.response import ApiResponse, PaginatedResponse
from app.schemas.major import (
    MajorCreate, MajorUpdate, MajorResponse
)
from app.services.major_service import major_service
from app.models.user import User

router = APIRouter(prefix="/majors", tags=["专业管理"])


@router.post("", response_model=ApiResponse[MajorResponse], summary="创建专业")
async def create_major(
    data: MajorCreate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)]
):
    """创建专业（仅管理员）"""
    major = major_service.create(db, data)
    return ApiResponse(data=MajorResponse.model_validate(major))


@router.get("", response_model=ApiResponse[PaginatedResponse[MajorResponse]], summary="专业列表")
async def list_majors(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    department_id: int = Query(None, gt=0, description="按系部筛选"),
    keyword: str = Query(None, description="搜索关键字"),
    status: int = Query(None, ge=0, le=1, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """专业列表（分页、搜索、筛选）"""
    result = major_service.get_list(db, page, page_size, department_id, keyword, status)
    return ApiResponse(data=PaginatedResponse(
        total=result["total"],
        page=page,
        page_size=page_size,
        items=[MajorResponse.model_validate(item) for item in result["items"]]
    ))


@router.get("/{major_id}", response_model=ApiResponse[MajorResponse], summary="专业详情")
async def get_major(
    major_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """根据ID查询专业详情"""
    major = major_service.get_by_id(db, major_id)
    return ApiResponse(data=MajorResponse.model_validate(major))


@router.put("/{major_id}", response_model=ApiResponse[MajorResponse], summary="更新专业")
async def update_major(
    major_id: int,
    data: MajorUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """更新专业信息"""
    major = major_service.update(db, major_id, data)
    return ApiResponse(data=MajorResponse.model_validate(major))


@router.delete("/{major_id}", response_model=ApiResponse[None], summary="删除专业")
async def delete_major(
    major_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """删除专业（检查关联用户/选题）"""
    major_service.delete(db, major_id)
    return ApiResponse(message="删除成功")
